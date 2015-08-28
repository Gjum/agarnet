# agarnet.utils

#### special_names
List of names that have a skin on the official client.

#### find_server(region='EU-London', mode=None)
Returns `(address, token)`, both strings.

`mode` is the game mode of the requested server.
It can be `'party'`, `'teams'`, `'experimental'`, or `None` for "Free for all". 

*TODO document the region argument*

The returned `address` is in `'IP:port'` format.

Makes a request to http://m.agar.io to get address and token.

#### get_party_address(party_token)
Returns the address (`'IP:port'` string) of the party server.

To generate a `party_token`:
```python
from agarnet.utils import find_server
_, token = find_server(mode='party')
```

Makes a request to http://m.agar.io/getToken to get the address.

#### moz_headers
Used to make the requests to `m.agar.io`.

Sets the `User-Agent` to Firefox and the `Origin` and `Referer` to `http://agar.io`.
