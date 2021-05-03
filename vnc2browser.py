import sys
import struct
import json
from threading import Thread

import asyncio
import websockets

from twisted.python import usage, log
from twisted.internet import reactor, protocol
#~ from twisted.internet import defer
from twisted.internet.protocol import Factory, Protocol

from domonic.html import *
#from domonic.constants.color import Color
from domonic.constants.keyboard import KeyCode
from domonic.CDN import *
from domonic.events import EventDispatcher, KeyboardEvent, MouseEvent
#from domonic.geom import Rect


class Rect():
    def __init__(self, x,y,width,height):
        self.x=x
        self.y=y
        self.width=width
        self.height=height

import rfb

# js/html -> vnc
KEYMAPPINGS = {
    KeyCode.BACKSPACE:rfb.KEY_BackSpace,
    KeyCode.TAB:rfb.KEY_Tab,
    KeyCode.ENTER:rfb.KEY_Return,
    KeyCode.ESCAPE:rfb.KEY_Escape,
    KeyCode.RETURN:rfb.KEY_KP_Enter,
    KeyCode.UP:rfb.KEY_Up,
    KeyCode.DOWN:rfb.KEY_Down,
    KeyCode.RIGHT:rfb.KEY_Right,
    KeyCode.LEFT:rfb.KEY_Left,
    KeyCode.INSERT:rfb.KEY_Insert,
    KeyCode.DELETE:rfb.KEY_Delete,
    KeyCode.HOME:rfb.KEY_Home,
    KeyCode.END:rfb.KEY_End,
    KeyCode.PAGE_UP:rfb.KEY_PageUp,
    KeyCode.PAGE_DOWN:rfb.KEY_PageDown,
    KeyCode.F1:rfb.KEY_F1,
    KeyCode.F2:rfb.KEY_F2,
    KeyCode.F3:rfb.KEY_F3,
    KeyCode.F4:rfb.KEY_F4,
    KeyCode.F5:rfb.KEY_F5,
    KeyCode.F6:rfb.KEY_F6,
    KeyCode.F7:rfb.KEY_F7,
    KeyCode.F8:rfb.KEY_F8,
    KeyCode.F9:rfb.KEY_F9,
    KeyCode.F10:rfb.KEY_F10,
    KeyCode.F11:rfb.KEY_F11,
    KeyCode.F12:rfb.KEY_F12,
    KeyCode.F13:rfb.KEY_F13,
    KeyCode.F14:rfb.KEY_F14,
    KeyCode.F15:rfb.KEY_F15,
}
'''
MODIFIERS = {
    'K_NUMLOCK':          rfb.KEY_Num_Lock,
    'K_CAPSLOCK':         rfb.KEY_Caps_Lock,
    'K_SCROLLOCK':        rfb.KEY_Scroll_Lock,
    'K_RSHIFT':           rfb.KEY_ShiftRight,
    'K_LSHIFT':           rfb.KEY_ShiftLeft,
    'K_RCTRL':            rfb.KEY_ControlRight,
    'K_LCTRL':            rfb.KEY_ControlLeft,
    'K_RALT':             rfb.KEY_AltRight,
    'K_LALT':             rfb.KEY_AltLeft,
    'K_RMETA':            rfb.KEY_MetaRight,
    'K_LMETA':            rfb.KEY_MetaLeft,
    'K_LSUPER':           rfb.KEY_Super_L,
    'K_RSUPER':           rfb.KEY_Super_R,
    'K_MODE':             rfb.KEY_Hyper_R,        #???
    #~ K_HELP:             rfb.
    #~ K_PRINT:            rfb.
    'K_SYSREQ':           rfb.KEY_Sys_Req,
    'K_BREAK':            rfb.KEY_Pause,          #???
    'K_MENU':             rfb.KEY_Hyper_L,        #???
    #~ K_POWER:            rfb.
    #~ K_EURO:             rfb.
}                        
'''
# class Rect():
#     def __init__(self,x,y,width,height):
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height
#         pass


