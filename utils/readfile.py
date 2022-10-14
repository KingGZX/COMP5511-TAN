'''
author: Zhexuan Gu
Date: 2022-09-27 14:21:26
LastEditTime: 2022-10-08 15:17:03
FilePath: /Assignment 1 2/utils/readfile.py
Description: from given dataset, parse it and create a prettier dataset which can be parsed by read_csv api
'''
# As the .txt file is not orgniszed well, 
# so I can't use read_csv api offered by pandas library to parse correctly

from curses.ascii import isspace
import os

'''
description: the main purpose is to parse the digit numbers from a line which is a string
event: 
param {str} line
return {*}
'''
def translate_string_to_numbers(line:str):
    numberlist = []
    i = 0
    while i < len(line):
        if line[i].isspace() == False:
            numberstr = ""
            while i < len(line) and (line[i].isdigit() or (i - 1 >= 0 and line[i - 1].isdigit() and line[i] == ".")):
                numberstr += line[i]
                i += 1
            if numberstr != "":
                numberlist.append(numberstr)
        i += 1
    return numberlist

'''
description: read all line in old dataset file, and parse the line, then write into the new dataset file
event: 
param {str} filepath
return {*}
'''
def write_data_into_new_file(filepath:str):
    with open(filepath, 'w') as newdataset:
        with open('./Code and Dataset/TSPTW_dataset.txt', 'r') as olddataset:
            lines = olddataset.readlines()
            for line in lines:
                numberlist = translate_string_to_numbers(line)
                if(len(numberlist) > 0):
                    cnt = 0
                    for number in numberlist:
                        newdataset.write(number)
                        cnt += 1
                        if cnt < len(numberlist):
                            newdataset.write(',')
                    newdataset.write("\r\n")
                    numberlist.clear()

'''
description: create a new dataset file, whose name is filepath, the input parameter
event: 
param {str} filepath
return {*}
'''
def create_nice_dataset(filepath:str):
    #filepath = './Code and Dataset/nicer_TSP_dataset_gzx.txt'
    if os.path.exists(filepath) == False:
        # since mknod api on MacOS needs privilege, use the following code to create a file
        open(filepath, 'a').close()
    write_data_into_new_file(filepath)