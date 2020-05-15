import unittest
from project.hello_world import say_hello


class TestHellWorld(unittest.TestCase):

    def test_say_hello(self):
        self.assertEqual("Hello Alice", say_hello("Alice"), "Expected to say hello to Alice")
        self.assertEqual("Hello Bob", say_hello("Bob"), "Expected to say hello to Bob")