class VNC2B(EventDispatcher):
    """VNC2B"""
    
    def __init__(self):
        super().__init__(self)
        width, height = 640, 480
        self.setRFBSize(width, height)
        self.alive = 1
        self.loopcounter = 0
        self.buttons = 0
        self.protocol = None

        self.addEventListener( KeyboardEvent.KEYDOWN, self.on_keydown )
        self.addEventListener( KeyboardEvent.KEYUP, self.on_keyup )

        self.addEventListener( MouseEvent.MOUSEMOVE, self.on_mousemove )
        self.addEventListener( MouseEvent.MOUSEDOWN, self.on_mousedown )
        self.addEventListener( MouseEvent.MOUSEUP, self.on_mouseup )

    def on_keydown(self, event):
        print('a key was pressed', event)

        #if event.key in MODIFIERS:
        #    self.protocol.keyEvent(MODIFIERS[event.key], down=1)
        if event.key in KEYMAPPINGS:
            self.protocol.keyEvent(KEYMAPPINGS[event.key])
        #elif event.unicode:
        #    self.protocol.keyEvent(ord(event.unicode))
        #else:
        #    print("warning: unknown key")
            

    def on_keyup(self, event):
        print('a key was released')
        #self.protocol.keyEvent(MODIFIERS[e.key], down=0)
    #~ else:
        #~ print "unknown key %r" % (e)

    def on_mousemove(self, event):
        print('mousemove', event)
        self.buttons  = event.buttons[0] and 1
        self.buttons |= event.buttons[1] and 2
        self.buttons |= event.buttons[2] and 4
        self.protocol.pointerEvent(event.x, event.y, self.buttons)
        #~ print event.pos

    def on_mousedown(self, event):
        print('mousedown', event)
        if event.button == 1: self.buttons |= 1
        if event.button == 2: self.buttons |= 2
        if event.button == 3: self.buttons |= 4
        if event.button == 4: self.buttons |= 8
        if event.button == 5: self.buttons |= 16
        self.protocol.pointerEvent(event.x, event.y, self.buttons)

    def on_mouseup(self, event):
        print('mouseup', event)
        if event.button == 1: self.buttons &= ~1
        if event.button == 2: self.buttons &= ~2
        if event.button == 3: self.buttons &= ~4
        if event.button == 4: self.buttons &= ~8
        if event.button == 5: self.buttons &= ~16
        self.protocol.pointerEvent(event.x, event.y, self.buttons)

    def setRFBSize(self, width, height, depth=32):
        """change screen size"""
        self.width, self.height = width, height
        self.area = Rect(0, 0, width, height)
        self.screen = None
        self.background = None

    def setProtocol(self, protocol):
        """attach a protocol instance to post the events to"""
        self.protocol = protocol

    def checkEvents(self):
        """process events from the queue"""
        seen_events = 1
        return seen_events

    def mainloop(self, dum=None):
        # TODO - at moment calls for screen updates. but maybe could be the socket response doing that.
        # however that would then require a connection to render the framebuggerupdate event.
        # print('loop')
        no_work = self.checkEvents()
        if self.alive:
            reactor.callLater(no_work and 0.020, self.mainloop)
    
    #~ def error(self):
        #~ log.msg('error, stopping reactor')
        #~ reactor.stop()


