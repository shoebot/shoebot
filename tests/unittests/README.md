Shoebot Unit Tests
==================

Run
---

From this directory:

```sh
$ python run_all.py
```

Or from setup.py in the root directory of Shoebot:

```sh
$ python setup.py test
```


Bot API Tests
-------------

These tests have 'botapi' in the name and test the bot API, e.g. ```test_botapi_bezier.py```.

See "Using Shoebot as a Module" in the docs for how this is implemented.


Shoebot Tests
-------------

These test the system, e.g. "can all the backends output files" ```test_file_output.py```
