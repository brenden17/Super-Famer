import math
from random import randint

import numpy as np


RABBIT, SHEEP, PIG, COW, HORSE, SMALL_DOG, BIG_DOG, FOX, WOOF = range(9)
ANIMAL = ('rabbit', 'sheep', 'pig', 'cow', 'horse', 'small_dog', 'big_dog', 'fox', 'woof')

SOURCE, PRICE, TARGET = range(3)
DICE_ANIMAL1 = 7
DICE_ANIMAL2 = 8

# PARAMETERS : ANIMAL, EXCHANGE_RATE, OCCURRENCE OF FOX AND WOOF, DICE
class BasicConfig(object):
    def __init__(self):
        self.name = 'basic config'
        self.DICE1_OCCURRENCES = ((0, 6, RABBIT),
                            (6, 8, SHEEP),
                            (8, 10, PIG),
                            (10, 11, HORSE),
                            (11, 12, FOX))

        self.DICE2_OCCURRENCES = ((0, 6, RABBIT),
                            (6, 9, SHEEP),
                            (9, 10, PIG),
                            (10, 11, COW),
                            (11, 12, FOX))

        self.EXCHANGE_TABLE = ((RABBIT, 6, SHEEP),
                            (SHEEP, 2, PIG),
                            (PIG, 3, COW),
                            (COW, 2, HORSE),
                            (SHEEP, 2, SMALL_DOG),
                            (COW, 1, BIG_DOG))
        self._animal_price = {}
        self._win_score = 0

        self.n_player = 3
        self.apply_dog = False

    @property
    def animal_price(self):
        for i, r in enumerate(self.EXCHANGE_TABLE):
            if i == 0:
                self._animal_price[0] = 1
            self._animal_price[r[2]] = r[1] * self._animal_price[r[0]]
        return self._animal_price

    @property
    def win_score(self):
        self._win_score = sum([self._animal_price[i] for i in range(5)])
        return self._win_score


class DogConfig(BasicConfig):
    def __init__(self):
        super(DogConfig, self).__init__()
        self.apply_dog = True


class ExchangeTableConfig(BasicConfig):
    def __init__(self):
        super(ExchangeTableConfig, self).__init__()
        self.name = 'Changed EXCHANGE_TABLE - Rabbit to Sheep : 6->3'
        # self.DICE1_OCCURRENCES = ((0, 2, RABBIT),
        #                         (2, 7, SHEEP),
        #                         (7, 10, PIG),
        #                         (10, 11, HORSE),
        #                         (11, 12, FOX))

        self.EXCHANGE_TABLE = ((RABBIT, 3, SHEEP),
                            (SHEEP, 2, PIG),
                            (PIG, 3, COW),
                            (COW, 2, HORSE),
                            (SHEEP, 2, SMALL_DOG),
                            (COW, 1, BIG_DOG))
        

class ExchangeTableConfig2(BasicConfig):
    def __init__(self):
        super(ExchangeTableConfig2, self).__init__()
        self.name = 'Changed EXCHANGE_TABLE - Rabbit to Sheep : 6->3, Pig to Cow: 3->2'
        # self.DICE1_OCCURRENCES = ((0, 2, RABBIT),
        #                         (2, 7, SHEEP),
        #                         (7, 10, PIG),
        #                         (10, 11, HORSE),
        #                         (11, 12, FOX))

        self.EXCHANGE_TABLE = ((RABBIT, 3, SHEEP),
                            (SHEEP, 2, PIG),
                            (PIG, 2, COW),
                            (COW, 2, HORSE),
                            (SHEEP, 2, SMALL_DOG),
                            (COW, 1, BIG_DOG))