class RFBToGUI(rfb.RFBClient):
    """RFBClient protocol that talks to the GUI app"""
    
    def vncConnectionMade(self):
        """choose appropriate color depth, resize screen"""
        #print( "Desktop name: %r" % self.name )
        #~ print "redmax=%r, greenmax=%r, bluemax=%r" % (self.redmax, self.greenmax, self.bluemax)
        #~ print "redshift=%r, greenshift=%r, blueshift=%r" % (self.redshift, self.greenshift, self.blueshift)

        self.remoteframebuffer = self.factory.remoteframebuffer
        self.screen = self.remoteframebuffer.screen
        #self.queue = self.remoteframebuffer.queue
        self.remoteframebuffer.setProtocol(self)
        self.remoteframebuffer.setRFBSize(self.width, self.height, 32)
        self.setEncodings(self.factory.encodings)
        self.setPixelFormat()           #set up pixel format to 32 bits
        self.framebufferUpdateRequest() #request initial screen update
        self.frame = None

    def vncRequestPassword(self):
        print('password request')
        if self.factory.password is not None:
            self.sendPassword(self.factory.password)
        else:
            print('NO PASSWORD HAS BEEN PROVIDED')
    
    def beginUpdate(self):
        """begin series of display updates"""
        print('start updates')
        self.frame = []

    def commitUpdate(self, rectangles = None):
        """finish series of display updates"""
        #~ log.msg("screen unlock")
        # pygame.display.update(rectangles)
        # TODO 
        print('UPDATE NOW')
        queue.append(self.frame)
        self.framebufferUpdateRequest(incremental=1)
        # self.framebufferUpdateRequest(incremental=1)

    def updateRectangle(self, x, y, width, height, data):
        """new bitmap data"""
        #~ print "%s " * 5 % (x, y, width, height, len(data))
        #~ log.msg("screen update")
        #self.screen.blit(
        #    pygame.image.fromstring(data, (width, height), 'RGBX'),     #TODO color format
        #    (x, y)
        #)
        print(data, (width, height), 'RGBX', x, y)

    def copyRectangle(self, srcx, srcy, x, y, width, height):
        """copy src rectangle -> destinantion"""
        #~ print "copyrect", (srcx, srcy, x, y, width, height)
        # self.screen.blit(self.screen,
        #     (x, y),
        #     (srcx, srcy, width, height)
        # )
        print(srcx, srcy, x, y, width, height)


    def fillRectangle(self, x, y, width, height, color):
        """fill rectangle with one color"""
        #~ remoteframebuffer.CopyRect(srcx, srcy, x, y, width, height)
        # self.screen.fill(struct.unpack("BBBB", color), (x, y, width, height))
        # TODO -
        if type(color) != bytes:
            color = bytes(color,'latin-1')
        #print( x, y, width, height, struct.unpack("BBBB", color))
        col = struct.unpack("BBBB", color) 
        #print(col)
        try:
            hexa = "#%02x%02x%02x%02x" % col
        except Exception as e:
            print('fail', col)
            hexa = "#ffffff"

        data = [x, y, width, height, hexa]
        #global queue
        self.frame.append(data)


    def bell(self):
        print("katsching")
        pass

    def copy_text(self, text):
        print(f"Clipboard: {text}")
        pass

'''
#use a derrived class for other depths. hopefully with better performance
#that a single class with complicated/dynamic color conversion.
class RFBToGUIeightbits(RFBToGUI):
    def vncConnectionMade(self):
        print('sup')
        """choose appropriate color depth, resize screen"""
        self.remoteframebuffer = self.factory.remoteframebuffer
        self.screen = self.remoteframebuffer.screen
        self.remoteframebuffer.setProtocol(self)
        self.remoteframebuffer.setRFBSize(self.width, self.height, 8)
        self.setEncodings(self.factory.encodings)
        self.setPixelFormat(bpp=8, depth=8, bigendian=0, truecolor=1,
            redmax=7,   greenmax=7,   bluemax=3,
            redshift=5, greenshift=2, blueshift=0
        )
        self.palette = self.screen.get_palette()
        self.framebufferUpdateRequest()

    def updateRectangle(self, x, y, width, height, data):
        """new bitmap data"""
        #~ print "%s " * 5 % (x, y, width, height, len(data))
        #~ assert len(data) == width*height
        bmp = pygame.image.fromstring(data, (width, height), 'P')
        bmp.set_palette(self.palette)
        self.screen.blit(bmp, (x, y))

    def fillRectangle(self, x, y, width, height, color):
        """fill rectangle with one color"""
        self.screen.fill(ord(color), (x, y, width, height))
'''

