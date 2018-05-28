class Link:
    """Link module"""
    #name = [] # node 1 to node 2
    #speed_coefficient = 12.336 # us
    #delay = 50 # us
    #macrotick = 1 # us
    #buffercon = 50 #us

    def __init__(self, name, speed_coefficient, delay, macrotick):
        self.name = name
        self.speed_coefficient = speed_coefficient
        self.delay = delay
        self.macrotick = macrotick
