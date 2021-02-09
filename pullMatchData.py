import csv
import datetime
import time
import os
import sys
import shutil
from collections import OrderedDict 
from decimal import *
import vertebra
import requests

getcontext().traps[FloatOperation] = True

def main():
	curMatchID = 28056
	tables = ['matches',  'balls_backups', 'balls', 'commentaries', 'match_innings', 'batting_player_scores', 'bowling_player_scores', 'match_current_players', 'match_officials', 'tournaments']
	for table in tables:
		url = "https://www.funngage.com/api/"+str(curMatchID)+"/"+table+"/csv"
		response = requests.get(url)
		if response.status_code != 200:
			print("\nError! Could not load data from: "+url)
			raise(ValueError)
		else:
			print("\nLoading data from "+url)
			filepath = "data/"+table + ".csv"
			f = open(filepath, "w")
			f.write(response.text)
			f.close()
			print("Created file:"+filepath)
		response.close()

	
if __name__ == '__main__':
	main()