'''
author: Zhexuan Gu
Date: 2022-10-15 12:31:48
LastEditTime: 2022-10-22 11:01:26
FilePath: /Assignment 1 2/utils/WeightedMultiObject.py
Description: Weighted Multi-objective optimization function
'''
from cmath import cos
from utils.GeneticAlgorithm import SimpleTSPGA
import random
import numpy as np
import utils.visualizeScatterPlot as vsp

class WeightedGA(SimpleTSPGA):
    def __init__(self, customernum: int, population: int, distancematrix, mutationrate: float, crossoverrate: float, weight:float, xcoords, ycoords) -> None:
        super().__init__(customernum, population, distancematrix, mutationrate, crossoverrate, xcoords, ycoords)
        self.Profits = []
        self.RealRouteLen = np.inf
        self.RealProfits = np.inf
        self.weight = weight
        self.routecosts = []
        
    def RandomGenerateProfit(self):
        random.seed(3047)
        self.Profits = np.zeros_like(np.array(self.diatance_matrix))
        for i in range(self.genes):
            for j in range(self.genes):
                if i != j:
                    self.Profits[i, j] = 1 + random.random() * (50 - 1)
                    
    
    '''
    description: use a weighted function to achive multiobject optimization 
    event: 
    param {float} param
    return {*}
    '''    
    def TSPCost(self, chromosome):
        cost = 0
        realLen, realProf = 0, 0
        for i in range(1, len(chromosome)):
            # for a specific i in chromosome, it's just a gene
            realLen += self.diatance_matrix[chromosome[i], chromosome[i - 1]]
            realProf += self.Profits[chromosome[i - 1], chromosome[i]]
        # back to the start point
        if len(chromosome) > 1:
            realLen += self.diatance_matrix[chromosome[len(chromosome) - 1], chromosome[0]]
            realProf += self.Profits[chromosome[len(chromosome) - 1], chromosome[0]]
        cost = realLen - realProf * self.weight
        if cost < self.routeLen:
            self.RealRouteLen, self.RealProfits = realLen, realProf
        return cost
    
    def FitnessFunction(self, cost: float):
        # to help tackle the negtive cost problem 
        '''
        acoording to the experiment, the cost is usually very big at first, like 500+
        so the fitness will be approximatly 0, thus, in simple selection funtion, bugs occurring
        
        I use -cost mainly to make the priority of a negtive cost bigger!!
        
        and exponetial funtion guarantees that the fitness must be positive!!
        '''
        return np.exp(-cost/1e4) 
    
    def Solver(self, epochs: int):
        self.RandomGenerateProfit()
        self.RandomGenerateChoromoson()
        for epoch in range(epochs):
            self.ElitismSelect()
            self.SimpleCrossOver()
            self.SimpleMutation()
            self.CalculateFitness()
            # print some debugging information
            if epoch % 200 == 0:
                print("Epoch %d: best route length is %f, best profit is %f, minimum cost is %f  -------- avearage fitness is %f" % (epoch, self.RealRouteLen, 
                                                                                                                 self.RealProfits, self.routeLen,
                                                                                              sum(self.Fitness) * 1e4 / self.population))
        print("Finish Training, best route is: ", end="")
        print(self.best_route)
        print("The real route length is %f, while the profit is %f" % (self.RealRouteLen, self.RealProfits))
        print(self.Fitness)
        self.chromosomes.clear()
        self.best_route.clear()
        self.Percentage.clear()
        self.routecosts.clear()
        self.routeLen = np.inf
        return self.RealRouteLen, self.RealProfits
        #pass