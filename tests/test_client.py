import select
import unittest

from agarnet.client import Client
from agarnet.utils import find_server


class SubscriberMock(object):
    def __init__(self):
        self.events = []
        self.data = []

    def reset(self):
        self.events.clear()
        self.data.clear()

    def __getattr__(self, item):
        assert item[:3] == 'on_', 'Requested non-event handler from subscriber'
        assert 'error' not in item, 'Error event emitted'
        event = item[3:]
        data = {}
        self.events.append(event)
        self.data.append(data)
        return lambda **d: data.update(d)


class ClientTest(unittest.TestCase):
    def test_connect(self):
        nick = 'Dummy'
        address, token = find_server()
        subscriber = SubscriberMock()
        client = Client(subscriber)

        self.assertEqual('', client.player.nick)
        client.player.nick = nick

        self.assertFalse(client.connected)
        self.assertEqual('', client.address)
        self.assertEqual('', client.server_token)

        try:
            success = client.connect(address, token)
        except ConnectionResetError:
            print('Connection got closed on first attempt, retrying')
            success = client.connect(address, token)

        self.assertTrue(success)
        self.assertTrue(client.connected)
        self.assertEqual(address, client.address)
        self.assertEqual(token, client.server_token)
        self.assertEqual(nick, client.player.nick)
        self.assertEqual(1, len(subscriber.events))
        self.assertEqual('sock_open', subscriber.events[0])

        # the following tests cover expected server behavior and responses

        def poll_select(client):
            """
            Waits until the client receives a packet
            then calls its on_message() method to receive one packet.
            """
            r = False
            while not r:
                r, w, e = select.select((client.ws.sock,), (), ())
                assert not e, 'Error while receiving from socket'
            client.on_message()

        def pop_and_check_keys(event, *keys):
            received_event = subscriber.events.pop(0)
            received_data = subscriber.data.pop(0)
            self.assertEqual(event, received_event)
            if keys:
                self.assertSetEqual(set(keys), set(received_data.keys()))
            else:
                self.assertDictEqual({}, received_data)

        # receive world_rect packet
        subscriber.reset()
        poll_select(client)
        pop_and_check_keys('ingame')
        pop_and_check_keys('world_rect', 'left', 'top', 'right', 'bottom')
        if len(subscriber.events) > 2:  # optional, might be removed later
            pop_and_check_keys('server_version', 'number', 'text')

        # receive at least one leaderboard and world_update
        received = {
            'leaderboard': False, 'world_update': False,
            'cell_info': False, 'cell_eaten': False,
            'cell_removed': True,  # not required, but checked
        }
        for i in range(30):  # assuming <30tps and >1 leaderboard per second
            # receive any packet
            subscriber.reset()
            poll_select(client)
            if subscriber.events[0] == 'leaderboard_names':
                received['leaderboard'] = True
                pop_and_check_keys('leaderboard_names', 'leaderboard')
            elif subscriber.events[0] == 'world_update_pre':
                received['world_update'] = True
                self.assertEqual('world_update_post', subscriber.events[-1])
                self.assertDictEqual({}, subscriber.data[0])
                self.assertDictEqual({}, subscriber.data[-1])
                for evt, data in zip(subscriber.events, subscriber.data):
                    if evt == 'cell_info':
                        received['cell_info'] = True
                        self.assertSetEqual({'cid', 'x', 'y', 'size', 'name',
                                             'color', 'is_virus', 'is_agitated'
                                             }, set(data.keys()))
                    elif evt == 'cell_eaten':
                        received['cell_eaten'] = True
                        self.assertSetEqual({'eater_id', 'eaten_id'},
                                            set(data.keys()))
                    elif evt == 'cell_removed':
                        received['cell_removed'] = True
                        self.assertSetEqual({'cid'}, set(data.keys()))
                    elif evt not in ('world_update_pre', 'world_update_post'):
                        self.fail('Got unexpected event during world_update:'
                                  ' %s %s' % (evt, data))
            else:
                self.fail('Unexpected event %s %s'
                          % (subscriber.events, subscriber.data))
            if all(received.values()):
                break  # we received all packets we want to check
        else:
            self.fail('Did not receive all wanted packets, missing: %s'
                      % ', '.join(e for e, v in received.items() if not v))

        # TODO test spectating

        # TODO test movement

        # TODO test split/shoot

        # do not test respawn, we might not get eaten for a long time

        client.disconnect()

        self.assertFalse(client.connected)
        self.assertFalse(client.ingame)
        self.assertEqual(address, client.address)
        self.assertEqual(token, client.server_token)
        self.assertEqual(nick, client.player.nick)
        self.assertEqual('sock_closed', subscriber.events[-1])

if __name__ == '__main__':
    unittest.main()
