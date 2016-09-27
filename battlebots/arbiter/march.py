class March:
    def __init__(self, road, origin, destination, owner, size):
        self.road = road
        self.origin = origin
        self.destination = destination
        self.owner = owner
        self.size = size
        self.owner.marches.add(self)

    def dispatch(self, steps=None):
        if self.size > self.origin.garrison:
            self.owner.warning('{} is trying to send more soldiers than '
                               'available. Sending all remaining soldiers.'
                               .format(self.owner))
        self.size = min(self.size, self.origin.garrison)
        self.origin.garrison -= self.size
        self.road.add_march(self, steps)

    def die(self):
        self.owner.marches.remove(self)

    def __repr__(self):
        return ('<March from {origin} to {destination} by {owner} '
                'with {size} soldiers>'.format(**self.__dict__))
