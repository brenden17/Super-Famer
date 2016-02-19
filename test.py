import unittest

from simulation import *

class TestStringMethods(unittest.TestCase):

    def test_game(self):
        basic_config = BasicConfig()
        simulate(basic_config, count=300)

        # dog_config = DogConfig('Without dogs')
        # simulate(dog_config, count=100)

        dice1_config = Dice1Config()
        simulate(dice1_config, count=300)


if __name__ == '__main__':
    unittest.main()