class VNCFactory(rfb.RFBFactory):
    """A factory for remote frame buffer connections."""
    
    def __init__(self, remoteframebuffer, depth, fast, *args, **kwargs):
        rfb.RFBFactory.__init__(self, *args, **kwargs)
        self.remoteframebuffer = remoteframebuffer
        if depth == 32:
            print('a')
            self.protocol = RFBToGUI
        elif depth == 8:
            print('b')
            self.protocol = RFBToGUIeightbits
        else:
            raise ValueError
            
        if fast:
            self.encodings = [
                rfb.COPY_RECTANGLE_ENCODING,
                rfb.RAW_ENCODING,
            ]
        else:
            self.encodings = [
                rfb.COPY_RECTANGLE_ENCODING,
                rfb.HEXTILE_ENCODING,
                rfb.CORRE_ENCODING,
                rfb.RRE_ENCODING,
                rfb.RAW_ENCODING,
            ]


    def buildProtocol(self, addr):
        display = addr.port - 5900
        print('Python VNC Viewer on %s:%s' % (addr.host, display))
        return rfb.RFBFactory.buildProtocol(self, addr)

    def clientConnectionLost(self, connector, reason):
        log.msg("connection lost: %r" % reason.getErrorMessage())
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        log.msg("cannot connect to server: %r\n" % reason.getErrorMessage())
        reactor.stop()

class Options(usage.Options):
    optParameters = [
        ['display',     'd', '0',               'VNC display'],
        ['host',        'h', None,              'remote hostname'],
        ['outfile',     'o', None,              'Logfile [default: sys.stdout]'],
        ['password',    'p', None,              'VNC password'],
        ['depth',       'D', '32',              'Color depth'],
    ]
    optFlags = [
        ['shared',      's',                    'Request shared session'],
        ['fast',        'f',                    'Fast connection is used'],
    ]

#~ def eventcollector():
    #~ while remoteframebuffer.alive:
        #~ pygame.event.pump()
        #~ e = pygame.event.poll()
        #~ if e.type != NOEVENT:
            #~ print e
            #~ reactor.callFromThread(remoteframebuffer.processEvent, e)
    #~ print 'xxxxxxxxxxxxx'

remoteframebuffer = VNC2B()
queue = []

def main():
    o = Options()
    try:
        o.parseOptions()
    except usage.UsageError as errortext:
        print(sys.argv[0], errortext)
        raise SystemExit

    depth = int(o.opts['depth'])

    logFile = sys.stdout
    if o.opts['outfile']:
        logFile = o.opts['outfile']
    log.startLogging(logFile)
    


    host = o.opts['host']
    display = int(o.opts['display'])
    if host is None:
        host = 'localhost:1'#inputbox.ask(screen, "Host")
        if host == '':
            raise SystemExit
        if ':' in host:
            host, display = host.split(':')
            if host == '':  host = 'localhost'
            display = int(display)

    # connect to this host and port, and reconnect if we get disconnected
    reactor.connectTCP(
        host,                                   #remote hostname
        display + 5900,                         #TCP port number
        VNCFactory(
                remoteframebuffer,              #the application/display
                depth,                          #color depth
                o.opts['fast'],                 #if a fast connection is used
                o.opts['password'],             #password or none. (vnc passwords should be encrypted)
                int(o.opts['shared']),          #shared session flag
        )
    )

    # run the socket server
    async def update(websocket, path):
        while True:
            msg = await websocket.recv()
            dom_event = json.loads(msg)

            print(msg)
            t = dom_event['type']
            evt = None

            if t == "keydown":
                evt = KeyboardEvent(t)
                evt.keyCode = dom_event['keyCode']
                print('keydown', evt)
        
            elif t == "keyup":
                evt = KeyboardEvent(t)
                evt.keyCode = dom_event['keyCode']
                print('keyup',evt)

            elif t == 'mousedown':
                evt = MouseEvent(t)
                evt.x = dom_event['clientX']
                evt.y = dom_event['clientY']
                # evt.buttons = dom_event['buttons']
                print('mousedown', evt)

            elif t == 'mouseup': 
                evt = MouseEvent(t)
                evt.x = dom_event['clientX']
                evt.y = dom_event['clientY']
                print('mouseup', evt)

            elif t == "mousemove":
                evt = MouseEvent(t)
                evt.x = dom_event['clientX']
                evt.y = dom_event['clientY']
                print('mousemove', evt)
                
            if evt is not None:
                # listen for mouse events.
                global remoteframebuffer
                remoteframebuffer.dispatchEvent( evt )

            global queue
            if len(queue)>0:
                await websocket.send(json.dumps(queue))
                queue=[]  # TODO - lock the queue on both sides 

    def bg_thread(loop, server, queue):
        loop.run_until_complete(server)
        loop.run_forever()


    server_loop = asyncio.new_event_loop()
    server = websockets.serve(update, '0.0.0.0', 5555, loop=server_loop)

    t = Thread(target=bg_thread, args=(server_loop,server,queue))
    t.start()

    reactor.callLater(0.1, remoteframebuffer.mainloop)
    reactor.run()









