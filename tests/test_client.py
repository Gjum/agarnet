from unittest import TestCase

from agarnet.client import Client
from agarnet.utils import find_server


class SubscriberMock(object):
    def __init__(self):
        self.events = []
        self.data = []

    def __getattr__(self, item):
        assert item[:3] == 'on_', \
            'Requested non-event handler from subscriber'
        assert item not in (
            'on_connect_error',
            'on_sock_error',
        ), 'Error event emitted'
        event = item[3:]
        data = {}
        self.events.append(event)
        self.data.append(data)
        return lambda **d: data.update(d)


class ClientTest(TestCase):
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
            # sometimes connection gets closed on first attempt
            success = client.connect(address, token)

        self.assertTrue(success)
        self.assertTrue(client.connected)
        self.assertEqual(address, client.address)
        self.assertEqual(token, client.server_token)
        self.assertEqual(nick, client.player.nick)
        self.assertEqual('sock_open', subscriber.events[-1])

        client.disconnect()

        self.assertFalse(client.connected)
        self.assertFalse(client.ingame)
        self.assertEqual(address, client.address)
        self.assertEqual(token, client.server_token)
        self.assertEqual(nick, client.player.nick)
        self.assertEqual('sock_closed', subscriber.events[-1])
