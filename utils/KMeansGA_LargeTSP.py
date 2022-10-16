'''
author: Zhexuan Gu
Date: 2022-10-10 00:00:51
LastEditTime: 2022-10-11 20:42:55
FilePath: /Assignment 1 2/utils/KMeansGA_LargeTSP.py
Description: Question3 of Assignment1
'''
import numpy as np
import random
from utils.GeneticAlgorithm import SimpleTSPGA

class GAWithCluster(SimpleTSPGA):
    def __init__(self, customernum: int, population: int, distancematrix, mutationrate: float, crossoverrate: float, center:int, xcoords, ycoords) -> None:
        super().__init__(customernum, population, distancematrix, mutationrate, crossoverrate)
        self.clusterCenternum = center
        self.Xcoordinations = xcoords   
        self.Ycoordinations = ycoords
        self.ClusterBestRoute = []
        self.ClusterBestRouteLen = []
        self.Centers = []
        self.Labels = [i for i in range(len(self.Xcoordinations))]      # to record which cluster each customer belongs to
    
    def RandomGenerateChoromoson(self, clusterIndex)->bool:
        # generate chromosomes for each cluster, so override the original randomgenerator method
        indexes = np.where(np.array(self.Labels) == clusterIndex)
        print(indexes)
        for i in range(self.population):
            if len(indexes[0]) == 0:
                self.clusterCenternum -= 1
                return False
            if len(indexes[0]) == 1:
                self.ClusterBestRoute.append(list(indexes[0]))
                self.ClusterBestRouteLen.append(0)
                return False
            chromosome = list(np.random.permutation(indexes)[0])
            cost = self.TSPCost(chromosome)
            fitness = self.FitnessFunction(cost)
            index = self.FitnessInsertion(fitness)
            self.chromosomes.insert(index, chromosome)
            self.initialbestlen = min(self.initialbestlen, cost)
        return True
    
    def ClustetrCenterGenerater(self, fMin, fMax):
        return fMin + random.random() * (fMax - fMin)
    
    def Clustering(self, index):
        label = 0
        mmin = np.inf
        for i in range(self.clusterCenternum):
            x_diff = self.Xcoordinations[index] - self.Centers[i][0]
            y_diff = self.Ycoordinations[index] - self.Centers[i][1]
            cost = np.sqrt(np.square(x_diff) + np.square(y_diff))
            if cost < mmin:
                mmin = cost 
                label = i
        self.Labels[index] = label
    
    def ResetClusterCenters(self):
        labels = np.array(self.Labels)
        for i in range(self.clusterCenternum):
            index = np.where(labels == i)
            # calculating the mean of these points and set it to be the new center of the corresponding cluster
            newCluterCenterX = np.mean(np.array(self.Xcoordinations)[index])
            newCluterCenterY = np.mean(np.array(self.Ycoordinations)[index])
            self.Centers[i][0], self.Centers[i][1] = newCluterCenterX, newCluterCenterY
            
            
    '''
    description: cluster all customers
    event: 
    param {*} self
    return {*}
    '''    
    def KMeans(self):
        # randomly generate self.clusterCenter centers and divide all customers to different centers
        minX, maxX = min(self.Xcoordinations), max(self.Xcoordinations)
        minY, maxY = min(self.Ycoordinations), max(self.Ycoordinations)
        for i in range(self.clusterCenternum):
            self.Centers.append([self.ClustetrCenterGenerater(minX, maxX), self.ClustetrCenterGenerater(minY, maxY)])
        # iterating until centers do not change anymore
        # the criterion is too strict, I choose a relatively mild condition
        customerNum = len(self.Xcoordinations)
        iterations = 0
        while iterations <= 200:
            for i in range(customerNum):
                self.Clustering(i)
            self.ResetClusterCenters()
            iterations += 1
    
    def FindNearestTwoVertices(self, index:int):
        v1, v2 = 0, 0
        index1, index2 = 0, 0
        mminLen = np.inf
        for in1, vertice1 in enumerate(self.ClusterBestRoute[index]):
            for in2, vertice2 in enumerate(self.ClusterBestRoute[index + 1]):
                if self.diatance_matrix[vertice1, vertice2] < mminLen:
                    mminLen = self.diatance_matrix[vertice1, vertice2]
                    v1, v2 = vertice1, vertice2
                    index1, index2 = in1, in2
        return v1, v2, index1, index2
    
    def ChooseDeleteAndInsert(self, v1:int, v2:int, index:int, index1:int, index2:int):
        route1Len = len(self.ClusterBestRoute[index])
        route2Len = len(self.ClusterBestRoute[index + 1])
        v1Left = self.ClusterBestRoute[index][(index1 + route1Len - 1) % route1Len]
        v1right = self.ClusterBestRoute[index][(index1 + 1) % route1Len]
        v2Left = self.ClusterBestRoute[index + 1][(index2 + route2Len - 1) % route2Len]
        v2Right = self.ClusterBestRoute[index + 1][(index2 + 1) % route2Len]
        cost = np.inf
        dele1, dele2, insr1, insr2 = 0, 0, 0, 0
        for edge1 in [v1Left, v1right]:
            for edge2 in [v2Left, v2Right]:
                sign1, sign2 = 1, 1
                '''
                % sign = 1 means righthand side node
                '''
                if edge1 == v1Left:
                    sign1 = -1
                if edge2 == v2Left:
                    sign2 = -1
                len1 = self.diatance_matrix[v1, v2] + self.diatance_matrix[edge1, edge2] - self.diatance_matrix[v1, edge1] - self.diatance_matrix[v2, edge2]
                len2 = self.diatance_matrix[v1, edge2] + self.diatance_matrix[edge1, v2] - self.diatance_matrix[v1, edge1] - self.diatance_matrix[v2, edge2]
                if len1 < len2 and len1 < cost:
                    cost = len1
                    dele1, dele2, insr1, insr2 = sign1, sign2, v2, sign2
                if len2 < len1 and len2 < cost:
                    cost = len1
                    dele1, dele2, insr1, insr2 = sign1, sign2, sign2, v2
        print("Merge cost is: %f" % (cost))
        self.routeLen += cost
        '''
        % dele1 is the direct node linked to v1 that the edge between these two nodes will be deleted
        % dele2 same as above
        
        % insr1 is the node that chosen from another cluster and link v1 to this node
        % same but link the dele1 to the node
        '''
        return dele1, dele2, insr1, insr2
    
    def MergeNodes(self, index:int, dele1:int, dele2:int, insr1:int, insr2:int, index1:int, index2:int):
        '''
        # debug information
        print("Merging Cluster %d and %d, link nodes are %d, %d" % (index, index + 1, index1, index2))
        print("first route is:", end="")
        print(self.ClusterBestRoute[index])
        print("second route is:", end="")
        print(self.ClusterBestRoute[index + 1])
        print("deleting %d, %d respectively" % (dele1, dele2))
        print("inserting %d, %d respectively" % (insr1, insr2))
        '''
        route1Len, route2Len = len(self.ClusterBestRoute[index]), len(self.ClusterBestRoute[index + 1])
        route1Len = len(self.ClusterBestRoute[index])
        route2Len = len(self.ClusterBestRoute[index + 1])
        v1Left = (index1 + route1Len - 1) % route1Len
        v1right = (index1 + 1) % route1Len
        v2Left = (index2 + route2Len - 1) % route2Len
        v2Right = (index2 + 1) % route2Len
        route = []
        if route1Len == 1 or route2Len == 1:
            if route1Len == 1:
                if dele2 == 1:
                    route = self.ClusterBestRoute[index + 1].insert(index2 + 1)
                else:
                    route = self.ClusterBestRoute[index + 1].insert(index2)
            else:
                if dele1 == 1:
                    route = self.ClusterBestRoute[index].insert(index1 + 1)
                else:
                    route = self.ClusterBestRoute[index].insert(index1)
        else:
            if dele1 == 1:
                route += self.ClusterBestRoute[index][0:index1 + 1]
                if insr1 == 1:
                    route += self.ClusterBestRoute[index + 1][v2Right:]
                    route += self.ClusterBestRoute[index + 1][0:v2Right]
                elif insr1 == -1:
                    temp = self.ClusterBestRoute[index + 1][0:v2Left + 1]
                    temp.reverse()
                    route += temp
                    temp = self.ClusterBestRoute[index + 1][v2Left + 1:]
                    temp.reverse()
                    route += temp
                else:
                    if dele2 == 1:
                        temp = self.ClusterBestRoute[index + 1][0:index2 + 1]
                        temp.reverse()
                        route += temp
                        temp = self.ClusterBestRoute[index + 1][index2 + 1:]
                        temp.reverse()
                        route += temp
                    else:
                        route += self.ClusterBestRoute[index + 1][index2:]
                        route += self.ClusterBestRoute[index + 1][0:index2]
                route += self.ClusterBestRoute[index][index1 + 1:]
            else:
                route += self.ClusterBestRoute[index][0:v1Left + 1]
                if insr1 == 1:
                    route += self.ClusterBestRoute[index + 1][v2Right:]
                    route += self.ClusterBestRoute[index + 1][0:v2Right]
                elif insr1 == -1:
                    temp = self.ClusterBestRoute[index + 1][0:v2Left + 1]
                    temp.reverse()
                    route += temp
                    temp = self.ClusterBestRoute[index + 1][v2Left + 1:]
                    temp.reverse()
                    route += temp
                else:
                    if dele2 == 1:
                        route += self.ClusterBestRoute[index + 1][v2Right:]
                        route += self.ClusterBestRoute[index + 1][0:v2Right]
                    else:
                        temp = self.ClusterBestRoute[index + 1][0:v2Left + 1]
                        temp.reverse()
                        route += temp
                        temp = self.ClusterBestRoute[index + 1][v2Left + 1:]
                        temp.reverse()
                        route += temp
                route += self.ClusterBestRoute[index][v1Left + 1:]  
        self.ClusterBestRoute[index + 1] = route
                
    
    '''
    description: combine all the circles
    event: 
    param {*} self
    return {*}
    '''    
    def CombineHamiltonCircle(self):
        # 1.find 2 nearest vertices from two clusters
        for i in range(self.clusterCenternum - 1):
            self.routeLen += self.ClusterBestRouteLen[i]
            v1, v2, index1, index2 = self.FindNearestTwoVertices(i)
            dele1, dele2, insr1, insr2 = self.ChooseDeleteAndInsert(v1, v2, i, index1, index2)
            # Link the node and merge the circle
            self.MergeNodes(i, dele1, dele2, insr1, insr2, index1, index2)
            #self.ClusterBestRoute[i + 1] += self.ClusterBestRoute[i]
            print("current route:", end="")
            print(self.ClusterBestRoute[i + 1])
        self.routeLen += self.ClusterBestRouteLen[self.clusterCenternum - 1]
            
    def Solver(self, epochs: int):
        # I'm not intend to write a parallel trainning programme
        # therefore, I choose to train every Cluster and finally combine
        self.KMeans()
        for i in range(self.clusterCenternum):
            flag = self.RandomGenerateChoromoson(i)
            if flag == True:
                print("Cluster %d, After initialization, the best route cost is: %d" % (i, self.initialbestlen))
                for epoch in range(epochs):
                    self.ElitismSelect()
                    self.SimpleCrossOver()
                    self.SimpleMutation()
                    self.CalculateFitness()
                    # print some debugging information
                    if epoch % 200 == 0:
                        print("Cluster %d, Epoch %d: best route length is %d  -------- avearage fitness is %f" % (i, epoch, self.routeLen, 
                                                                                                    sum(self.Fitness) * 1e4 / self.population))
                self.ClusterBestRoute.append(self.best_route)
                print(self.best_route)
                self.ClusterBestRouteLen.append(self.routeLen)
                self.chromosomes.clear()
                self.Percentage.clear()
                self.Fitness.clear()
            self.routeLen = np.inf
            self.initialbestlen = np.inf
        self.routeLen = 0
        self.CombineHamiltonCircle()
        print("After combining all clusters, the optimal value is: %d" % (self.routeLen))
        print("Best route is: ", end="")
        print(self.ClusterBestRoute[self.clusterCenternum - 1])
        self.chromosomes.clear()
        self.Percentage.clear()
        self.Fitness.clear()
        self.routeLen = np.inf
        self.ClusterBestRoute.clear()
        self.ClusterBestRouteLen.clear()
        self.Centers.clear()
        self.Labels.clear()
        self.best_route.clear()