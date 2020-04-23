Shoebot Unit Tests
==================

Run
---

From this directory:

```sh
$ python3 -munittest
```

Or from setup.py in the root directory of Shoebot:

```sh
$ python3 setup.py test
```


Writing tests
-------------

Tests try and follow the AAA pattern where possible.


Helper functions
----------------

ShoebotTestCase:

Extends unittest.TestCase, and provides the ability to run a bot using a known random seed, 
making it possible to get the same output on subsequent runs.

Assertions are provided to make it straightforward to check if output is as expected.
x
