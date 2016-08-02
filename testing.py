import random

class Descriptor:
    def __init__(self):
        self.value = 10

    def __get__(self, instance, owner):
        print("GET")
        return self.value

    def __set__(self, instance, value):
        print("SET")
        self.value = value

class Values(object):
    number = Descriptor()
    def __init__(self, value):
        self.number = value

value = Values(7)
print(value.number)
value.number = 5
print(value.number)