# create webpage with a socket connection back to our server so it can get the data
page = html(
# make a canvas
style('''
    canvas {
        background: #131c35 linear-gradient(black,#192853, black);
        display:block; position:absolute;
        top:0; left:0; right:0; bottom:0;
    }
    ''',
    _type="text/css"
),
body(
    
    input(_placeholder="localhost:1", _id="host"), input(_placeholder="port", _id="port"), input(_placeholder="password", _id="password"),
    script(_scr=CDN_JS.JQUERY_3_5_1),
    canvas(_id="canvas", _width="1280", _height="800")),

# listen on the socket and call draw when we get a message
script('''
//const socket = new WebSocket('ws://0.0.0.0:5555');
const socket = new WebSocket('ws://domain.com:5560'); // your nginx should listen on 5560 and forward to 5555

socket.onmessage = function(event) { data = JSON.parse(event.data); draw(); };  // TOOD - dont send json. just data with seperator


function stringify_object(object, depth=0, max_depth=2) {
    // change max_depth to see more levels, for a touch event, 2 is good
    if (depth > max_depth)
        return 'Object';

    const obj = {};
    for (let key in object) {
        let value = object[key];
        if (value instanceof Node)
            // specify which properties you want to see from the node
            value = {id: value.id};
        else if (value instanceof Window)
            value = 'Window';
        else if (value instanceof Object)
            value = stringify_object(value, depth+1, max_depth);

        if(key=="originalEvent"){ // note im stripping this one off
          continue;
        }

        obj[key] = value;
    }

    return depth? obj: JSON.stringify(obj);
}

$(canvas).ready(function() { 
    $("canvas").on('mousedown', function(event){ 
        socket.send( stringify_object(event) );
    }); 
    $("canvas").on('mouseup', function(event){ 
        socket.send( stringify_object(event) );
    }); 
    $("body").on("keydown", function(event){
        socket.send( stringify_object(event) );
    })
    $("body").on("keyup", function(event){
        socket.send( stringify_object(event) );
    })
    $("canvas").on("mousemove", function(event){
        //socket.send( stringify_object(event) );
    })
});


'''),

# draw the data
script('''
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    var WIDTH=canvas.width;
    var HEIGHT=canvas.height;
    function resizeCanvas(){
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      WIDTH=canvas.width;
      HEIGHT=canvas.height;
    }
    function animate() {
        socket.send('!'); // send any old message to trigger socket response. so i can control the framerate
        // draw();
    }
    function draw() {

        console.log(data);
        data = data.flat();
        // context.clearRect(0, 0, WIDTH, HEIGHT);
        // context.globalCompositeOperation = "source-over";
        var i, r;
        for(i = 0; i < data.length; i++ ) {
         //   point = data[i];
           // context.save();
           // context.translate(point.x,point.y);
           // context.rotate( point.rotation );
           // context.restore();

            r = data[i];
            drawRect(r[0],r[1],r[2],r[3],r[4]);
        }
    }
    function drawRect(x,y,width,height,color){
      context.beginPath();
      context.fillStyle = color.substr(0,7);
      context.fillRect(x, y, width, height);
      //context.lineWidth = 2;
      //context.strokeStyle = '#000';
      //context.stroke();
      context.fill();
    }
    var intID;
    function setFramerate(val){
      clearInterval(this.intID)
      this.intID = setInterval( function(){ animate(); }, 1000/val );
      // window.requestAnimationFrame(animate);
    }
    setFramerate(60);
    resizeCanvas();
''')

)

# render a page of rectangle data sent by the vnc server
render( page, 'viewer.html' )


if __name__ == '__main__':
    main()
