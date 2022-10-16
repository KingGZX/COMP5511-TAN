'''
author: Zhexuan Gu
Date: 2022-09-27 16:22:43
LastEditTime: 2022-10-16 13:41:51
FilePath: /Assignment 1 2/utils/GeneticAlgorithm.py
Description: Question1 of Assignment1
'''
import random
import numpy as np

'''
description: It's a minimization problem, so lower cost means higher fitness
event: 
return {*}
'''
class SimpleTSPGA:
    def __init__(self, customernum:int, population:int, distancematrix, mutationrate:float, crossoverrate:float) -> None:
        self.genes = customernum      # this num implys the number of genes
        self.population = population    # generate fixed num of chromosome
        self.diatance_matrix = distancematrix
        self.mutationrate = mutationrate
        self.crossoverrate = crossoverrate
        self.chromosomes = []                                         # record all choromosomes
        self.Elite = []                                               # elite chromosome
        self.Fitness = []                                             # inverse of the cost of a road
        self.Percentage = []                                          # when r-w selection, probability is used
        self.EliteRate = 0.1
        self.routeLen = np.inf
        self.initialbestlen = np.inf
        self.best_route = []
        self.offSprings = []
    
    '''
    description: to make fitness list ordered
    event: 
    param {*} self
    param {float} fitness
    return the rank of the fitness
    '''    
    def FitnessInsertion(self, fitness:float)->int:
        # the higher the fitness, the frontier it should be
        index = len(self.Fitness)
        for i in range(len(self.Fitness)):
            if fitness > self.Fitness[i]:
                index = i
                break
        self.Fitness.insert(index, fitness)
        return index
    
    '''
    description: initially generate some chromosomes, use numpy permutation which helps us directly generate different numbers
    event: 
    param {*} self
    return {*}
    '''    
    def RandomGenerateChoromoson(self):
        for i in range(self.population):
            chromosome = list(np.random.permutation(self.genes))
            cost = self.TSPCost(chromosome)
            fitness = self.FitnessFunction(cost)
            index = self.FitnessInsertion(fitness)
            self.chromosomes.insert(index, chromosome)
            self.initialbestlen = min(self.initialbestlen, cost)

    '''
    description: this function helps calculate the cost of one specific choromosome
    event: 
    param {*} self
    param {*} chromosome
    return {*}
    '''    
    def TSPCost(self, chromosome):
        # just calculate the cost according to the current road
        cost = 0
        for i in range(1, len(chromosome)):
            cost += self.diatance_matrix[chromosome[i], chromosome[i - 1]]
        # back to the start point
        if len(chromosome) > 1:
            cost += self.diatance_matrix[chromosome[len(chromosome) - 1], chromosome[0]]
        return cost
    
    '''
    description: Roulette Wheel Selection
    event: 
    param {*} self
    return {*}
    '''    
    def SimpleSelection(self):
        totalFitness = sum(self.Fitness)
        '''
        since we are definitly going to reintroduce the elite in last generation
        I'm intend not to let those elite take part in the 
        '''
        self.Percentage = [fitness / totalFitness for fitness in self.Fitness]
        # after calculating the percentage, we randomly generate some number and decide which choromosomes are chosen
        selected = []
        for i in range(self.population):
            randomGenerator = np.random.rand()
            temp = 0.0
            # randomly generate a number and judge which interval it falls in 
            for j in range(self.population):
                temp += self.Percentage[j]
                if temp >= randomGenerator:
                    selected.append(self.chromosomes[j])
                    break
        # after selection, update self.choromosome
        self.chromosomes = selected.copy()
        selected.clear()
    
    '''
    description: randomly generate the start and length of crossover part. and use the methodology introduced on class
    event: 
    param {*} self
    param {list} parent1
    param {list} parent2
    return {*}
    '''    
    def PerformReproduction(self, parent1:list, parent2:list):
        # use random generator to ensure the start and length
        chromosomelen = len(parent1)
        randomStart = np.random.randint(0, chromosomelen)
        # I'm not going to exchange a great deal of genes
        randomSliceLen = np.random.randint(0, 30)
        # avoid overflows
        randomSliceLen = min(randomSliceLen, chromosomelen - 1 - randomStart)
        Slice1 = parent1[randomStart:randomStart + randomSliceLen]
        Slice2 = parent2[randomStart:randomStart + randomSliceLen]
        offspring1 = []
        offspring2 = []
        i = 0
        while i < chromosomelen:
            if parent2[i] not in Slice1:
                if len(offspring1) == randomStart:
                    offspring1 += Slice1
                offspring1.append(parent2[i])
            if parent1[i] not in Slice2:
                if len(offspring2) == randomStart:
                    offspring2 += Slice2
                offspring2.append(parent1[i])
            i += 1
        self.offSprings.append(offspring1)
        self.offSprings.append(offspring2)
        return offspring1, offspring2
    
    def SimpleCrossOver(self):
        # just try not to use crossover rate first
        for i in range(0, self.population, 2):
            offspring1, offspring2 = self.PerformReproduction(self.chromosomes[i], self.chromosomes[i + 1])
            self.chromosomes[i], self.chromosomes[i + 1] = offspring1, offspring2
        
    
    '''
    description: for each gene, we generate a random number, if it's smaller than the mutation rate, then excute
    event: 
    param {*} self
    return {*}
    '''    
    def SimpleMutation(self):
        # It's just a kind of swap!
        chromosomelen = len(self.chromosomes[0])
        for i in range(self.population):
            randomGenerator = np.random.rand()
            if randomGenerator <= self.mutationrate:
                # randomly select a element to excute swapping
                exA, exB = random.sample([j for  j in range(chromosomelen)], 2)
                offspring = self.chromosomes[i]
                offspring[exA], offspring[exB] = offspring[exB], offspring[exA]       
                self.chromosomes[i] = offspring
                self.offSprings.append(offspring)

    
    def FitnessFunction(self, cost:float):
        # just use the inverse of cost Function, so the less the cost is, the higher the fitness will be
        return 1/cost
    
    '''
    description: sometimes bugs occur out of expectations. It's mostly about chromosomes being destructed.
    event: 
    param {*} self
    return sanity condition
    '''    
    def SanityCheck(self):
        for choromsome in self.chromosomes:
            if len(choromsome) != self.genes or len(set(choromsome)) != self.genes:
                print("PARENT ERROR")
                return
        print("True")
    
    '''
    description:  keep 10% of elite parents and reintroduce then in next generation
    event: 
    param {*} self
    return {*}
    '''    
    def ElitismSelect(self):
        # keep the best 10% choromosomes and the rest are selected by Roulette Wheel Selection（轮盘法）
        elitenum = int(self.population * self.EliteRate)
        for i in range(elitenum):
            self.Elite.append([self.chromosomes[i], self.Fitness[i]])
        self.SimpleSelection()
    
    '''
    description: fitness function, after each generation, excute it
    event: 
    param {*} self
    return {*}
    '''    
    def CalculateFitness(self):
        self.Fitness.clear()
        self.Percentage.clear()
        generations = self.chromosomes.copy()
        self.chromosomes.clear()
        for i in range(self.population):
            cost = self.TSPCost(generations[i])
            fitness = self.FitnessFunction(cost)
            index = self.FitnessInsertion(fitness)
            self.chromosomes.insert(index, generations[i])
            if cost < self.routeLen:
                self.routeLen = cost
                self.best_route = generations[i]
        # reintroduce the elite choromosomes
        elitenum = int(self.population * self.EliteRate)
        for i in range(elitenum):
            self.Fitness.pop()
            self.chromosomes.pop()
        for i in range(elitenum):
            index = self.FitnessInsertion(self.Elite[i][1])
            self.chromosomes.insert(index, self.Elite[i][0])
        self.Elite.clear()
        generations.clear()
        
    '''
    description: train the model 
    event: 
    param {*} self
    param {int} epochs
    return {*}
    '''    
    def Solver(self, epochs:int):
        self.RandomGenerateChoromoson()
        #self.routeLen = self.initialbestlen
        print("After initialization, the best route cost is: %d" % (self.initialbestlen))
        for epoch in range(epochs):
            self.ElitismSelect()
            self.SimpleCrossOver()
            self.SimpleMutation()
            self.CalculateFitness()
            # print some debugging information
            if epoch % 200 == 0:
                print("Epoch %d: best route length is %d  -------- avearage fitness is %f" % (epoch, self.routeLen, 
                                                                                              sum(self.Fitness) * 1e4 / self.population))
        print("Finish Training, best route is: ", end="")
        print(self.best_route)
        self.chromosomes.clear()
        self.best_route.clear()
        self.Percentage.clear()
        self.Fitness.clear()
        self.offSprings.clear()
        self.routeLen = np.inf
        #pass
        
        