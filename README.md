agarnet
=======
[![Join the chat at https://gitter.im/Gjum/gagar](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Gjum/gagar?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Latest PyPI version](https://img.shields.io/pypi/v/agarnet.svg?style=flat)](https://pypi.python.org/pypi/agarnet/)
[![Number of PyPI downloads](https://img.shields.io/pypi/dm/agarnet.svg?style=flat)](https://pypi.python.org/pypi/agarnet/)
[![Build Status](https://travis-ci.org/Gjum/agarnet.svg)](https://travis-ci.org/Gjum/agarnet)
[![Coverage Status](https://coveralls.io/repos/Gjum/agarnet/badge.svg?branch=master&service=github)](https://coveralls.io/github/Gjum/agarnet?branch=master)

[agar.io](http://agar.io/) client and connection toolkit

Installation
------------
The client can be installed directly from [PyPI](https://pypi.python.org/pypi?name=agarnet&:action=display) with

    pip install agarnet

or, if you want to get/edit the source code,

    git clone git@github.com:Gjum/agarnet.git
    cd agarnet/
    python3 setup.py install

Documentation
-------------
See [doc/](https://github.com/Gjum/agarnet/blob/master/doc/):
- [events](https://github.com/Gjum/agarnet/blob/master/doc/client.md#events)
- [client](https://github.com/Gjum/agarnet/blob/master/doc/client.md#client)
- [cell, world, player](https://github.com/Gjum/agarnet/blob/master/doc/world.md#agarnetworld)
- [utils](https://github.com/Gjum/agarnet/blob/master/doc/utils.md#agarnetutils)

About
-----
This is a hobby project of me, on which I work in my free time.

Pull requests are more than welcome, but you should open an issue first, so we can talk about it.

I reverse-engineered the protocol implementation by looking at the (barely) obfuscated Javascript code on the agar.io website.
Although it would be much easier now to write a client, because [there is a wiki](http://agar.gcommer.com/) describing the whole protocol and most game mechanics.

If you have any game-related questions, feel free to ask in the [#agariomods IRC channel on the Rizon network](http://irc.lc/rizon/agariomods/CodeBlob@@@).
For questions about this client specifically, [open an issue](https://github.com/Gjum/agarnet/issues/new) or write me an email: [code.gjum+agarnet@gmail.com](mailto:code.gjum+agarnet@gmail.com)

Disclaimer
----------
This project isn't affiliated with [agar.io](http://agar.io/) in any way. When playing with this client, you do not get advertisements, which may be nice for you, but does not pay for the servers needed to run the game.

---

Licensed under GPLv3.
