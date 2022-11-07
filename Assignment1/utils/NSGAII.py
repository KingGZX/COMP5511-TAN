'''
author: Zhexuan Gu
Date: 2022-10-15 15:49:14
LastEditTime: 2022-10-22 09:55:29
FilePath: /Assignment 1 2/utils/NSGAII.py
Description: Please implement
'''

import profile
from utils.GeneticAlgorithm import SimpleTSPGA
import random
import numpy as np
import utils.visualizeScatterPlot as vsp

class NSGAII(SimpleTSPGA):
    def __init__(self, customernum: int, population: int, distancematrix, mutationrate: float, crossoverrate: float, objNum:int, xcoords, ycoords) -> None:
        super().__init__(customernum, population, distancematrix, mutationrate, crossoverrate, xcoords, ycoords)
        self.objFunctions = objNum
        self.Profits = []                       # profit matrix
        self.dominated = []
        self.dominationcnt = []
        self.Levels = []
        self.individualRank = []
        self.individualCost = []
        self.individualProfit = []
        self.crowdingDistances = []
        self.oldGeneration = []
        self.routecosts = []
        self.profits = []
        
        
    def RandomGenerateProfit(self):
        random.seed(3047)
        self.Profits = np.zeros_like(np.array(self.diatance_matrix))
        for i in range(self.genes):
            for j in range(self.genes):
                if i != j:
                    self.Profits[i, j] = 1 + random.random() * (50 - 1)
        
    def CalculateProfits(self, chromosome):
        realProf = 0
        for i in range(1, len(chromosome)):
            realProf += self.Profits[chromosome[i - 1]][chromosome[i]]
        # back to the start point
        if len(chromosome) > 1:
            realProf += self.Profits[chromosome[len(chromosome) - 1]][chromosome[0]]
        return realProf

    def Crowding_Distance(self, num:int):
        self.crowdingDistances = [0] * num
        CostSortIndex = sorted(range(len(self.individualCost)), key= lambda k:self.individualCost[k])
        ProfitSortIndex = sorted(range(len(self.individualProfit)), key= lambda k:self.individualProfit[k])
        maxCost, minCost = max(self.individualCost), min(self.individualCost)
        maxProfit, minProfit = max(self.individualProfit), min(self.individualProfit)
        for i in range(num):
            # find choromosome in each sorted index
            index1, index2 = CostSortIndex.index(i), ProfitSortIndex.index(i)
            # extrat the neiborhood of it and calculate the distance
            if index1 == 0 or index2 == 0 or index1 == num - 1 or index2 == num - 1:
                self.crowdingDistances[i] = np.inf
            else:
                n1Cost, n2Cost = self.individualCost[index1 - 1], self.individualCost[index1 + 1]
                n1Profit, n2Profit = self.individualProfit[index2 - 1], self.individualProfit[index2 + 1]
                # normalize the distance
                self.crowdingDistances[i] = (n2Cost - n1Cost) / (maxCost - minCost) + (n2Profit - n1Profit) / (maxProfit - minProfit)
    
    def Fast_non_Dominated_Sort(self, num:int):
        # because there're at most N levels of domination(N = population)
        self.dominated, self.dominationcnt, self.Levels = [[] for i in range(num)], [0] * num, [[] for i in range(num)]
        self.individualCost, self.individualProfit, self.individualRank = [0] * num, [0] * num, [0] * num
        for i in range(num):
            choromosomea = self.chromosomes[i]
            costa, profita = self.TSPCost(choromosomea), self.CalculateProfits(choromosomea)
            self.individualCost[i], self.individualProfit[i] = costa, profita
            for j in range(i + 1, num):
                choromosomeb = self.chromosomes[j]
                # judge the relationship of dominance
                costb, profitb = self.TSPCost(choromosomeb), self.CalculateProfits(choromosomeb)
                if (costa <= costb and profita > profitb) or (profita >= profitb and costa < costb):
                    # then b is dominated by a!
                    self.dominationcnt[j] += 1
                    self.dominated[i].append(j)
                if (costb <= costa and profitb > profita) or (profitb >= profita and costb < costa):
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
            
    def Tournament_Selection(self):
        # keep randomly selecting choromosomes and choose the highest fitness(here rank[Levels]) 
        # as the parents
        self.oldGeneration.clear()
        self.oldGeneration = self.chromosomes.copy()
        self.chromosomes.clear()
        # 25 iterations, for each iteraion, choose 2 from 4
        group_num = int(self.population / 2)
        group_size = 4
        win_num = 2
        for iters in range(group_num):
            temp = []
            for i in range(group_size):
                index = random.randint(0, self.population - 1)
                temp.append(index)
            # temp is the choromosome indexe and the priority should be given to thoses choromosmes whose rank value is smaller
            res = sorted(range(len(temp)), key=lambda k : self.individualRank[temp[k]])
            for j in range(win_num):
                self.chromosomes.append(self.oldGeneration[temp[res[j]]])
        """
        then perform same crossover and mutation operatoer, and we will record all offsprings in the list 
        after one generation, combine the old and new together and perform non-dominate sort to choose 
        self.population number as the real next generation
        """
        
    def Elitism(self):
        cnt = self.population
        temp = self.chromosomes.copy()
        self.chromosomes.clear()
        rank = 0
        while cnt > 0:
            if len(self.Levels[rank]) <= cnt:
                cnt -= len(self.Levels[rank])
                for index in self.Levels[rank]:
                    self.chromosomes.append(temp[index])
                rank += 1
            else:
                res = sorted(range(len(self.Levels[rank])), key=lambda k : self.crowdingDistances[self.Levels[rank][k]], reverse=True)
                for i in range(cnt):
                    self.chromosomes.append(temp[self.Levels[rank][res[i]]])
                cnt = 0
    
    def ShowTextResult(self):
        for choromosome in self.chromosomes:
            cost = self.TSPCost(choromosome)
            profit = self.CalculateProfits(choromosome)
            print("optimal solution: cost is %f, profit is %f." % (cost, profit)) 
            
    def DrawPareto(self):
        for chromosome in self.chromosomes:
            self.RoutecostAndProfit(chromosome)
        vsp.drawParetoFront(self.routecosts, self.profits)
    
    def RoutecostAndProfit(self, chromosome):
        realLen, realProf = 0, 0
        for i in range(1, len(chromosome)):
            # for a specific i in chromosome, it's just a gene
            realLen += self.diatance_matrix[chromosome[i], chromosome[i - 1]]
            realProf += self.Profits[chromosome[i - 1], chromosome[i]]
        # back to the start point
        if len(chromosome) > 1:
            realLen += self.diatance_matrix[chromosome[len(chromosome) - 1], chromosome[0]]
            realProf += self.Profits[chromosome[len(chromosome) - 1], chromosome[0]]
        self.routecosts.append(realLen)
        self.profits.append(realProf)
    
    def Solver(self, epochs: int):
        self.RandomGenerateProfit()
        # 1. initialize the population and perform non-dominated fast sort on it
        self.RandomGenerateChoromoson()
        self.Fast_non_Dominated_Sort(self.population)
        #print("After initialization, the best route cost is: %d" % (self.initialbestlen))
        for epoch in range(epochs):
            self.Tournament_Selection()
            self.SimpleCrossOver()
            self.SimpleMutation()
            # after excuting basic above operatoer above
            # combine the new and old generation and take the best chromosomes
            self.chromosomes = self.oldGeneration + self.offSprings
            totalNum = len(self.chromosomes)
            self.Fast_non_Dominated_Sort(totalNum)
            self.Crowding_Distance(totalNum)
            # choose elites!
            self.Elitism()
            self.offSprings.clear()
            # print some debugging information
            if epoch % 10 == 0:
                print("process -------- %f%%" % (epoch * 100 / epochs))
        self.ShowTextResult()
        self.DrawPareto()
        self.individualCost.clear()
        self.individualProfit.clear()
        self.individualRank.clear()
        self.dominated.clear()
        self.dominationcnt.clear()
        self.crowdingDistances.clear()
        self.oldGeneration.clear()
        self.Levels.clear()
        self.chromosomes.clear()
        self.best_route.clear()
        self.Percentage.clear()
        self.Fitness.clear()
        self.offSprings.clear()
        self.profits.clear()
        self.routecosts.clear()
        self.routeLen = np.inf
        #pass