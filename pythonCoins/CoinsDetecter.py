import math
from typing import Dict, List, Tuple, Optional

from colorama import Fore, Style

import pandas as pd

from CoinsKeeper import CoinsKeeper


class CoinsDetector:
    """
    Class which contains all required methods and information in order to find fake coin among genuine ones.
    """

    def __init__(self, ck: CoinsKeeper):
        self.ck = ck
        self.coinsState: Dict[str, int] = self.ck.getCoinsState()

        # It's considered that fake coins can be only in one of these three states
        self.fakeCoinIsLighter = True if self.coinsState["n_fake_l"] >= 1 else False
        self.fakeCoinIsHeavier = True if self.coinsState["n_fake_h"] >= 1 else False
        self.fakeCoinIsUnknown = True if self.coinsState["n_fake"] >= 1 else False

        self.coinsNumber = sum(self.coinsState.values())
        # self.left_pan: List[int] = None
        # self.right_pan: List[int] = None
        self.weightingCount = 0

    # def getLeftPan(self):
    #     return self.left_pan
    #
    # def getRightPan(self):
    #     return self.right_pan

    def weightingProcess(self, groupL: List[int], groupR: List[int], managingItem: int):
        """
        Displays weighting two groups of coins.

        Args:
            groupL: first group of coins indices
            groupR: second group of coins indices
            managingItem: value that describes result of weighting:
                if managingItem == -1, groupL is heavier than groupR

                if managingItem == 0, groupL is equal to groupR by weight

                if managingItem == 1, groupL is lighter than groupR
        """
        print("Weighting---------------")
        indices = [i for i in range(self.coinsNumber)]
        indecesStr = list(map(str, indices))

        indecesStr[groupL[0]] = f"({Fore.GREEN}" + indecesStr[groupL[0]]
        indecesStr[groupL[-1]] = indecesStr[groupL[-1]] + f"{Style.RESET_ALL})"

        indecesStr[groupR[0]] = f"({Fore.GREEN}" + indecesStr[groupR[0]]
        indecesStr[groupR[-1]] = indecesStr[groupR[-1]] + f"{Style.RESET_ALL})"

        formattedStr = ", ".join(indecesStr)

        print(f"Indices of coins: {formattedStr}\n")
        if managingItem == 1:
            print(f"{groupL} < {groupR}\nLeft group is lighter than right group")
        elif managingItem == -1:
            print(f"{groupL} > {groupR}\nLeft group is heavier than right group")
        else:
            print(f"{groupL} = {groupR}\nLeft group is equal to right group by weight")
        print("------------------------\n")

    def solver(self):
        """
        Function executes algorithms of finding fake coins and print the result, according to coins information:

        if it's unknown if fake coin is lighter or heavier, genCaseAlgorithm method will be executed;

        if we know whether fake coin is lighter or heavier, partCaseAlgorithm method will be executed;
        """
        if self.fakeCoinIsLighter or self.fakeCoinIsHeavier:
            n = math.ceil(math.log10(self.coinsNumber) / math.log10(3))

            print(f"Expected number of weighting: {n}")
            print(f"Coins number = {self.coinsNumber}")
            print()

            self.weightingCount = 0
            fakeCoinIndex = self.partCaseAlgorithm(n)
            print(f"In the end weighting number equals {self.weightingCount}")

            if self.fakeCoinIsLighter:
                print(f"lighter fake coin has index: {fakeCoinIndex}")
            else:
                print(f"heavier fake coin has index: {fakeCoinIndex}")

        elif self.fakeCoinIsUnknown:
            n = math.ceil((math.log10(self.coinsNumber) / math.log10(3)) + 1)

            print(f"{n=}")
            print(f"Coins number = {self.coinsNumber}")
            print()

            self.weightingCount = 0
            fakeCoinIndex, fakeCoinWeightIndex = self.genCaseAlgorithm(n)
            print(f"In the end weighting number equals {self.weightingCount}")

            if fakeCoinWeightIndex == -1:
                print(f"lighter fake coin has index: {fakeCoinIndex}")
            elif fakeCoinWeightIndex == 1:
                print(f"heavier fake coin has index: {fakeCoinIndex}")
            elif fakeCoinWeightIndex is None:
                print(f"can't find if fake coin is lighter or heavier")

    def partCaseAlgorithm(self, n):
        """
        In this function it's considered that we know if fake coins is lighter or heavier

        Args:
            n: number of weighting to find fake coin
        Returns:
            index: index of fake coin
        """

        currIndices = [i for i in range(self.coinsNumber)]

        for i in range(n):
            if len(currIndices) == 2:
                currIndices = self.getFakeGroupPartCaseAlg(currIndices[:1], currIndices[1:], None)
                # print(currIndices)
                return currIndices[0]
            currCoinsNumber = len(currIndices)
            # curr_n = math.ceil(math.log10(currCoinsNumber) / math.log10(3))
            b = int(math.floor(currCoinsNumber / 3))

            c = currCoinsNumber - 2 * b
            # c coins from the right
            group3 = currIndices[-c:]

            # coins in the middle
            group2 = currIndices[b: -c]

            # coins from the left
            group1 = currIndices[:b]

            currIndices = self.getFakeGroupPartCaseAlg(group1, group2, group3)

        # print(currIndices)
        return currIndices[0]

    def getFakeGroupPartCaseAlg(self, group1: List[int], group2: List[int], group3: Optional[List[int]]) -> List[int]:
        """
        The method compares weights of two coins group using the method balance from CoinsKeeper class,
        and then decides which group contains a fake coin, depending on whether a fake coin is lighter or heavier.
        There are no intersections between groups of coin's indices
        Args:
            group1: first group of coins with their indices in it
            group2: second group of coins with their indices in it
            group3: third group of coins with their indices in it

        Returns:
            group: list of coin's indices which contains a fake coin
        """
        # 1 if group2 > group1
        # -1 if group2 < group1
        # - if group2 == group1
        managing_item = self.ck.balance(group1, group2)
        self.weightingCount += 1
        self.weightingProcess(groupL=group1, groupR=group2, managingItem=managing_item)

        if managing_item == 0:
            return group3

        if self.fakeCoinIsLighter:
            if managing_item == 1:
                return group1
            # managing_item == -1
            else:
                return group2

        elif self.fakeCoinIsHeavier:
            if managing_item == 1:
                return group2
            # managing_item == -1
            else:
                return group1

    def genCaseAlgorithm(self, n):
        """
        In this function it's considered that we don't know if fake coins is lighter or heavier

        Args:
            n: number of weighting to find fake coin
        Returns:
            index: index(integer) of fake coin
        """
        indices = [i for i in range(self.coinsNumber)]
        currIndices = [i for i in range(self.coinsNumber)]
        assert self.coinsNumber > 2, \
            "Can't solver the problem for unknown fake coin weight relation and for 2 coins in total"
        fakeCoinWeightIndex: int = None

        while self.weightingCount <= (n + 2):
            currCoinsNumber = len(currIndices)
            if currCoinsNumber == 1:
                return currIndices[0], fakeCoinWeightIndex

            elif currCoinsNumber == 2:
                managing_item0 = self.ck.balance(currIndices[:1], currIndices[1:])
                self.weightingCount += 1
                self.weightingProcess(currIndices[:1], currIndices[1:], managingItem=managing_item0)

                genCoinIndex = list(filter(lambda x: x not in currIndices, indices))[0]
                managing_item1 = self.ck.balance(currIndices[:1], indices[genCoinIndex: genCoinIndex + 1])
                self.weightingCount += 1
                self.weightingProcess(currIndices[:1], indices[genCoinIndex: genCoinIndex + 1],
                                      managingItem=managing_item1)

                if managing_item1 == 0:
                    if managing_item0 == 1:
                        return currIndices[1], 1
                    elif managing_item0 == -1:
                        return currIndices[1], -1

                elif managing_item1 == 1:
                    return currIndices[0], -1

                # managing_item1 == -1
                else:
                    return currIndices[0], 1

            if currCoinsNumber == 3:
                group0 = [currIndices[0], ]
                group1 = [currIndices[1], ]
                group2 = [currIndices[2], ]
                group3 = None

            else:
                b = currCoinsNumber / 3
                if b == int(b):
                    b = int(b) - 1
                else:
                    b = int(math.floor(b))

                c = currCoinsNumber - 3 * b
                # c coins from the right
                group3 = currIndices[-c:]

                # coins in the middle
                group2 = currIndices[2 * b: -c]

                # coins after group0
                group1 = currIndices[b:2 * b]

                # coins from the left
                group0 = currIndices[:b]

            currIndices, a = self.getFakeGroupGenCaseAlg(group0, group1, group2, group3)
            if a is not None:
                fakeCoinWeightIndex = a
            print(f"current indices = {currIndices}")

        print(currIndices, fakeCoinWeightIndex)
        return currIndices[0]

    def getFakeGroupGenCaseAlg(self, group0: List[int], group1: List[int], group2: List[int], group3: List[int]) -> \
            Tuple[List[int], Optional[int]]:
        """
        The method compares weights of three coins group using the method balance from CoinsKeeper class,
        and then decides which group contains a fake coin.
        Also, method tries to figure out whether fake coin is lighter or heavier.
        There are no intersections between groups of coin's indices

        Args:
            group0: first group of coins with their indices in it
            group1: second group of coins with their indices in it
            group2: third group of coins with their indices in it
            group3: forth group of coins with their indices in it

        Returns:
            group: group with fake coin;
            indicator: indicates whether this fake coin is heavier or lighter, can be either -1, 1 or None.
        """
        # 1 if groupR > groupL
        # -1 if groupR < groupL
        # - if groupR == groupL
        # managing_item = self.ck.balance(groupL, groupR)

        managing_item0 = self.ck.balance(group0, group1)
        self.weightingCount += 1
        self.weightingProcess(groupL=group0, groupR=group1, managingItem=managing_item0)

        managing_item1 = self.ck.balance(group0, group2)
        self.weightingCount += 1
        self.weightingProcess(groupL=group0, groupR=group2, managingItem=managing_item1)

        # group0, group1, group2 have no difference in weight
        if managing_item0 == 0 and managing_item1 == 0:
            return group3, None

        # group2 is different to group0 and group1 by weight
        elif managing_item0 == 0 and managing_item1 != 0:
            if managing_item1 == 1:
                return group2, 1
            # managing_item1 == -1
            else:
                return group2, -1

        # group1 is different to group0 and group2 by weight
        elif managing_item0 != 0 and managing_item1 == 0:
            if managing_item0 == 1:
                return group1, 1
            # managing_item0 == -1
            else:
                return group1, -1

        # group0 is different to group1 and group2 by weight
        elif managing_item0 != 0 and managing_item1 != 0:
            if managing_item0 == 1:
                return group0, -1
            # managing_item0 == -1
            else:
                return group0, 1


