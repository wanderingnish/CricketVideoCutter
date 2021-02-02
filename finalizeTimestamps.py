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


def main():
	curMatchID = 28056
	timestampFile = "output/"+str(curMatchID) + "_timestamps_initial.csv"
	timestampList = vertebra.readCsvDataFile(timestampFile)
	checkTimeStamps(timestampList)
	propogateKnownTimestamps(timestampList)

	ballDataList = vertebra.readCsvDataFile("data/balls_backups.csv")
	ballDataDict = vertebra.filterDataToDict(ballDataList, "id", "match_id", curMatchID)

	fillAllTimestamps(timestampList, ballDataDict)

	vertebra.writeListOfDicts(timestampList, timestampList[0].keys(), "output/"+str(curMatchID)+"_timestamps_final.csv")

def fillAllTimestamps(timestampList, ballDataDict):
	print("\nFilling in all unknown timestamps...")
	assert len(timestampList) == len(ballDataDict)
	blockList = getBlocks(timestampList)

	for curBlockIndices in blockList:
		blockStartIndex = curBlockIndices[0]
		blockEndIndex = curBlockIndices[1]
		assert blockStartIndex >= 0
		assert blockEndIndex >= blockEndIndex
		assert blockEndIndex < len(timestampList)
		timestampBlock = timestampList[blockStartIndex:blockEndIndex+1]
		fillAllTimestampsWithinBlock(timestampBlock, ballDataDict)
	print("Done.")
	
def fillAllTimestampsWithinBlock(timestampBlock, ballDataDict):	
	blockStartTime = Decimal(timestampBlock[0]["start_time_seconds"])
	blockEndTime = Decimal(timestampBlock[-1]["end_time_seconds"])
	if blockEndTime <= blockStartTime:
		for curIndex in range(len(timestampBlock)):
			timestampBlock[curIndex]["start_time_seconds"] = blockStartTime
			timestampBlock[curIndex]["end_time_seconds"] = blockStartTime
	else:
		#Start from latest ball
		curIndex = len(timestampBlock) - 1
		while curIndex > 0:
			curBallID = int(timestampBlock[curIndex]['ball_id'])
			curBallScoredTime = datetime.datetime.strptime(ballDataDict[curBallID]['created_at'], "%Y-%m-%d %H:%M:%S")
			prevBallID = int(timestampBlock[curIndex-1]['ball_id'])
			prevBallScoredTime = datetime.datetime.strptime(ballDataDict[prevBallID]['created_at'], "%Y-%m-%d %H:%M:%S")
			curBallDuration = Decimal((curBallScoredTime - prevBallScoredTime).total_seconds())

			timestampBlock[curIndex]["start_time_seconds"] = Decimal(timestampBlock[curIndex]["end_time_seconds"]) - curBallDuration
			timestampBlock[curIndex-1]["end_time_seconds"] = Decimal(timestampBlock[curIndex]["start_time_seconds"])
			curIndex -= 1

		#No need to handle first ball. It ignores duration and forcibly take all available time at start of block.



def getBlocks(timestampList):
	blockList = list()
	blockStart = -1
	blockEnd = -1
	for i in range(len(timestampList)):
		currentBall = timestampList[i]
		if len(str(currentBall["start_time_seconds"]).strip()) > 0:
			assert blockEnd == -1
			blockStart = i
		if len(str(currentBall["end_time_seconds"]).strip()) > 0:
			assert blockStart >= 0 
			blockEnd = i
			curBlock = [blockStart, blockEnd]
			blockList.append(curBlock)
			blockStart = -1
			blockEnd = -1
	return blockList


def propogateKnownTimestamps(timestampList):
	assert len(str(timestampList[-1]["end_time_seconds"]))>0
	for i in range(len(timestampList) - 1):
		currentBall = timestampList[i]
		nextBall = timestampList[i+1]
		if len(str(nextBall["start_time_seconds"]).strip()) > 0 and len(str(currentBall["end_time_seconds"]).strip()) == 0:
			currentBall["end_time_seconds"] = nextBall["start_time_seconds"]
		elif len(str(nextBall["start_time_seconds"]).strip()) == 0 and len(str(currentBall["end_time_seconds"]).strip()) > 0:
			nextBall["start_time_seconds"] = currentBall["end_time_seconds"]


def videoTimeStamps(ballDataDict, videoClip, video_startTime = "00:00:00", video_endTime = None, firstBall_endTime = "00:00:00"):
	print("\nFinding start and end times of all balls...")
	if video_endTime is None: #Then default to total duration of video clip
		video_endTime = time.strftime('%H:%M:%S', time.gmtime(videoClip.duration))

	timeStampDict = dict()
	prevBallID = None

	for ballID in ballDataDict:
		if prevBallID is None:
			ball_start = video_startTime
			ball_end = firstBall_endTime
		else:
			ball_start = timeStampDict[prevBallID]["endtime"]
			curBallScoredTime = datetime.datetime.strptime(ballDataDict[ballID]['created_at'], "%Y-%m-%d %H:%M:%S")
			prevBallScoredTime = datetime.datetime.strptime(ballDataDict[prevBallID]['created_at'], "%Y-%m-%d %H:%M:%S")

			ball_duration = (curBallScoredTime - prevBallScoredTime).total_seconds()
			ball_end_asDateTime = datetime.datetime.strptime(ball_start,"%H:%M:%S") + datetime.timedelta(seconds = ball_duration)
			ball_end = datetime.datetime.strftime(ball_end_asDateTime, "%H:%M:%S")

		timeStampDict[ballID] = {
			"starttime":ball_start,
			"endtime":ball_end,	
		}
		prevBallID = ballID
	print("Done.")
	return timeStampDict

def checkTimeStamps(timestampList):
	print("\nChecking initial time stamps...")
	latestTime = Decimal("-1")
	for currentBall in timestampList:
		currentTimeString = str(currentBall["start_time_seconds"]).strip()
		if len(currentTimeString) > 0:
			currentTimeStamp = Decimal(currentTimeString)
			if not currentTimeStamp >= latestTime:
				print("\nProblem! Time stamp data has conflicts (timestamps are not in ascending order)\n")
				raise(AssertionError)
			latestTime = currentTimeStamp
		currentTimeString = str(currentBall["end_time_seconds"]).strip()
		if len(currentTimeString) > 0:
			currentTimeStamp = Decimal(currentTimeString)
			if not currentTimeStamp >= latestTime:
				print("\nProblem! Time stamp data has conflicts (timestamps are not in ascending order)\n")
				raise(AssertionError)
			latestTime = currentTimeStamp
	print("Check Complete.")

if __name__ == '__main__':
	main()