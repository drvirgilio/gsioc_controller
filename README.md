gsioc_controller
================

Gilson GSIOC communication protocol written in python.

Requires pyserial.

Example instantiation:

    import gsoic from gsoic
    g = gsoic()
    g.createSerial(port=0,timeout=0.1)
    g.connect(ID=5)
    g.iCommand("1f")
    g.bCommand("Text to display")
    g.closeSerial()

This is my first python project so I hope you like it :)