def run(n_gen=9, n_fake=1, n_fake_l=0, n_fake_h=0, weights=None):
    """
    Function is used to create all required objects and to invoke method solve.
    Also, print in pretty way coins with their weights and indices.
    """
    ck = CoinsKeeper(n_gen=n_gen, n_fake=n_fake, n_fake_l=n_fake_l, n_fake_h=n_fake_h, weights=weights)
    indices = [i for i in range(len(ck.weights))]
    df = pd.DataFrame(columns=indices)
    df.index.name = "indices"
    df.loc["weights"] = ck.weights

    print(df.to_markdown())

    cd = CoinsDetector(ck)
    cd.solver()


def main():
    """Function which is served as console interface of this program"""
    while True:
        print("\n\n")
        print("Якщо бажаєте вийти, введіть '#'")
        print("Якщо бажаєте, щоб маси монеток згенерувалися самостійно, введіть '0'")
        print("Якщо бажаєте, щоб маси монеток прочиталися з дефолтного файлу "
              "з ім'ям 'coinsWeightsFile.txt', введіть '1'")
        print("Якщо маєте текстовий файл з масами монеток, введіть його ім'я")
        managing_val = input(":")

        filename = None
        if managing_val == "#":
            break

        elif managing_val == "0":
            filename = None
            print("Введіть кількість справжніх монеток або натисніть 'Enter', щоб вибрати кількість 9")

            n_gen = 9
            managing_val = input(":")
            if managing_val != "":
                try:
                    managing_val = int(managing_val)
                    n_gen = managing_val
                except ValueError:
                    pass

        elif managing_val == 1:
            filename = "file"

        elif ".txt" in managing_val:
            filename = managing_val

        #
        print("Якщо бажаєте вибрати варіант знаходження фальшивої монетки, яка легша по масі, введіть '0'")
        print("Якщо бажаєте вибрати варіант знаходження фальшивої монетки, яка важча по масі, введіть '1'")
        print("Якщо бажаєте вибрати варіант знаходження фальшивої монетки, маса якої невідома введіть '2'")
        managing_val = input(":")

        n_fake = 1
        n_fake_l = 0
        n_fake_h = 0

        if managing_val == "0":
            n_fake = 0
            n_fake_l = 1
            n_fake_h = 0
        elif managing_val == "1":
            n_fake = 0
            n_fake_l = 0
            n_fake_h = 1
        elif managing_val == "2":
            n_fake = 1
            n_fake_l = 0
            n_fake_h = 0

        run(n_gen=n_gen, n_fake=n_fake, n_fake_l=n_fake_l, n_fake_h=n_fake_h, weights=filename)


if __name__ == '__main__':
    # ck = CoinsKeeper(n_gen=25, n_fake=1, n_fake_l=0, n_fake_h=0, weights="file")
    # indices = [i for i in range(len(ck.weights))]
    # df = pd.DataFrame(columns=indices)
    # df.index.name = "indices"
    # df.loc["weights"] = ck.weights

    # print(df.to_markdown())

    # cd = CoinsDetector(ck)
    # cd.solver()
    #
    main()
