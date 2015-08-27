from unittest import TestCase

from agarnet.utils import find_server, get_party_address


class UtilsTest(TestCase):
    def test_find_server(self):
        address_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}'

        for i in range(3):  # TODO make sure to not get above a rate limit
            address, token = find_server(region='EU-London', mode='teams')
            self.assertNotEqual('0.0.0.0:0', address)
            self.assertRegex(address, address_regex)
            self.assertGreater(len(token), 0, 'no token received')

    def test_get_party_address(self):
        address, token = find_server(mode='party')
        party_address = get_party_address(token)
        self.assertEqual(address, party_address, 'party mode broke')
