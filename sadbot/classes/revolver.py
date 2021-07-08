class Revolver:
    """This is the revolver class"""

    def __init__(self, capacity: int) -> None:
        """Initializes a revolver"""
        self.capacity = capacity
        self.drum = [0] * self.capacity
        self.fired = 0

    def set_capacity(self, capacity: int) -> str:
        """Changes the revolver's capacity"""
        self.__init__(capacity)
        return "Changed revolver capacity. "

    def reload(self, bullets: int) -> str:
        """Reoloads the revolver bullets"""
        if bullets >= self.capacity:
            return "There are too many bullets, y'all would be dead lmao"
        for i in range(0, bullets):
            self.drum[i] = 1
        random.shuffle(self.drum)
        self.fired = 0
        return "Reloaded!"

    def shoot(self) -> str:
        """Shoots"""
        if self.fired > self.capacity - 1:
            return "No more bullets, you have to .reload"
        self.fired = self.fired + 1
        if self.drum[self.fired - 1] == 1:
            return "OH SHIIii.. you're dead, lol."
        return "Eh.. you survived."