class Player(object):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.animals = np.zeros((7+2, 300))
        self.animals[0, 0] = 1
        self.current_score = 0

    
    def clear(self):
        self.animals = np.zeros((7+2, 300))
        self.animals[0, 0] = 1
        self.current_score = 0

    def get_fox(self, t):
        if self.animals[SMALL_DOG, t] > 0:
            self.animals[SMALL_DOG, t] -= 1
        else:
            self.animals[RABBIT, t] = 1
    
    def get_woof(self, t):
        if self.animals[BIG_DOG, t] > 0:
            self.animals[BIG_DOG, t] -= 1
        else:
            self.animals[SHEEP, t] = 0
            self.animals[PIG, t] = 0
            self.animals[COW, t] = 0

    def get_animal(self, animal1, animal2, t):
        if t > 0:
            self.animals[:, t] = self.animals[:, t-1]
        # print('#######################')
        # print(self.current_status(t))
        self.animals[DICE_ANIMAL1] = animal1
        self.animals[DICE_ANIMAL2] = animal2
        self.exchange_by_basic_policy(t)
        # print('exchange_animal_policy')
        # print(self.current_status(t))
        if animal1 == WOOF or animal2 == WOOF:
            self.get_woof(t)
        elif animal1 == FOX or animal2 == FOX:
            self.get_fox(t)
        else:
            if animal1 == animal2:
                self.animals[animal1, t] += 1
            else:
                big_animal, small_animal = (animal1, animal2) if animal1 > animal2 else (animal2, animal1)
                if self.animals[big_animal, t] > 0:
                    self.animals[big_animal, t] += 1
                elif self.animals[small_animal, t] > 0:
                    self.animals[small_animal, t] += 1
                # else self.animals[small_animal, t] > 0:
                #     self.animals[small_animal, t] += 1
                # else:
                #     return
        # print(t, ANIMAL[animal1], ANIMAL[animal2])
        # print(self.current_status(t))

    def exchange_by_basic_policy(self, t, apply_dog=True):
        table = self.config.EXCHANGE_TABLE

        for row in table[:4]:
            if self.animals[row[SOURCE], t] > row[PRICE]:
                self.animals[row[TARGET]] += 1
                self.animals[row[SOURCE], t] -= row[PRICE]

        if self.config.apply_dog:
            for row in table[4:]:
                if self.animals[row[SOURCE], t] > row[PRICE]:
                    self.animals[row[TARGET]] += 1
                    self.animals[row[SOURCE], t] -= row[PRICE]

    def is_finished(self, t):
        self.current_score = sum([self.animals[a, t] * self.config.animal_price[a] for a in range(7)])
        if self.current_score >= self.config.win_score:
            return True
           
        return False
        
    def current_status(self, t):
        return '{}, {}\tR {}\tS {}\tP {}\tC {}\tH {}\tS {}\tB {}\t score {}'.format(t, self.name,
                                                                self.animals[RABBIT, t], 
                                                                self.animals[SHEEP, t],
                                                                self.animals[PIG, t],
                                                                self.animals[COW, t],
                                                                self.animals[HORSE, t],
                                                                self.animals[SMALL_DOG, t],
                                                                self.animals[BIG_DOG, t],
                                                                self.current_score)


class Game(object):
    def __init__(self, config):
        self.n_player = config.n_player
        self.players = [Player(name=str(i)+'-Player', config=config) for i in range(self.n_player)]
        self.config = config
        self.turning_time = 15 # 10 sec

        self.t = 0
        self.total_game_time = 0
        self.winner = None

    def generate_animal(self, animal_occrrences):
        dice = randint(0, 11)
        for occurrence in animal_occrrences:
            if dice in range(occurrence[0], occurrence[1]):
                return occurrence[2]
        return None

    def roll_dice(self):
        animal1 = self.generate_animal(self.config.DICE1_OCCURRENCES)
        animal2 = self.generate_animal(self.config.DICE2_OCCURRENCES)
        return animal1, animal2

    def step(self, turn, t):
        animal1, animal2 = self.roll_dice()
        self.players[turn].get_animal(animal1, animal2, t)

    def play(self):
        self.clear()
        t = 0
        while not self.is_finished(t):
            for turn in range(0, self.n_player):
                self.step(turn, t)
            t = t + 1

        # self.report_summary()
        
    def is_finished(self, t):
        t = t-1 if t > 0 else 0
        result = [player.is_finished(t) for player in self.players]

        if any(result):
            self.total_game_time = t * self.turning_time *  self.n_player
            self.winner = result.index(True)
            self.t = t
        return any(result)
    
    def report_summary(self):
        print('total time {}, {:.2f} min'.format(self.t, self.total_game_time/60.0))
        print('winner {}'.format(self.winner))

    def get_player_score(self):
        return [player.current_score for player in self.players]

    def mean_player_score(self):
        scores = self.get_player_score()
        return sum(scores) * 1.0 / len(scores)

    def std_player_score(self):
        scores = self.get_player_score()
        mean = self.mean_player_score()
        variance = map(lambda x: (x - mean)**2, scores)
        variance_avg = sum(variance) * 1.0 / len(variance)
        return math.sqrt(variance_avg)

    def get_result(self):
        return self.t, self.total_game_time/60.0, self.std_player_score()

    def play_and_report(self):
        self.play()
        return self.get_result()

    def clear(self):
        for player in self.players:
            player.clear()

        self.t = 0
        self.total_game_time = 0
        self.winner = None

def simulate(config, count=10):
    g = Game(config=config)

    results = [g.play_and_report() for _ in range(count)]
    length = len(results)
    t = sum(result[0] for result in results) * 1.0 / length
    total_time = sum(result[1] for result in results) * 1.0 / length
    std_score = sum(result[2] for result in results) * 1.0 / length
    print('***** {} ******'.format(g.config.name))
    print(t, total_time, std_score)
    return (t, total_time, std_score)
