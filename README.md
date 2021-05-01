VNC2Browser
-----------

An experiment to see if I could send VNC frame buffer data to the browser over a web socket,
and return keyboard / mouse / clipboard event data back.

UNFINISHED - only just started this. 
(pushing as after an evening hackathon I have it rendering to the browser. still a long way to go)


Usage
-----

1. setup xfce on something your aws box. check you can login and it looks pretty etc.
2. Setup a vncserver
3. Configure nginx to have a ws:// endpoint
4. Run your vncserver
5. follow Setup steps below.
6. place viewer.html somewhere visitable. i.e. serve it. Then Visit it in the browser


Setup
-----

```

cd vnc2browser

python3 -m venv venv
. venv/bin/activate

python -m pip install -r requirments.txt
```


start the server passing it your password
```
python vnc2browser.py -password XXXXX

```

running vnc2browser.py will generate the viewer.html. You can edit this and put it where it needs to be. Then visit that page.

(edit the socket endpoint in viewer.html which appears when you run the server)
const socket = new WebSocket('ws://domain.com:5560'); // i.e. if your nginx listens on 5560 and forward to 5555





Bugs
---------
- Lots ;P
- You will need at least 3 cpus if you visit a browser on the same box as running it. My advice is to setup the nginx config and do the browser testing on your side. Or do local network with 2 computers.
- Dont login with a normal vnc client. then run this. It will boot you out. (might depend on your vnc client or setup)


Notes
---------
- (uses threading for now instead of asyncio so should work with any 3.x version)
- At the moment I have 2 threads sharing a global var. This needs to be done differently and with a lock


References:
-----------
heavily borrowed (or compeletey stolen?) from here.... http://code.google.com/p/python-vnc-viewer/

  http://www.realvnc.org
  https://github.com/david415/python-vnc-viewer/
  https://tools.ietf.org/id/draft-levine-rfb-02.html#anchor5
  https://vncdotool.readthedocs.io/en/0.8.0/rfbproto.html#representation-of-pixel-data



More Notes
----------

vnserver commands:


vnserver  # start it


vnserver -kill :1  # < white space formating here is important or it talks to wrong one (if you have 2 installed).


vncpasswd  # < change password. 


remember to :


ssh -i myapp.pem -L 5901:localhost:5901 root@myapp.com

then you can just connect to localhost:5901 or 2 or 3 etc when you vnc.

(Mac has a built-in screen-sharing app that can just connect.)




Warnings:
-----------

Don't actually use this for anything ever. Just use a normal vnc client.



LICENCE:
-----------
It uses 2 files that carry their own licenses. (public domain and MIT)

They may have modificatons to work in python3 as they were py2 before

Apart from that. No license. free to use
