# circular_buffer.py

class CircularBuffer:
    def __init__(self, capacity):
        """
        Initializes the circular buffer with a fixed capacity.
        
        :param capacity: The maximum number of elements the buffer can hold.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.start = 0  # Points to the oldest element
        self.end = 0    # Points to the next insertion point
        self.size = 0   # Current number of elements in the buffer

    def add(self, item):
        """
        Adds a new item to the buffer. Overwrites the oldest item if the buffer is full.
        
        :param item: The item to be added to the buffer.
        """
        self.buffer[self.end] = item
        self.end = (self.end + 1) % self.capacity
        
        if self.size < self.capacity:
            self.size += 1
        else:
            # Buffer is full; move the start pointer to overwrite the oldest data
            self.start = (self.start + 1) % self.capacity

    def get_all(self):
        """
        Retrieves all items in the buffer in FIFO order.
        
        :return: A list of items from oldest to newest.
        """
        items = []
        for i in range(self.size):
            index = (self.start + i) % self.capacity
            items.append(self.buffer[index])
        return items

    def __str__(self):
        """
        Returns a string representation of the buffer.
        """
        return "CircularBuffer([" + ", ".join(str(item) for item in self.get_all()) + "])"

    def is_full(self):
        """
        Checks if the buffer is full.
        
        :return: True if full, else False.
        """
        return self.size == self.capacity

    def is_empty(self):
        """
        Checks if the buffer is empty.
        
        :return: True if empty, else False.
        """
        return self.size == 0
