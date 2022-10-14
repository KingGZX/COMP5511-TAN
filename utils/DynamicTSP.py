'''
author: Zhexuan Gu
Date: 2022-10-09 14:29:52
LastEditTime: 2022-10-11 20:45:07
FilePath: /Assignment 1 2/utils/DynamicTSP.py
Description: Question2 of Assignment1
'''


from random import randrange
from utils.GeneticAlgorithm import SimpleTSPGA
import numpy as np

class DynamicGA(SimpleTSPGA):
    def __init__(self, customernum: int, population: int, distancematrix, mutationrate: float, crossoverrate: float, xcoords, ycoords) -> None:
        super().__init__(customernum, population, distancematrix, mutationrate, crossoverrate)
        self.VisitPermission = 50       # At first, it's only allowed to visit 50 customers
        self.Xcoordinations = xcoords   
        self.Ycoordinations = ycoords
        self.LastEventBestChromosomes = []
    
    '''
    description: the length of choromosome will not always be 100, it should be VisitPermission
    event: 
    param {*} self
    return {*}
    '''    
    def RandomGenerateChoromoson(self, num):
        for i in range(num):
            chromosome = list(np.random.permutation(self.VisitPermission))
            cost = self.TSPCost(chromosome)
            fitness = self.FitnessFunction(cost)
            index = self.FitnessInsertion(fitness)
            self.chromosomes.insert(index, chromosome)
            self.initialbestlen = min(self.initialbestlen, cost)
    
    def ResetDistanceMatrix(self, e):
        # distance matrixs
        if e != 0:
            self.VisitPermission += 10
            print("Now visiting %d customers" % (self.VisitPermission))
        newxcoords, newycoords = [], []
        for i in range(len(self.Xcoordinations)):
            newxcoords.append(self.Xcoordinations[i] + np.cos(np.pi * e / 2))
            newycoords.append(self.Ycoordinations[i] + np.sin(np.pi * e / 2))
        for i in range(len(newxcoords)):
            for j in range(i + 1, len(newxcoords), 1):
                x_diff = newxcoords[j] - newxcoords[i]
                y_diff = newycoords[i] - newycoords[j]
                distance = np.sqrt(np.square(x_diff) + np.square(y_diff))
                self.diatance_matrix[i][j] = self.diatance_matrix[j][i] = distance
                
    def ReuseChromosomes(self):
        # reuse 10 of the last event best choromosomes
        reusenum = 10
        self.LastEventBestChromosomes = self.chromosomes[0:10].copy()
        self.Fitness.clear()
        self.chromosomes.clear()
        self.RandomGenerateChoromoson(self.population - reusenum)
        for i in range(reusenum):
            newCustomersPermutation = list(np.random.choice(10, 10, replace=False) + self.VisitPermission - 10)
            for item in newCustomersPermutation:
                self.LastEventBestChromosomes[i].insert(randrange(len(self.LastEventBestChromosomes[i]) + 1), item)
            cost = self.TSPCost(self.LastEventBestChromosomes[i])
            fitness = self.FitnessFunction(cost)
            index = self.FitnessInsertion(fitness)
            self.chromosomes.insert(index, self.LastEventBestChromosomes[i])
            self.initialbestlen = min(self.initialbestlen, cost)
        self.LastEventBestChromosomes.clear()
        
    
    def Solver(self, epochs: int, reusing:bool):
        self.RandomGenerateChoromoson(self.population)
        #self.routeLen = self.initialbestlen
        print("After initialization, the best route cost is: %d" % (self.initialbestlen))
        print("Now visiting %d customers" % (self.VisitPermission))
        for epoch in range(epochs):
            self.ElitismSelect()
            self.SimpleCrossOver()
            self.SimpleMutation()
            self.CalculateFitness()
            # print some debugging information
            if epoch % 100 == 0:
                print("Epoch %d: best route length is %d  -------- avearage fitness is %f" % (epoch, self.routeLen, 
                                                                                              sum(self.Fitness) * 1e4 / self.population))
            if epoch % 100 == 0 and epoch <= 500:
                self.ResetDistanceMatrix(epoch // 100)
                if epoch != 0:
                    if reusing == True:
                        self.ReuseChromosomes()
                    else:
                        self.chromosomes.clear()
                        self.Fitness.clear()
                        self.RandomGenerateChoromoson(self.population)
                self.routeLen = np.inf
        print("Finish Training, best route is: ", end="")
        print(self.best_route)
        self.chromosomes.clear()
        self.Percentage.clear()
        self.Fitness.clear()
        self.best_route.clear()
        self.routeLen = np.inf
        #pass