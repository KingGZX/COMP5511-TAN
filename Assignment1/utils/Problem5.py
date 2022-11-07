'''
author: Zhexuan Gu
Date: 2022-10-22 15:45:51
LastEditTime: 2022-10-22 18:10:48
FilePath: /Assignment 1 2/utils/Problem5.py
Description: Please implement
'''
import utils.visualizeScatterPlot as vsp
import numpy as np
import random
from utils.NSGAII import NSGAII

class NSGAIIForP5(NSGAII):
    def __init__(self, customernum: int, population: int, distancematrix, mutationrate: float, crossoverrate: float, objNum: int, xcoords, ycoords, readytime, duetime) -> None:
        super().__init__(customernum, population, distancematrix, mutationrate, crossoverrate, objNum, xcoords, ycoords)
        self.readytime = readytime
        self.duetime = duetime
        self.individualViolationtime = []
        self.violationtime = []
    
    def CalculateViolationtime(self, chromosome):
        violationTime = 0
        currentTime = 0
        length = len(chromosome)
        for i in range(0, length - 1):
            if currentTime >= self.readytime[chromosome[i]] and currentTime <= self.duetime[chromosome[i]]:
                pass
            else:
                if currentTime < self.readytime[chromosome[i]]:
                    violationTime += self.readytime[chromosome[i]] - currentTime
                else:
                    violationTime += currentTime - self.duetime[chromosome[i]]
            currentTime += self.diatance_matrix[chromosome[i]][chromosome[i + 1]]
        # for the last gene
        if currentTime < self.readytime[chromosome[length - 1]]:
            violationTime += self.readytime[chromosome[length - 1]] - currentTime
        if currentTime > self.duetime[chromosome[length - 1]]:
            violationTime += currentTime - self.duetime[chromosome[length - 1]]
        return violationTime
    
    def Crowding_Distance(self, num:int):
        self.crowdingDistances = [0] * num
        CostSortIndex = sorted(range(len(self.individualCost)), key= lambda k:self.individualCost[k])
        ProfitSortIndex = sorted(range(len(self.individualProfit)), key= lambda k:self.individualProfit[k])
        ViolationTimeIndex = sorted(range(len(self.individualViolationtime)), key= lambda k:self.individualViolationtime[k])
        maxCost, minCost = max(self.individualCost), min(self.individualCost)
        maxProfit, minProfit = max(self.individualProfit), min(self.individualProfit)
        maxViolationtime, minViolationtime = max(self.individualViolationtime), min(self.individualViolationtime)
        for i in range(num):
            # find choromosome in each sorted index
            index1, index2, index3 = CostSortIndex.index(i), ProfitSortIndex.index(i), ViolationTimeIndex.index(i)
            # extrat the neiborhood of it and calculate the distance
            if index1 == 0 or index2 == 0 or index3 == 0 or index1 == num - 1 or index2 == num - 1 or index3 == num - 1:
                self.crowdingDistances[i] = np.inf
            else:
                n1Cost, n2Cost = self.individualCost[index1 - 1], self.individualCost[index1 + 1]
                n1Profit, n2Profit = self.individualProfit[index2 - 1], self.individualProfit[index2 + 1]
                n1Violationtime, n2Violationtime = self.individualViolationtime[index3 - 1], self.individualViolationtime[index3 + 1]
                # normalize the distance
                self.crowdingDistances[i] = (n2Cost - n1Cost) / (maxCost - minCost) + (n2Profit - n1Profit) / (maxProfit - minProfit) + (n2Violationtime - n1Violationtime) / (maxViolationtime - minViolationtime)
    
    def Fast_non_Dominated_Sort(self, num:int):
        # because there're at most N levels of domination(N = population)
        self.dominated, self.dominationcnt, self.Levels = [[] for i in range(num)], [0] * num, [[] for i in range(num)]
        self.individualViolationtime, self.individualCost, self.individualProfit, self.individualRank = [0] * num, [0] * num, [0] * num, [0] * num
        for i in range(num):
            choromosomea = self.chromosomes[i]
            costa, profita, violationtimea = self.TSPCost(choromosomea), self.CalculateProfits(choromosomea), self.CalculateViolationtime(choromosomea)
            self.individualCost[i], self.individualProfit[i], self.individualViolationtime[i] = costa, profita, violationtimea
            for j in range(i + 1, num):
                choromosomeb = self.chromosomes[j]
                # judge the relationship of dominance
                costb, profitb, violationtimeb = self.TSPCost(choromosomeb), self.CalculateProfits(choromosomeb), self.CalculateViolationtime(choromosomeb)
                if (costa <= costb and profita > profitb and violationtimea <= violationtimeb) or (profita >= profitb and costa < costb and violationtimea <= violationtimeb) or (profita >= profitb and costa <= costb and violationtimea < violationtimeb):
                    # then b is dominated by a!
                    self.dominationcnt[j] += 1
                    self.dominated[i].append(j)
                if (costb <= costa and profitb > profita and violationtimeb <= violationtimea) or (profitb >= profita and costb < costa and violationtimeb <= violationtimea) or (profitb >= profita and costb <= costa and violationtimeb < violationtimea):
                    # opposite situation
                    self.dominationcnt[i] += 1
                    self.dominated[j].append(i)
            if self.dominationcnt[i] == 0:
                # temporary optimal solutions which are not dominated by any other solutions
                self.individualRank[i] = 0
                self.Levels[0].append(i)
        i = 0
        while i < num:
            for j in self.Levels[i]:
                for k in self.dominated[j]:
                    self.dominationcnt[k] -= 1
                    if self.dominationcnt[k] == 0:
                        self.Levels[i + 1].append(k)
                        self.individualRank[k] = i + 1
            i += 1
    
    def DrawPareto(self):
        for chromosome in self.chromosomes:
            self.RoutecostAndProfit(chromosome)
            self.violationtime.append(self.CalculateViolationtime(chromosome))
        vsp.drawPareto3D(self.routecosts, self.profits, self.violationtime)
    
    def Solver(self, epochs: int):
        super().Solver(epochs)
        self.individualViolationtime.clear()
        self.violationtime.clear()
    
    