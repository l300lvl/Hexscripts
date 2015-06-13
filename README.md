# Hexscripts
Miscellaneous Hexchat scripts I've found some need for or felt like updating.
###Trimmer.py
######If you want to use the "TabXHider" script alongside this, you **must** install the Python 3 plugin during installation. Using both with the Python 2 plugin will cause a crash.
Shortens extremely long usernames. Yes, I'm looking at you, "aaaaaaaaAAAAAaaaaaaa".

Custom cut-off length, optional "cap" character.

![alt text](demo/trim.PNG "10 cut w/ ~ cap")

###TabXHider.py
######Updated to work with both Python 2 and 3 plugin. There are incompatibilities; see [Trimmer](https://github.com/migwu/Hexscripts#trimmer) for details.
Removes the ugly "Close tab" button from the channel tab view.
![alt text](demo/noX.PNG "Removes tab close button")

###Gossip.py
Stores mentions on a per-channel basis and (optionally) private messages for later viewing. Great to avoid lengthy scroll-back. Logging can be toggled on and off and are session independent.
![alt text](demo/gossip.PNG "Mention stored here from user, \"mysterious_user\". Username with trimmer.py.")