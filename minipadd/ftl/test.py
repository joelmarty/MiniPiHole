from unittest import TestCase

from minipadd import ftl


class Test(TestCase):
    def test_get_stats(self):
        stats = ftl.get_stats('192.168.50.97', '96c3780287c58bd0867c8cd9b2d60c387ea070c4df3f87d2d3e3c770d3baab0b')
        print(stats)
