# agarnet.client

- [Events](#events)
  - [Connection](#connection)
    - [on_sock_open()](#on_sock_open)
    - [on_sock_closed()](#on_sock_closed)
    - [on_sock_error()](#on_sock_error)
    - [on_connect_error(msg)](#on_connect_errormsg)
    - [on_message_error(msg)](#on_message_errormsg)
  - [World updates](#world-updates)
    - [on_world_update_pre()](#on_world_update_pre)
    - [on_cell_eaten(eater_id, eaten_id)](#on_cell_eateneater_id-eaten_id)
    - [on_cell_info(cid, x, y, size, name, color, is_virus, is_agitated)](#on_cell_infocid-x-y-size-name-color-is_virus-is_agitated)
    - [on_cell_removed(cid)](#on_cell_removedcid)
    - [on_world_update_post()](#on_world_update_post)
  - [Other ingame events](#other-ingame-events)
    - [on_world_rect(left, top, right, bottom)](#on_world_rectleft-top-right-bottom)
    - [on_server_version(number, text)](#on_server_versionnumber-text)
    - [on_leaderboard_groups(angles)](#on_leaderboard_groupsangles)
    - [on_leaderboard_names(leaderboard)](#on_leaderboard_namesleaderboard)
    - [on_ingame()](#on_ingame)
    - [on_spectate_update(pos, scale)](#on_spectate_updatepos-scale)
    - [on_respawn()](#on_respawn)
    - [on_own_id(cid)](#on_own_idcid)
    - [on_death()](#on_death)
    - [on_experience_info(level, current_xp, next_xp)](#on_experience_infolevel-current_xp-next_xp)
  - [Unknown](#unknown)
    - [on_clear_cells()](#on_clear_cells)
    - [on_debug_line(x, y)](#on_debug_linex-y)
- [Client](#client)
  - [Client.\_\_init\_\_(subscriber)](#client__init__subscriber)
  - [Attributes](#attributes)
    - [Client.address](#clientaddress)
    - [Client.connected](#clientconnected)
    - [Client.facebook_token](#clientfacebook_token)
    - [Client.ingame](#clientingame)
    - [Client.player](#clientplayer)
    - [Client.server_token](#clientserver_token)
    - [Client.subscriber](#clientsubscriber)
    - [Client.world](#clientworld)
    - [Client.ws](#clientws)
  - [Connection](#connection-1)
    - [Client.connect(address, token=None)](#clientconnectaddress-tokennone)
    - [Client.disconnect()](#clientdisconnect)
    - [Client.listen()](#clientlisten)
    - [Client.on_message()](#clienton_message)
  - [Sending packets to the server](#sending-packets-to-the-server)
    - [Client.send_handshake()](#clientsend_handshake)
    - [Client.send_token(token)](#clientsend_tokentoken)
    - [Client.send_facebook(token)](#clientsend_facebooktoken)
    - [Client.send_spectate()](#clientsend_spectate)
    - [Client.send_spectate_toggle()](#clientsend_spectate_toggle)
    - [Client.send_respawn()](#clientsend_respawn)
    - [Client.send_target(x, y, cid=0)](#clientsend_targetx-y-cid0)
    - [Client.send_shoot()](#clientsend_shoot)
    - [Client.send_split()](#clientsend_split)
    - [Client.send_explode()](#clientsend_explode)
- [Internal details](#internal-details)

## Events
When emitting an event, the [`subscriber`](#clientsubscriber)'s corresponding `on_*()` method gets called.

The easiest way to use this is to create a class like this:
```python
class SimpleSubscriber(object):
    def __getattr__(self, handler_name):
        return lambda *args, **kwargs: None  # default handler does nothing
```

or, a more safe way:
```python
class Subscriber(object):
    """Base class for event handlers via on_*() methods."""

    def __getattr__(self, func_name):
        # still throw error when not getting an `on_*()` attribute
        if 'on_' != func_name[:3]:
            raise AttributeError("'%s' object has no attribute '%s'"
                                 % (self.__class__.__name__, func_name))
        return lambda *args, **kwargs: None  # default handler does nothing
```

You can then add more methods to handle specific events:
```python
class AutoRespawnSubscriber(Subscriber):
    def __init__(self, client):
        self.client = client

    def on_ingame(self):
        self.client.send_respawn()

    def on_death(self):
        self.client.send_respawn()
```

To connect multiple subscribers to one client, you can use something like this:
```python
class MultiSubscriber(Subscriber):
    """Distributes method calls to multiple subscribers."""

    def __init__(self, *subs):
        self.subs = list(subs)

    def sub(self, subscriber):
        self.subs.append(subscriber)
        return subscriber

    def __getattr__(self, func_name):
        super(MultiSubscriber, self).__getattr__(func_name)

        def wrapper(*args, **kwargs):
            for sub in self.subs:
                handler = getattr(sub, func_name, None)
                if handler:
                    handler(*args, **kwargs)

        return wrapper


sub = MultiSubscriber()
client = Client(sub)

auto_respawn_subscriber = AutoRespawnSubscriber(client)
some_other_subscriber = SomeOtherSubscriber()

sub.sub(auto_respawn_subscriber, some_other_subscriber)
```

### Connection

#### on_sock_open()
The websocket is now open, you can start sending data.

This gets emitted in `connect()`, so you can call `disconnect()` here to cancel the handshake.

#### on_sock_closed()
The websocket is now closed, you cannot send data anymore.

#### on_sock_error()
The websocket is in an exceptional state.

#### on_connect_error(msg)
The connection in `connect()` failed or the client already was connected to a server.

#### on_message_error(msg)
The message that was received in `on_message()` could not be parsed.

### World updates
These get emitted in this order when receiving a `world_update` packet.

#### on_world_update_pre()
Emitted before the client makes any changes to the `world` instance.

Use this if you want to back up the world state to compare it in `on_world_update_post`.

#### on_cell_eaten(eater_id, eaten_id)
`eater_id` ate `eaten_id`.

After emitting this event, the client removes the eaten cell from the world.

#### on_cell_info(cid, x, y, size, name, color, is_virus, is_agitated)
Emitted for every cell that got visible, moved, or changed in size.

After emitting this event, the client calls the cell's `update` method with the new data.

#### on_cell_removed(cid)
The cell will not be updated any longer by the server.

This happens when the cell moves out of the visible area or gets eaten.

#### on_world_update_post()
All world updates have been applied.

Use this to calculate statistics.

### Other ingame events
Roughly in order of appearance during a session.

#### on_world_rect(left, top, right, bottom)
The borders of the rectangular world.

Usually the first packet sent by the server.

#### on_server_version(number, text)
Sent in the `world_rect` packet. Example:

    number = 0
    text = "Sep 14 2015 22:58:35"

#### on_leaderboard_groups(angles)
Sent every 500ms.

- `angles` List of angles (`float`) for the pie chart in `teams` mode.

#### on_leaderboard_names(leaderboard)
Sent every 500ms.

- `leaderboard` List of `(cid, name)` pairs, from top to bottom (1st to 10th).

The `cid`s seem to always be the lowest ID of that player.

The name can be an empty string. The official client then displays "An unnamed cell" instead.

#### on_ingame()
The client started receiving ingame packets.

#### on_spectate_update(pos, scale)
The center and size of the spectated area were updated.

#### on_respawn()
The player respawned and can now move.

This is emitted before the corresponding [`on_own_id`](#on_own_id) event.

#### on_own_id(cid)
By respawning or splitting, the player got another cell to control.

#### on_death()
The player died and can now respawn.

#### on_experience_info(level, current_xp, next_xp)
After dying, the server sent the new experience bar data.

### Unknown
These have not been observed by the package developer, but are specified in the official client.

#### on_clear_cells()
The server told the client to clear its cells.

#### on_debug_line(x, y)
The server told the client to draw a line from all cells to this position.


## Client


### Client.\_\_init\_\_(subscriber)
- `subscriber` class instance that implements any `on_*()` event methods


### Attributes

#### Client.address
The most recent address used to connect to the server.

#### Client.connected
`self.ws.connected`

#### Client.facebook_token
The most recent Facebook token sent to a server.

#### Client.ingame
`False` after connection, `True` upon receiving a packet listed in `ingame_packets`.

#### Client.player
Gets updated with the new data when the server sends a packet.

#### Client.server_token
The most recent token used to connect to the server.

#### Client.subscriber
Class whose `on_*()` methods get called when an [event](#events) occurs.

#### Client.world
`self.player.world`

Gets updated with data from the server.

#### Client.ws
The websocket instance used to connect to the server.


### Connection

#### Client.connect(address, token=None)
Connect the underlying websocket to the address,
 send a `handshake` and optionally a `token` packet.

Returns `True` if connected, `False` if the connection failed.

Parameters:

- `address` string, `'IP:PORT'`
- `token` optional, unique token, required by official servers, acquired through [`utils.find_server()`](utils.md#find_serverregioneu-london-modenone)

#### Client.disconnect()
Disconnect from server.

Closes the websocket, sets `ingame = False`, and emits an [`on_sock_closed`](#on_sock_closed) event.

#### Client.listen()
Set up a quick connection. Returns on disconnect.

After calling `connect()`, this waits for messages from the server using `select`,
and notifies the [`subscriber`](#clientsubscriber) of any [events](#events).

#### Client.on_message()
Poll the websocket for a new packet.

Called by `listen()`.


### Sending packets to the server

#### Client.send_handshake()
Used by [`connect()`](#clientconnectaddress-tokennone).

Tells the server which protocol to use.

Has to be sent before any other packets, or the server will disconnect the client.

#### Client.send_token(token)
Used by [`connect()`](#clientconnectaddress-tokennone).

After connecting to an official server and sending the handshake packets,
the client has to send the token acquired through [`find_server()`](utils.md#find_serverregioneu-london-modenone),
otherwise the server will drop the connection upon receiving any other packet.

#### Client.send_facebook(token)
Tells the server which Facebook account this client uses.

After sending, the server takes some time to get the data from Facebook.

Seems to be broken in recent versions of the game.

#### Client.send_spectate()
Puts the player into spectate mode.

The server then starts sending `spectate_update` packets containing the center and size of the spectated area.

#### Client.send_spectate_toggle()
Toggles the spectate mode between following the largest player and moving around freely.

#### Client.send_respawn()
Respawns the player.

#### Client.send_target(x, y, cid=0)
Sets the target position of all cells.

`x` and `y` are world coordinates. They can exceed the world border.

For continuous movement, send a new target position before the old one is reached.

In earlier versions of the game, it was possible to control each cell individually by specifying the cell's `cid`.

Same as moving your mouse in the original client.

#### Client.send_shoot()
Ejects a pellet from all controlled cells.

Same as pressing `W` in the original client.

#### Client.send_split()
Splits all controlled cells, while not exceeding 16 cells.

Same as pressing `Space` in the original client.

#### Client.send_explode()
In earlier versions of the game, sending this caused your cells to split into lots of small cells and die.


## Internal details

#### handshake_version
Tells the server which protocol to use.

Used in `send_handshake`.

#### ingame_packets
When receiving one of these packets, the client emits an [`on_ingame`](#on_ingame) event.

#### packet_c2s
`dict` to convert packet IDs to strings for method calling.

Currently not used

#### packet_s2c
`dict` to convert packet IDs to strings for method calling.

#### Client.parse_world_update()
#### Client.parse_leaderboard_names()
#### Client.parse_leaderboard_groups()
#### Client.parse_own_id()
#### Client.parse_world_rect()
#### Client.parse_spectate_update()
#### Client.parse_experience_info()
#### Client.parse_clear_cells()
#### Client.parse_debug_line()

#### Client.send_struct(fmt, *data)
Called by all other `send_` methods to send a single packet to the server.

`fmt` is the same as for Python structs.
