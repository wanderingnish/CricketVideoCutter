import csv
import datetime
import time
import os
import sys
import shutil
from collections import OrderedDict 
from decimal import *
import moviepy.editor
import vertebra

getcontext().traps[FloatOperation] = True

def main():
	curMatchID = 28056
	
	ballDataList = vertebra.readCsvDataFile("data/balls_backups.csv")
	ballDataDict = vertebra.filterDataToDict(ballDataList, "id", "match_id", curMatchID)
	
	commentaryDataList = vertebra.readCsvDataFile("data/commentaries.csv")
	commentaryDataDict = vertebra.filterDataToDict(commentaryDataList, "ball_id", "match_id", curMatchID, raiseErrorOnDuplicatePK = False)

	inningsDataList = vertebra.readCsvDataFile("data/match_innings.csv")
	inningsDataDict = vertebra.filterDataToDict(inningsDataList, "id", "match_id", curMatchID, raiseErrorOnDuplicatePK = False)

	videoFile = "videos/"+str(curMatchID)+".mp4"
	pythonVideoClip = moviepy.editor.VideoFileClip(videoFile)

	makeTimestampFile(ballDataDict, commentaryDataDict, inningsDataDict, curMatchID, pythonVideoClip)
	return 0

def makeTimestampFile(ballDataDict, commentaryDataDict, inningsDataDict, matchID, pythonVideoClip):
	assert len(ballDataDict) == len(commentaryDataDict)
	first = True
	list_of_dicts = list()
	for ballID in ballDataDict:
		FK = int(ballDataDict[ballID]["ball_map_id"])
		if FK not in commentaryDataDict:
			print("\nProblem! Ball data contains entries not in commentary data!\n")
			raise(KeyError)

		currentEntry = dict()
		currentEntry["ball_id"] = ballID
		inningID = int(ballDataDict[ballID]["match_inning_id"])
		currentEntry["innings_number"] = inningsDataDict[inningID]["inning_number"]
		currentEntry["ball_number"] = commentaryDataDict[FK]["ball_number"]
		currentEntry["start_time_seconds"] = None
		currentEntry["end_time_seconds"] = None
		currentEntry["message"] = commentaryDataDict[FK]["message"]
		if first:
			currentEntry["start_time_seconds"] = Decimal("0.0")
			first = False
		list_of_dicts.append(currentEntry)

	lastItem = list_of_dicts[-1]
	lastItem["end_time_seconds"] = pythonVideoClip.duration

	vertebra.writeListOfDicts(list_of_dicts, list_of_dicts[0].keys(), "output/"+str(matchID)+"_timestamps_initial.csv")

if __name__ == '__main__':
	main()