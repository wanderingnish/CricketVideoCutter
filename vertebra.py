import csv
import datetime
import time
import os
import sys
import shutil
from collections import OrderedDict 


def filterDataToDict(dataList, pk_name, filterColName, filterValueInt, raiseErrorOnDuplicatePK = True):
	print("\nFiltering by "+filterColName+" == "+str(filterValueInt)+"...")
	dataDict = OrderedDict() 
	for rowDict in dataList:
		if int(rowDict[filterColName]) == int(filterValueInt):
			pk = int(rowDict[pk_name])
			if raiseErrorOnDuplicatePK:
				assert pk not in dataDict
				dataDict[pk] = rowDict
			elif pk not in rowDict:
				dataDict[pk] = rowDict
	print("Done.")
	return dataDict

def readCsvDataFile(filepath):
	if os.path.isfile(filepath):
		print("\nLoading data from "+filepath+"...")
		with open(filepath, encoding = 'utf-8') as csvfile:
			readCSV = csv.DictReader(csvfile, delimiter = ",", restval = "")
			'''if readCSV.fieldnames != expectedHeader:
				print("\nColumn names have changed in file!")
				raise(ValueError)'''
			list_of_dicts = list()
			for rowdict in readCSV:
				list_of_dicts.append(rowdict)
		print("Loaded.")
		return list_of_dicts
	else:
		print("\nFile not found - "+filepath)
		raise(FileNotFoundError)

def writeListOfDicts(list_of_dicts, headerRow, filepath):
	print("\nWriting data to " + filepath + "...")
	if os.path.isfile(filepath):
		print("\nWARNING: "+filepath+" already exists and will be overwritten. \nMAKE SURE THIS FILE IS NOT OPEN.")
		input("Press Enter to continue. ")
	pen = csv.DictWriter(open(filepath, 'w', encoding = 'utf-8'), delimiter = ',', lineterminator = '\n', fieldnames = headerRow, restval = "", extrasaction = 'ignore')
	pen.writeheader()
	for curRowDict in list_of_dicts:
		pen.writerow(curRowDict)
	print('Written new file: '+filepath)