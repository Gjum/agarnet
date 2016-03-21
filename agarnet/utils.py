import urllib.error
import urllib.request

from .client import handshake_version

# List of names that always have a skin on the official client.
special_names = 'poland;usa;china;russia;canada;australia;spain;brazil;germany;ukraine;france;sweden;chaplin;north korea;south korea;japan;united kingdom;earth;greece;latvia;lithuania;estonia;finland;norway;cia;maldivas;austria;nigeria;reddit;yaranaika;confederate;9gag;indiana;4chan;italy;bulgaria;tumblr;2ch.hk;hong kong;portugal;jamaica;german empire;mexico;sanik;switzerland;croatia;chile;indonesia;bangladesh;thailand;iran;iraq;peru;moon;botswana;bosnia;netherlands;european union;taiwan;pakistan;hungary;satanist;qing dynasty;matriarchy;patriarchy;feminism;ireland;texas;facepunch;prodota;cambodia;steam;piccolo;ea;india;kc;denmark;quebec;ayy lmao;sealand;bait;tsarist russia;origin;vinesauce;stalin;belgium;luxembourg;stussy;prussia;8ch;argentina;scotland;sir;romania;belarus;wojak;doge;nasa;byzantium;imperial japan;french kingdom;somalia;turkey;mars;pokerface;8;irs;receita federal;facebook;putin;merkel;tsipras;obama;kim jong-un;dilma;hollande;berlusconi;cameron;clinton;hillary;venezuela;blatter;chavez;cuba;fidel;palin;queen;boris;bush;trump;underwood' \
    .split(';')

# Used to make the requests to `m.agar.io`. Sets the
# `User-Agent` to Firefox and the `Origin` and `Referer` to `http://agar.io`.
default_headers = [
    ('User-Agent',
        'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'),
    ('Origin', 'http://agar.io'),
    ('Referer', 'http://agar.io'),
]


def find_server(region='EU-London', mode=None):
    """
    Returns `(address, token)`, both strings.

    `mode` is the game mode of the requested server. It can be
    `'party'`, `'teams'`, `'experimental'`, or `None` for "Free for all".

    The returned `address` is in `'IP:port'` format.

    Makes a request to http://m.agar.io to get address and token.
    """
    if mode:
        region = '%s:%s' % (region, mode)
    opener = urllib.request.build_opener()
    opener.addheaders = default_headers
    data = '%s\n%s' % (region, handshake_version)
    return opener.open('http://m.agar.io/', data=data.encode()) \
        .read().decode().split('\n')[0:2]


def get_party_address(party_token):
    """
    Returns the address (`'IP:port'` string) of the party server.

    To generate a `party_token`:
    ```
    from agarnet.utils import find_server
    _, token = find_server(mode='party')
    ```

    Makes a request to http://m.agar.io/getToken to get the address.
    """
    opener = urllib.request.build_opener()
    opener.addheaders = default_headers
    try:
        data = party_token.encode()
        return opener.open('http://m.agar.io/getToken', data=data) \
            .read().decode().split('\n')[0]
    except urllib.error.HTTPError:
        raise ValueError('Invalid token "%s" (maybe timed out,'
                         ' try creating a new one)' % party_token)
