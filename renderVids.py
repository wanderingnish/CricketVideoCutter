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
	timestampFile = "output/"+str(curMatchID) + "_timestamps_final.csv"
	timestampList = vertebra.readCsvDataFile(timestampFile)

	videoFile = "videos/"+str(curMatchID)+".mp4"
	fullClip = moviepy.editor.VideoFileClip(videoFile)

	#Delete video folder if it already exists
	matchFolder = 'output/'+str(curMatchID)
	if os.path.isdir(matchFolder):
		print("\nWarning: "+matchFolder+" already exists and will be deleted if you continue.")
		input("Press Enter to continue. ")
		shutil.rmtree('output/'+str(curMatchID))
	os.mkdir(matchFolder)

	timestampList.reverse()
	for rowDict in timestampList:
		ballID = rowDict["ball_id"]
		inningNum = rowDict["innings_number"]
		inningFolder = matchFolder+"/"+str(inningNum)
		if not os.path.isdir(inningFolder):
			os.mkdir(inningFolder)

		overAndBallArray = str(rowDict["ball_number"]).split(".")
		overNum = str(overAndBallArray[0])
		if len(overAndBallArray) > 1:
			ballNum = str(overAndBallArray[1])
		else:
			ballNum = '0'

		ballStart = rowDict['start_time_seconds']
		ballEnd = rowDict['end_time_seconds']
		if ballStart < ballEnd:
			ballClip = fullClip.subclip(ballStart, ballEnd)
			clipFileName = overNum+"_"+ballNum+"_"+str(ballID)+".mp4"
			ballClip.write_videofile(inningFolder +"/"+ clipFileName)


if __name__ == '__main__':
	main()