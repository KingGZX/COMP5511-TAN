'''
author: Zhexuan Gu
Date: 2022-09-27 16:28:36
LastEditTime: 2022-10-22 17:35:00
FilePath: /Assignment 1 2/utils/visualizeScatterPlot.py
Description: Please implement
'''
from cmath import cos
from re import X
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.interpolate import make_interp_spline

'''
description: draw initial scatter plot
event: 
param {*} Xcoords
param {*} Ycoords
return {*}
'''
def drawScatterPlot(Xcoords, Ycoords):
    plt.scatter(Xcoords, Ycoords, marker='*')
    plt.title("Initial Scatter Picture")
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

def drawLinePlot(Xcoords, Ycoords, save:bool):
    plt.plot(Xcoords, Ycoords)
    plt.title("Route")
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    if save:
        if os.path.exists("./SaveFigs") == False:
            os.mkdir('SaveFigs')
        num = len(os.listdir('./SaveFigs'))
        plt.savefig("./SaveFigs/" + str(num) + ".png");
    plt.show()
    
def drawFitness(logepoch, logfitness):
    plt.plot(logepoch, logfitness)
    plt.title("Fitness Verification")
    plt.xlabel('Epoch(s)')
    plt.ylabel('Average Fitness(* 1e4)')
    plt.show()
    
def drawRoute(route, Xcoords, Ycoords, cost):
    Xcoords = np.array(Xcoords)[route]
    Ycoords = np.array(Ycoords)[route]
    plt.plot(Xcoords, Ycoords)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title("Best Route, cost is %f" % (cost))
    for i in range(len(Xcoords)):
        plt.text(Xcoords[i], Ycoords[i], route[i], ha='center', va='bottom', fontsize=10)
    plt.show()
    
def drawClusters(xcoords, ycoords, labels, centers):
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'yellow', 'black', 'brown', 'wheat', 'azure']
    clusters = len(centers)
    for i in range(clusters):
        plt.scatter(centers[i][0], centers[i][1], marker="x", c=colors[i])
    for i in range(len(labels)):
        plt.scatter(xcoords[i], ycoords[i], c=colors[labels[i]])
        plt.text(xcoords[i], ycoords[i], str(i))
    plt.show()
    
def drawParetoFront(costs, profits):
    Indexes = sorted(range(len(costs)), key = lambda k: costs[k])
    costs = list(np.array(costs)[Indexes])
    profits = list(np.array(profits)[Indexes])
    length = len(profits)
    i = 1
    while i < length:
        if profits[i] < profits[i - 1]:
            profits.pop(i)
            costs.pop(i)
            length -= 1
            i -= 1
        i += 1
        
    plt.scatter(costs, profits, c="red")
    plt.xlabel('route cost')
    plt.ylabel('route profit')
    plt.title("Pareto Front")
    plt.show()
    
    """
    costs = np.array(costs)
    profits = np.array(profits)
    X_Y_Spline = make_interp_spline(costs, profits)
    # Returns evenly spaced numbers
    # over a specified interval.
    X_ = np.linspace(costs.min(), costs.max(), 500)
    Y_ = X_Y_Spline(X_)
    plt.plot(X_, Y_)
    plt.xlabel('route cost')
    plt.ylabel('route profit')
    plt.title("Pareto Front")
    plt.show()
    """

def drawPareto3D(costs, profits, vtime):
    Indexes = sorted(range(len(costs)), key = lambda k: costs[k])
    costs = list(np.array(costs)[Indexes])
    profits = list(np.array(profits)[Indexes])
    vtime = list(np.array(vtime)[Indexes])
    length = len(profits)
    i = 1
    while i < length:
        if (profits[i] < profits[i - 1] and vtime[i] >= vtime[i - 1]) or (profits[i] <= profits[i - 1] and vtime[i] > vtime[i - 1]):
            profits.pop(i)
            costs.pop(i)
            vtime.pop(i)
            length -= 1
            i -= 1
        i += 1
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    ax.scatter(costs, profits, vtime, c='red')
    ax.set_xlabel('Route Cost')
    ax.set_ylabel('Route Profit')
    ax.set_zlabel('Route Violation Time')
    pass