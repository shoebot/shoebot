============
Contributing
============

Development tasks
=================

Make new examples or port existing ones
---------------------------------------

We're always eager to welcome new examples that explain a concept or show off an interesting technique.

If you need inspiration, there are many examples in the `nodebox-pyobjc <https://github.com/karstenw/nodebox-pyobjc/tree/master/examples>`_ port that aren't yet ported to Shoebot. They should work mostly without modifications -- we need help testing them. 

Try them out and post any issues you find on our `issue tracker <https://github.com/shoebot/shoebot/issues/>`_.

Be sure to also check the brief guidelines in :ref:`example-style` so that your efforts can be included in Shoebot.


Help port libraries
-------------------

We're missing these Nodebox libraries; can you help us port them to Shoebot?

Incidentally, we're also missing documentation to explain how to port Nodebox libraries. If you're interested but stuck, file an issue and we'll help you.

- Knowledge

  * `WordNet <https://www.nodebox.net/code/index.php/WordNet>`_ -- the bundled wordnet should be downloadable separately
  * `Keywords <https://www.nodebox.net/code/index.php/Keywords>`_
  * `Linguistics <https://www.nodebox.net/code/index.php/Linguistics>`_

- Bitmap
  
  * `Core Image <https://www.nodebox.net/code/index.php/Core_Image>`_ -- would need to be ported to PIL
  * `iSight <https://www.nodebox.net/code/index.php/iSight>`_ -- deal with generic webcams using Pygame (`howto <https://stackoverflow.com/a/9712824/122400>`_)
  * `Quicktime <https://www.nodebox.net/code/index.php/Quicktime>`_ -- use a Python video lib

- Systems

  * `Ants <https://www.nodebox.net/code/index.php/Ants>`_
  * `Noise <https://www.nodebox.net/code/index.php/Noise>`_

- Design

  * `Grid <https://www.nodebox.net/code/index.php/Grid>`_

- Typography

  * `Pixie <https://www.nodebox.net/code/index.php/Pixie>`_
  * `Fatpath <https://www.nodebox.net/code/index.php/Fatpath>`_

- Tangible

  * `WiiNode <https://www.nodebox.net/code/index.php/WiiNode>`_
  * `OSC <https://www.nodebox.net/code/index.php/OSC>`_

- Other

  * `Flowerewolf <https://github.com/karstenw/Library/tree/master/flowerewolf>`_
  * `twyg <https://github.com/karstenw/Library/tree/master/twyg>`_


Look for 'Help Out' issues
--------------------------

The `issues tagged 'Help Out' <https://github.com/shoebot/shoebot/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+out%22>`_ don't need a deep knowledge of Shoebot internals, and there's a good variety of tasks to be done.


Make text editor plugins
------------------------

While our simple editor is around, power-users will be using their favourite text editor to hack on Shoebot scripts. Having plugins for any popular text editor would be a fantastic addition.


Integrate Shoebot with other software
-------------------------------------

Shoebot can be a great tool to complement other software, be it for

- SVG, PDF or bitmap generation
- simple visualizations
- interact in real-time with the socket server

If you see a use case where Shoebot could be helpful, we'll be more than happy to support you in implementing it.


Non-development tasks
=====================

Find bugs in our documentation and fix them
-------------------------------------------

We're missing many details and we'd definitely welcome some help here. While actual contributions to the documentation would be the best, we'd be more than happy with pointing out the parts that are missing or plain wrong. Use the ``documentation`` label on the issue tracker to help us on this.


Try installing on Windows or Mac OS X
-------------------------------------

Just knowing what happens on these platforms would be really useful for us so we can provide support for them. Try it out and post an issue for any problem that you find.

