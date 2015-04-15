These work in shoebot, install shoebot then it's requirements.

pip install -r requirements.txt


Since these don't use pango* you can use these in pypy with the 'pgi' module
for extra performance.




*Pango doesn't work with pgi ( gi.repository implementation ) yet, as of dec 2014.



Performance

RECOMMENDED to run in Pypy !

Install Pypy
$ sudo apt-get install pypy

Create a virtualenv that uses pypy

$ virtualenv env-audiobots -p `which pypy`
$ source env-audiobots/bin/activate
$ pip install git+https://github.com/shoebot/shoebot.git@shoebot-gtk3-pgi#egg=shoebot-pgi
$ pip install -r requirements.txt

Now you can run the bots

$ cd audiobots
$ sbot -w
