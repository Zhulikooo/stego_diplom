"""
Генератор случайных чисел по формуле LCG
Параметры: a = 1664525, c = 1013904223, m = 2^32
"""

class LCG:
    def __init__(self, seed, a=1664525, c=1013904223, m=2**32):
        self.state = seed
        self.a = a
        self.c = c
        self.m = m
    
    def next(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state
    
    def random_float(self):
        return self.next() / self.m
    
    def random_int(self, low, high):
        return low + int(self.random_float() * (high - low))