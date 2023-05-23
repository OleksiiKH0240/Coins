import random
from typing import List, Union


class CoinsKeeper:
    '''
    Store weights of coins and general information about them.
    Store method for comparing weights of different groups of coins.
    '''

    def __init__(self, n_gen: int = 9, n_fake: int = 1, n_fake_l: int = 0, n_fake_h: int = 0,
                 weights: Union[List[int], str] = None):
        '''
        Args:
            n_gen: number of genuine coins
            n_fake: number of fake coins, which weights are unknown
            n_fake_l: number of fake coins, which are lighter than genuine coins
            n_fake_h: number of fake coins, which are heavier than genuine coins
            weights: weights for each coin;

                if weights equal None, weights will be generated randomly;

                if weights equal 'file.txt', weights will be read from 'file.txt' file;

                if weights equal 'file', weights will be read from default file, which is set in setWeightsFromTxtFile function.
        '''

        self.n_gen = n_gen
        self.n_fake = n_fake
        self.n_fake_l = n_fake_l
        self.n_fake_h = n_fake_h

        if weights is None:
            self.setRandomWeights()
        elif weights == "file":
            self.setWeightsFromTxtFile()
        elif ".txt" in weights:
            self.setWeightsFromTxtFile(filename=weights)
        else:
            self.weights = weights

    def setRandomWeights(self):
        """
        Function is used to generated weight randomly from range (1, 9) according to information about coins,
        that had been set before.
        """
        possWeights = [i for i in range(4, 7)]

        genuineCoinWeight = random.choice(possWeights)
        possWeights.remove(genuineCoinWeight)
        possWeights = [1, 2, 3] + possWeights + [7, 8, 9]

        # It's considered that fake coins can be only in one of these three states
        if self.n_fake_l >= 1:
            fakeCoinWeight = random.choice(list(filter(lambda x: x < genuineCoinWeight, possWeights)))
        elif self.n_fake_h >= 1:
            fakeCoinWeight = random.choice(list(filter(lambda x: x > genuineCoinWeight, possWeights)))
        # self.n_fake >= 1
        else:
            fakeCoinWeight = random.choice(possWeights)

        possWeights.remove(fakeCoinWeight)

        weights = [genuineCoinWeight, ] * self.n_gen + \
                  [fakeCoinWeight, ] * self.n_fake + \
                  [fakeCoinWeight, ] * self.n_fake_l + \
                  [fakeCoinWeight, ] * self.n_fake_h
        random.shuffle(weights)

        self.weights = weights

    def setWeightsFromTxtFile(self, filename: str = "coinsWeightsFile.txt"):
        """
        Function is used to read weights from .txt file, where each weights are integer values seperated with coma.

        Args:
            filename: file name
        """
        with open(filename, "r") as f:
            weightsStr = f.readline()

        self.weights = list(map(int, weightsStr.split(",")))
        self.n_gen = len(self.weights) - 1

    def balance(self, left_indices, right_indices):
        '''
        weighting of two groups of coins in order to figure out which one is heavier.

        Args:
            left_indices: coins indices in weights list.
            right_indices: coins indices in weights list.
        Returns:
            1: if weight of right group of coins is heavier than weight of left one;

            -1: if weight of right group of coins is lighter than weight of left one;

            0: if weight of right group of coins is equal to weight of left one;
        '''

        leftWeight = sum(map(lambda x: self.weights[x], left_indices))
        rightWeight = sum(map(lambda x: self.weights[x], right_indices))

        if rightWeight > leftWeight:
            return 1

        if rightWeight < leftWeight:
            return -1

        return 0

    def getCoinsState(self):
        """
        Function which return current information about coins.
        """
        d = self.__dict__.copy()
        d.pop("weights")
        return d


if __name__ == "__main__":
    ck = CoinsKeeper(n_gen=9, weights="file")
    print(ck.getCoinsState())
    print(vars(ck))
