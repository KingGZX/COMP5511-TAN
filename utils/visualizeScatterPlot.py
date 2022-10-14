'''
author: Zhexuan Gu
Date: 2022-09-27 16:28:36
LastEditTime: 2022-09-28 11:06:21
FilePath: /Assignment 1 2/visualizeScatterPlot.py
Description: Please implement
'''
import matplotlib.pyplot as plt
import os

def drawScatterPlot(Xcoords, Ycoords):
    plt.scatter(Xcoords, Ycoords, marker='*')
    plt.title("Initial Scatter Picture")
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

def drawLinePlot(Xcoords, Ycoords, save:bool):
    plt.plot(Xcoords, Ycoords)
    plt.title("Best Route")
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    if save:
        if os.path.exists("./SaveFigs") == False:
            os.mkdir('SaveFigs')
        num = len(os.listdir('./SaveFigs'))
        plt.savefig("./SaveFigs/" + str(num) + ".png");
    plt.show()