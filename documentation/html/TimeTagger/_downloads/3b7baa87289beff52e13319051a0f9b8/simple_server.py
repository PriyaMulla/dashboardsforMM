"""
Example Pyro5 RPC server exposing parts of the Time Tagger API.

See the tutorial article in the Time Tagger's Documentation:
https://www.swabianinstruments.com/static/documentation/TimeTagger/tutorials/TimeTaggerRPC.html

This example requires Pyro5 package that can be installed as:
    > pip install Pyro5

Start this script on a computer with the Time Tagger connected.
    > python server.py

By default the server is accessible only on this PC.
If you want to make it available over the network then you will need to 
    1. Set the "host" parameter of the daemon to your current IP address.
    2. Update the connection string in the simple_example.py 
       according to the URI printed when you start the server.

"""

import TimeTagger as TT
try:
    import Pyro5.api
except ModuleNotFoundError:
    import sys
    print('Please install Pyro5 module. "python -m pip install Pyro5"')
    sys.exit()


@Pyro5.api.expose
class Correlation:
    """Adapter class for Correlation measurement."""

    def __init__(self, tagger, args, kwargs):
        self._obj = TT.Correlation(tagger._obj, *args, **kwargs)

    def start(self):
        return self._obj.start()

    def startFor(self, capture_duration, clear):
        return self._obj.startFor(capture_duration, clear=clear)

    def stop(self):
        return self._obj.stop()

    def clear(self):
        return self._obj.clear()

    def isRunning(self):
        return self._obj.isRunning()

    def getIndex(self):
        return self._obj.getIndex().tolist()

    def getData(self):
        return self._obj.getData().tolist()


@Pyro5.api.expose
class DelayedChannel():
    """Adapter class for DelayedChannel."""

    def __init__(self, tagger, args, kwargs):
        self._obj = TT.DelayedChannel(tagger._obj, *args, **kwargs)

    def getChannel(self):
        return self._obj.getChannel()


@Pyro5.api.expose
class TimeTagger():
    """Adapter for the TimeTagger class"""

    def __init__(self, args, kwargs):
        self._obj = TT.createTimeTagger(*args, **kwargs)

    def setTriggerLevel(self, channel, voltage):
        return self._obj.setTriggerLevel(channel, voltage)

    def getTriggerLevel(self, channel):
        return self._obj.getTriggerLevel(channel)

    def getSerial(self):
        return self._obj.getSerial()

    def getModel(self):
        return self._obj.getModel()

    def setTestSignal(self, *args):
        return self._obj.setTestSignal(*args)

    def setInputDelay(self, channel, delay):
        return self._obj.setInputDelay(channel, delay)

    def setDeadtime(self, channel, deadtime):
        return self._obj.setDeadtime(channel, deadtime)

    def getInputDelay(self, channel):
        return self._obj.getInputDelay(channel)

    def getTestSignal(self, channel):
        return self._obj.getTestSignal(channel)

    def getDeadtime(self, channel):
        return self._obj.getDeadtime(channel)

    def sync(self, timeout):
        return self._obj.sync(timeout=timeout)


@Pyro5.api.expose
class TimeTaggerRPC:
    """Adapter for the Time Tagger Library"""

    def scanTimeTagger(self):
        """Return the serial numbers of the available Time Taggers."""
        return TT.scanTimeTagger()

    def createTimeTagger(self, *args, **kwargs):
        """Create the Time Tagger."""
        tagger = TimeTagger(args, kwargs)
        self._pyroDaemon.register(tagger)
        return tagger

    def freeTimeTagger(self, tagger_proxy):
        objectId = tagger_proxy._pyroUri.object
        tagger = self._pyroDaemon.objectsById.get(objectId)
        self._pyroDaemon.unregister(tagger)
        return TT.freeTimeTagger(tagger._obj)

    def Correlation(self, tagger_proxy, *args, **kwargs):
        """Create Correlation measurement."""
        objectId = tagger_proxy._pyroUri.object
        tagger = self._pyroDaemon.objectsById.get(objectId)
        pyro_obj = Correlation(tagger, args, kwargs)
        self._pyroDaemon.register(pyro_obj)
        return pyro_obj
    
    def DelayedChannel(self, tagger_proxy, *args, **kwargs):
        """Create DelayedChannel."""
        objectId = tagger_proxy._pyroUri.object
        tagger = self._pyroDaemon.objectsById.get(objectId)
        pyro_obj = DelayedChannel(tagger, args, kwargs)
        self._pyroDaemon.register(pyro_obj)
        return pyro_obj


if __name__ == '__main__':
    # Start server and expose the TimeTaggerRPC class
    with Pyro5.api.Daemon(host='localhost', port=23000) as daemon:
        # Register class with Pyro
        uri = daemon.register(TimeTaggerRPC, 'TimeTagger')
        # Print the URI of the published object
        print(uri)
        # Start the server event loop
        daemon.requestLoop()
