# -*- coding: UTF-8 -*-
import json

inputFile = open("parsedData.tsv","r")
targetFile = open("epAuthorsNumSubset.csv","w")
lineNum = 1
dictionary = {}

for line in inputFile:
    if lineNum == 1:
        targetFile.write("name,size\n")
    else:
        lineList = line.strip("\n")
        lineList = lineList.strip("\r")
        lineList = lineList.split("\t")
        epAuthor = lineList[2].strip(".")
        epAuthorListName = epAuthor.split(' ')
        if len(epAuthorListName) == 2:
            epAuthorLastName = epAuthorListName[1]
            try:
                dictionary[epAuthorLastName]+=1
            except KeyError:
                dictionary[epAuthorLastName]=1
        else:
            try:
                dictionary[epAuthor]+=1
            except KeyError:
                dictionary[epAuthor] = 1
    lineNum+=1

dictList = dictionary.items()
for pair in dictList:
    if (pair[1]>2):
        targetFile.write(str(pair[0])+","+str(pair[1])+"\n")
with open('epAuthorsNumSubset.json', 'w') as outfile:
    json.dump(dictList, outfile)
