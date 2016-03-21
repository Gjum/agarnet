import struct

import websocket

from .buffer import BufferStruct, BufferUnderflowError
from .vec import Vec
from .world import Player

packet_s2c = {
    16: 'world_update',
    17: 'spectate_update',
    18: 'clear_cells',  # TODO which cells?
    20: 'clear_cells',
    21: 'debug_line',
    32: 'own_id',
    49: 'leaderboard_names',
    50: 'leaderboard_groups',
    64: 'world_rect',
    81: 'experience_info',
}

packet_c2s = {
    0: 'respawn',
    1: 'spectate',
    16: 'target',
    17: 'split',
    18: 'spectate_toggle',
    20: 'explode',
    21: 'shoot',
    80: 'token',
    81: 'facebook',
    254: 'handshake1',
    255: 'handshake2',
}

ingame_packets = ('world_rect', 'world_update', 'leaderboard_names',
                  'leaderboard_groups', 'spectate_update', 'own_id')


handshake_version = 154669603


class Client(object):
    """Talks to a server and calls handlers on events."""

    def __init__(self, subscriber):
        """
        :param subscriber: class instance that implements any on_*() methods
        """
        self.subscriber = subscriber

        # Gets updated with the new data when the server sends a packet.
        self.player = Player()

        # The websocket instance used to connect to the server.
        self.ws = websocket.WebSocket()

        # The most recent address used to connect to the server.
        self.address = ''

        # The most recent token used to connect to the server.
        self.server_token = ''

        # The most recent Facebook token sent to a server.
        self.facebook_token = ''

        # `False` after connection, gets set to `True` when
        # receiving a packet listed in `ingame_packets`.
        self.ingame = False

    @property
    def world(self):
        return self.player.world

    @world.setter
    def world(self, world):
        self.player.world = world

    @property
    def connected(self):
        return self.ws.connected

    def connect(self, address, token=None):
        """
        Connect the underlying websocket to the address,
        send a handshake and optionally a token packet.

        Returns `True` if connected, `False` if the connection failed.

        :param address: string, `IP:PORT`
        :param token: unique token, required by official servers,
                      acquired through utils.find_server()
        :return: True if connected, False if not
        """
        if self.connected:
            self.subscriber.on_connect_error(
                'Already connected to "%s"' % self.address)
            return False

        self.address = address
        self.server_token = token
        self.ingame = False

        self.ws.settimeout(1)
        self.ws.connect('ws://%s' % self.address, origin='http://agar.io')
        if not self.connected:
            self.subscriber.on_connect_error(
                'Failed to connect to "%s"' % self.address)
            return False

        self.subscriber.on_sock_open()
        # allow handshake canceling
        if not self.connected:
            self.subscriber.on_connect_error(
                'Disconnected before sending handshake')
            return False

        self.send_handshake()
        if self.server_token:
            self.send_token(self.server_token)

        old_nick = self.player.nick
        self.player.reset()
        self.world.reset()
        self.player.nick = old_nick
        return True

    def disconnect(self):
        """
        Disconnect from server.

        Closes the websocket, sets `ingame = False`, and emits on_sock_closed.
        """
        self.ws.close()
        self.ingame = False
        self.subscriber.on_sock_closed()
        # keep player/world data

    def listen(self):
        """
        Set up a quick connection. Returns on disconnect.

        After calling `connect()`, this waits for messages from the server
        using `select`, and notifies the subscriber of any events.
        """
        import select
        while self.connected:
            r, w, e = select.select((self.ws.sock, ), (), ())
            if r:
                self.on_message()
            elif e:
                self.subscriber.on_sock_error(e)
        self.disconnect()

    def on_message(self, msg=None):
        """
        Poll the websocket for a new packet.

        `Client.listen()` calls this.

        :param msg (string(byte array)): Optional. Parse the specified message
            instead of receiving a packet from the socket.
        """
        if msg is None:
            try:
                msg = self.ws.recv()
            except Exception as e:
                self.subscriber.on_message_error(
                    'Error while receiving packet: %s' % str(e))
                self.disconnect()
                return False

        if not msg:
            self.subscriber.on_message_error('Empty message received')
            return False

        buf = BufferStruct(msg)
        opcode = buf.pop_uint8()
        try:
            packet_name = packet_s2c[opcode]
        except KeyError:
            self.subscriber.on_message_error('Unknown packet %s' % opcode)
            return False

        if not self.ingame and packet_name in ingame_packets:
            self.subscriber.on_ingame()
            self.ingame = True

        parser = getattr(self, 'parse_%s' % packet_name)
        try:
            parser(buf)
        except BufferUnderflowError as e:
            msg = 'Parsing %s packet failed: %s' % (packet_name, e.args[0])
            self.subscriber.on_message_error(msg)

        if len(buf.buffer) != 0:
            msg = 'Buffer not empty after parsing "%s" packet' % packet_name
            self.subscriber.on_message_error(msg)

        return packet_name

    def parse_world_update(self, buf):
        self.subscriber.on_world_update_pre()

        self.parse_cell_eating(buf)
        self.parse_cell_updates(buf)
        self.parse_cell_deletions(buf)

        if self.player.is_alive:
            self.player.cells_changed()

        self.subscriber.on_world_update_post()

    def parse_cell_eating(self, buf):
        for i in range(buf.pop_uint16()):
            # ca eats cb
            ca = buf.pop_uint32()
            cb = buf.pop_uint32()
            self.subscriber.on_cell_eaten(eater_id=ca, eaten_id=cb)
            if cb in self.player.own_ids:  # we got eaten
                if len(self.player.own_ids) <= 1:
                    self.subscriber.on_death()
                    # do not clear all cells yet, they still get updated
                self.player.own_ids.remove(cb)
            if cb in self.player.world.cells:
                self.subscriber.on_cell_removed(cid=cb)
                del self.player.world.cells[cb]

    def parse_cell_updates(self, buf):
        # create/update cells
        while 1:
            cid = buf.pop_uint32()
            if cid == 0:
                break
            cx = buf.pop_int32()
            cy = buf.pop_int32()
            csize = buf.pop_int16()
            color = (buf.pop_uint8(), buf.pop_uint8(), buf.pop_uint8())

            bitmask = buf.pop_uint8()
            is_virus = bool(bitmask & 1)
            is_agitated = bool(bitmask & 16)
            if bitmask & 2:  # skip padding
                for i in range(buf.pop_uint32()):
                    buf.pop_uint8()
            if bitmask & 4:  # skin URL
                skin_url = buf.pop_str8()
            else:  # no skin URL given
                skin_url = ''

            cname = buf.pop_str16()
            self.subscriber.on_cell_info(
                cid=cid, x=cx, y=cy, size=csize, name=cname, color=color,
                is_virus=is_virus, is_agitated=is_agitated)
            if cid not in self.player.world.cells:
                self.world.create_cell(cid)
            self.player.world.cells[cid].update(
                cid=cid, x=cx, y=cy, size=csize, name=cname, color=color,
                is_virus=is_virus, is_agitated=is_agitated)

            if skin_url:  # TODO Cell.update() and on_cell_info got too bulky
                self.subscriber.on_cell_skin(skin_url=skin_url)

    def parse_cell_deletions(self, buf):
        cells = self.player.world.cells
        # also keep these non-updated cells
        for i in range(buf.pop_uint32()):
            cid = buf.pop_uint32()
            if cid in cells:
                self.subscriber.on_cell_removed(cid=cid)
                del cells[cid]
                if cid in self.player.own_ids:  # own cells joined
                    self.player.own_ids.remove(cid)

    def parse_leaderboard_names(self, buf):
        # sent every 500ms
        # not in "teams" mode
        n = buf.pop_uint32()
        leaderboard_names = []
        for i in range(n):
            l_id = buf.pop_uint32()
            l_name = buf.pop_str16()
            leaderboard_names.append((l_id, l_name))
        self.subscriber.on_leaderboard_names(leaderboard=leaderboard_names)
        self.player.world.leaderboard_names = leaderboard_names

    def parse_leaderboard_groups(self, buf):
        # sent every 500ms
        # only in "teams" mode
        n = buf.pop_uint32()
        leaderboard_groups = []
        for i in range(n):
            angle = buf.pop_float32()
            leaderboard_groups.append(angle)
        self.subscriber.on_leaderboard_groups(angles=leaderboard_groups)
        self.player.world.leaderboard_groups = leaderboard_groups

    def parse_own_id(self, buf):  # new cell ID, respawned or split
        cid = buf.pop_uint32()
        if not self.player.is_alive:  # respawned
            self.player.own_ids.clear()
            self.subscriber.on_respawn()
        # server sends empty name, assumes we set it here
        if cid not in self.world.cells:
            self.world.create_cell(cid)
        # self.world.cells[cid].name = self.player.nick
        self.player.own_ids.add(cid)
        self.player.cells_changed()
        self.subscriber.on_own_id(cid=cid)

    def parse_world_rect(self, buf):  # world size
        left = buf.pop_float64()
        top = buf.pop_float64()
        right = buf.pop_float64()
        bottom = buf.pop_float64()
        self.subscriber.on_world_rect(
            left=left, top=top, right=right, bottom=bottom)
        self.world.top_left = Vec(top, left)
        self.world.bottom_right = Vec(bottom, right)

        if buf.buffer:
            number = buf.pop_uint32()
            text = buf.pop_str16()
            self.subscriber.on_server_version(number=number, text=text)

    def parse_spectate_update(self, buf):
        # only in spectate mode
        x = buf.pop_float32()
        y = buf.pop_float32()
        scale = buf.pop_float32()
        self.player.center.set(x, y)
        self.player.scale = scale
        self.subscriber.on_spectate_update(
            pos=self.player.center, scale=scale)

    def parse_experience_info(self, buf):
        level = buf.pop_uint32()
        current_xp = buf.pop_uint32()
        next_xp = buf.pop_uint32()
        self.subscriber.on_experience_info(
            level=level, current_xp=current_xp, next_xp=next_xp)

    def parse_clear_cells(self, buf):
        # TODO clear cells packet is untested
        self.subscriber.on_clear_cells()
        self.world.cells.clear()
        self.player.own_ids.clear()
        self.player.cells_changed()

    def parse_debug_line(self, buf):
        # TODO debug line packet is untested
        x = buf.pop_int16()
        y = buf.pop_int16()
        self.subscriber.on_debug_line(x=x, y=y)

    # format reminder
    # b int8
    # h int16
    # i int32
    # f float32
    # d float64

    def send_struct(self, fmt, *data):
        """
        If connected, formats the data to a struct and sends it to the server.
        Used internally by all other `send_*()` methods.
        """
        if self.connected:
            self.ws.send(struct.pack(fmt, *data))

    def send_handshake(self):
        """
        Used by `Client.connect()`.

        Tells the server which protocol to use.
        Has to be sent before any other packets,
        or the server will drop the connection when receiving any other packet.
        """
        self.send_struct('<BI', 254, 5)
        self.send_struct('<BI', 255, handshake_version)

    def send_token(self, token):
        """
        Used by `Client.connect()`.

        After connecting to an official server and sending the
        handshake packets, the client has to send the token
        acquired through `utils.find_server()`, otherwise the server will
        drop the connection when receiving any other packet.
        """
        self.send_struct('<B%iB' % len(token), 80, *map(ord, token))
        self.server_token = token

    def send_facebook(self, token):
        """
        Tells the server which Facebook account this client uses.

        After sending, the server takes some time to
        get the data from Facebook.

        Seems to be broken in recent versions of the game.
        """
        self.send_struct('<B%iB' % len(token), 81, *map(ord, token))
        self.facebook_token = token

    def send_respawn(self):
        """
        Respawns the player.
        """
        nick = self.player.nick
        self.send_struct('<B%iH' % len(nick), 0, *map(ord, nick))

    def send_target(self, x, y, cid=0):
        """
        Sets the target position of all cells.

        `x` and `y` are world coordinates. They can exceed the world border.

        For continuous movement, send a new target position
        before the old one is reached.

        In earlier versions of the game, it was possible to
        control each cell individually by specifying the cell's `cid`.

        Same as moving your mouse in the original client.
        """
        self.send_struct('<BiiI', 16, int(x), int(y), cid)

    def send_spectate(self):
        """
        Puts the player into spectate mode.

        The server then starts sending `spectate_update` packets
        containing the center and size of the spectated area.
        """
        self.send_struct('<B', 1)

    def send_spectate_toggle(self):
        """
        Toggles the spectate mode between following the largest player
        and moving around freely.
        """
        self.send_struct('<B', 18)

    def send_split(self):
        """
        Splits all controlled cells, while not exceeding 16 cells.

        Same as pressing `Space` in the original client.
        """
        self.send_struct('<B', 17)

    def send_shoot(self):
        """
        Ejects a pellet from all controlled cells.

        Same as pressing `W` in the original client.
        """
        self.send_struct('<B', 21)

    def send_explode(self):
        """
        In earlier versions of the game, sending this caused your cells
        to split into lots of small cells and die.
        """
        self.send_struct('<B', 20)
        self.player.own_ids.clear()
        self.player.cells_changed()
        self.ingame = False
        self.subscriber.on_death()
