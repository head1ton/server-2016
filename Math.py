
# Math.py
import utils
import DataModel
import firebaseCommunicator
import math
import numpy as np
import dmutils
import scipy as sp
from operator import attrgetter
import scipy.stats as stats
import sys, traceback
import pdb
import CacheModel as cache


class Calculator(object):
	"""docstring for Calculator"""
	def __init__(self, competition):
		super(Calculator, self).__init__()
		self.comp = competition
		self.categories = ['a', 'b', 'c', 'd', 'e']
		self.ourTeamNum = 1678
		self.defenseList = ['pc', 'cdf', 'mt', 'rt', 'rw', 'lb', 'rp', 'sp', 'db']
		self.defenseDictionary = {'a' : ['pc', 'cdf'],
			'b' : ['mt', 'rp'],
			'c' : ['sp', 'db'],
			'd' : ['rw', 'rt'],
			'e' : ['lb']
		}
		self.matches = self.comp.matches
		self.TIMDs = self.comp.TIMDs
		self.cachedTeamDatas = {}
		self.averageTeam = DataModel.Team()
		self.averageTeam.number = -1
		[utils.setDictionaryValue(self.cachedTeamDatas, team.number, cache.CachedTeamData(**{'teamNumber' : team.number})) for team in self.comp.teams]


	def bToI(self, boolean):
		if boolean: return 1
		if not boolean: return 0

	def getDefenseRetrievalFunctionForDefense(self, retrievalFunction, defenseKey):
		return lambda t: retrievalFunction(t)[defenseKey]
		return self.getDefenseRetrievalFunctionForCategoryAndDefenseForRetrievalFunction(retrievalFunction, defenseKey)

	def getDefenseRetrievalFunctions(self, retrievalFunction):
		return map(lambda dKey: self.getDefenseRetrievalFunctionForDefense(retrievalFunction, dKey), self.defenseList)

	def getValuedDefenseRetrievalFunctionsForTeam(self, team, retrievalFunction):
		return filter(lambda f: f(team) != None, self.getDefenseRetrievalFunctions(retrievalFunction))

	# Team utility functions
	def getTeamForNumber(self, teamNumber):
		return [team for team in self.comp.teams if team.number == teamNumber][0]

	def teamsWithCalculatedData(self):
		return filter(lambda t: self.calculatedDataHasValues(t.calculatedData), self.comp.teams)

	def getMatchesForTeam(self, team):
		return [match for match in self.matches if self.teamInMatch(team, match)]

	def getCompletedMatchesForTeam(self, team):
		return filter(self.matchIsCompleted, self.getMatchesForTeam(team))

	def getPlayedTIMDsForTeam(self, team):
		return [timd for timd in self.getTIMDsForTeamNumber(team.number) if self.timdIsPlayed(timd)]

	def teamsWithMatchesCompleted(self):
		return [team for team in self.comp.teams if len(self.getCompletedTIMDsForTeam(team)) > 0]

	def getColorFromTeamAndMatch(self, team, match):
		blue = map(getTeamForNumber, match.blueAllianceTeamNumbers)
		red = map(getTeamForNumber, match.redAllianceTeamNumbers)
		return blue if team in blue else red

	def getOppColorFromTeamAndMatch(self, team, match):
		blue = map(getTeamForNumber, match.blueAllianceTeamNumbers)
		red = map(getTeamForNumber, match.redAllianceTeamNumbers)
		return blue if team in red else red

	def getAllTeamMatchAlliances(self, team):
		return [self.getColorFromTeamAndMatch(team, match) for match in self.getCompletedMatchesForTeam(team)]

	def getAllTeamOppositionAlliances(self, team):
		return [self.getOppColorFromTeamAndMatch(team, match) for match in self.getCompletedMatchesForTeam(team)]

	# Match utility functions
	def getMatchForNumber(self, matchNumber):
		return [match for match in self.matches if match.number == matchNumber][0]

	def teamsInMatch(self, match):
		teamNumbersInMatch = match.redAllianceTeamNumbers
		teamNumbersInMatch.extend(match.blueAllianceTeamNumbers)
		return [self.getTeamForNumber(teamNumber) for teamNumber in teamNumbersInMatch]

	def teamInMatch(self, team, match):
		return team in self.teamsInMatch(match)

	def matchIsPlayed(self, match):
		return match.redScore != None or match.blueScore != None

	def matchIsCompleted(self, match):
		return len(self.getCompletedTIMDsForMatchNumber(match.number)) == 6

	def matchTIMDsForTeamAlliance(self, team, match):
		if team.number in match.blueAllianceTeamNumbers:
			return map(self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number), match.blueAllianceTeamNumbers)
		if team.number in match.redAllianceTeamNumbers:
			return map(self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number), match.redAllianceTeamNumbers)

	def getAllTIMDsForMatch(self, match):
		return [timd for timd in self.comp.TIMDs if timd.matchNumber == match.number]

	def matchHasAllTeams(self, match):
		return len(self.getAllTIMDsForMatch(match)) == 6		

	def matchesThatHaveBeenPlayed(self):
		return [match for match in self.matches if self.matchHasAllTeams(match)]

	def matchesThatHaveBeenCompleted(self):
		return [match for match in self.matches if self.matchIsCompleted(match)]

	# TIMD utility functions
	def getTIMDsForTeamNumber(self, teamNumber):
		return [timd for timd in self.comp.TIMDs if timd.teamNumber == teamNumber]

	def getCompletedTIMDsForTeamNumber(self, teamNumber):
		return filter(self.timdIsCompleted, self.getTIMDsForTeamNumber(teamNumber))

	def getCompletedTIMDsForTeam(self, team):
		return self.getCompletedTIMDsForTeamNumber(team.number)

	def getPlayedTIMDsForTeamNumber(self, teamNumber):
		return filter(self.timdIsPlayed, self.getTIMDsForTeamNumber(teamNumber))

	def getTIMDsForMatchNumber(self, matchNumber):
		return [timd for timd in self.comp.TIMDs if timd.matchNumber == matchNumber]

	def getCompletedTIMDsForMatchNumber(self, matchNumber):
		return filter(self.timdIsCompleted, self.getTIMDsForMatchNumber(matchNumber))

	def getTIMDForTeamNumberAndMatchNumber(self, teamNumber, matchNumber):
		return [timd for timd in self.getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]	

	def getCompletedTIMDsInCompetition(self):
		return [timd for timd in self.comp.TIMDs if self.timdIsCompleted(timd)]

	def calculatedDataHasValues(self, calculatedData):
		hasValues = False 
		for key, value in utils.makeDictFromObject(calculatedData).items():
			if value != None and not 'Defense' in key and not 'defense' in key and not 'second' in key and not "ballsIntakedAuto" in key:
				hasValues = True
		return hasValues

	def timdIsPlayed(self, timd):
		isPlayed = False 
		for key, value in utils.makeDictFromTIMD(timd).items():
			if value != None:
				isPlayed = True
		return isPlayed

	def teamsAreOnSameAllianceInMatch(self, team1, team2, match):
			areInSameMatch = False
			alliances = [match.redAllianceTeamNumbers, match.blueAllianceTeamNumbers]
			for alliance in alliances:
				if team1.number in alliance and team2.number in alliance:
					areInSameMatch = True
			return areInSameMatch

	exceptedKeys = ['calculatedData', 'ballsIntakedAuto', 'superNotes']

	def timdIsCompleted(self, timd):
		isCompleted = True 
		for key, value in utils.makeDictFromTIMD(timd).items():
			if key not in self.exceptedKeys and value == None:
				isCompleted = False
		return isCompleted

	# Calculated Team Data
	def getAverageForDataFunctionForTeam(self, team, dataFunction):
		return np.mean(map(dataFunction, self.getCompletedTIMDsForTeam(team)))

	def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
		return np.std(map(dataFunction, self.getCompletedTIMDsForTeam(team)))	

	def averageTIMDObjectOverMatches(self, team, key, coefficient = 1):
		return np.mean([utils.makeDictFromTIMD(timd)[key] for timd in self.getCompletedTIMDsForTeam(team)])

	def getTIMDHighShotAccuracyTele(self, timd):
		return timd.numHighShotsMadeTele / (timd.numHighShotsMadeTele + timd.numHighShotsMissedTele) if (timd.numHighShotsMadeTele+ timd.numHighShotsMissedTele) > 0 else 0

	def getTIMDHighShotAccuracyAuto(self, timd):
		return timd.numHighShotsMadeAuto / (timd.numHighShotsMadeAuto + timd.numHighShotsMissedAuto) if (timd.numHighShotsMadeAuto + timd.numHighShotsMissedAuto) > 0 else 0

	def getTIMDLowShotAccuracyTele(self, timd):
		return timd.numLowShotsMadeTele / (timd.numLowShotsMadeTele + timd.numLowShotsMissedTele) if (timd.numLowShotsMadeTele + timd.numLowShotsMissedTele) > 0 else 0

	def getTIMDLowShotAccuracyAuto(self, timd):
		return timd.numLowShotsMadeAuto / (timd.numLowShotsMadeAuto + timd.numLowShotsMissedAuto) if (timd.numLowShotsMadeAuto + timd.numLowShotsMissedAuto) > 0 else 0

	def flattenDictionary(self, dictionary):
		flattenedDict = {}
		for categoryDict in dictionary.values():
			for defense, dictionary in categoryDict.items():
				flattenedDict[defense] = dictionary
		return flattenedDict


	def makeArrayOfDictionaries(self, team, key): 
 		timds = self.getCompletedTIMDsForTeam(team)
 		arrayOfDictionaries = [] 
 		for timd in timds:
 			dictionary = utils.makeDictFromTIMD(timd)[key]
 			dictionary = self.flattenDictionary(dictionary)
 			for d in dictionary:
 				if dictionary[d] > None:
 					arrayOfDictionaries.append(dictionary) 
  		return arrayOfDictionaries 


 	def averageDictionaries(self, array):
 		subOutputDict = {}
 		outputDict = {'a' : {}, 'b' : {}, 'c' : {}, 'd': {}, 'e' : {}}
 		#print array
 		for dic in array:
			for key, value in dic.items():
				avg = 0.0
				#print "val " + str(value)
				for dictionary in array:
					# print key
					if key in dictionary.keys():
						avg += len(dictionary[key]) - 1
					#print "avg for " + str(key) + " is " + str(avg)
				avg /= len(array) 
				subOutputDict[key] = avg
		for key in subOutputDict:
			if key == 'cdf' or key == 'pc':
				outputDict['a'][key] = subOutputDict[key]
			elif key == 'mt' or key == 'rp':
				outputDict['b'][key] = subOutputDict[key]
			elif key == 'sp' or key == 'db':
				outputDict['c'][key] = subOutputDict[key]
			elif key == 'rw' or key == 'rw':
				outputDict['d'][key] = subOutputDict[key]
			elif key == 'lb':
				outputDict['e'][key] = subOutputDict[key]
 		#print outputDict
 		return outputDict

 	def twoBallAutoAccuracy(self, team):
 		timds = self.getCompletedTIMDsForTeam(team)
 		twoBallAutoCompleted = 0
 		for timd in timds:
 			totalNumShots = timd.numHighShotsMadeAuto + timd.numLowShotsMadeAuto + timd.numHighShotsMissedAuto + timd.numLowShotsMissedAuto
 			if totalNumShots > 2:
 				twoBallAutoCompleted += 1
 		return twoBallAutoCompleted / len(timds)

	def blockingAbility(self, team):
		allHighShotsAccuracies = 0
		numTeams = 0
		for team in self.comp.teams:
			if team.calculatedData.highShotAccuracyTele != None: 
				allHighShotsAccuracies += team.calculatedData.highShotAccuracyTele 
				numTeams += 1
		avgHighShotAccuracy = allHighShotsAccuracies / numTeams
		if team.calculatedData.avgShotsBlocked != None:
			return 5 * avgHighShotAccuracy * team.calculatedData.avgShotsBlocked

	def autoAbility(self, team):
		t = team.calculatedData
		defensesCrossed = sum(filter(lambda x: x != None, map(lambda dKey: team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[dKey], team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto.keys())))
		return (10 * t.avgHighShotsAuto) + (5 * t.avgLowShotsAuto) + (2 * t.reachPercentage) + 10 if defensesCrossed >= 1 else 0

	def teleopShotAbility(self, team): return (5 * team.calculatedData.avgHighShotsTele + 2 * team.calculatedData.avgLowShotsTele)

	def siegeAbility(self, team): 
		return 15 * team.calculatedData.scalePercentage + 5 * team.calculatedData.challengePercentage

	def singleSiegeAbility(self, timd): return (15 * self.bToI(timd.didScaleTele) + 5 * self.bToI(timd.didChallengeTele))

	def siegeConsistency(self, team): 
		return team.calculatedData.scalePercentage + team.calculatedData.challengePercentage if team.calculatedData.scalePercentage != None and team.calculatedData.challengePercentage != None else None

	def numAutoPointsForTIMD(self, timd):
		defenseCrossesInAuto = 0
		for defense, value in timd.timesSuccessfulCrossedDefensesAuto.items():
			defenseCrossesInAuto += len(value) if value != None else 0
		if defenseCrossesInAuto > 1: defenseCrossesInAuto = 1
		return 10 * int(timd.numHighShotsMadeAuto) + 5 * int(timd.numLowShotsMadeAuto) + 2 * (1 if timd.didReachAuto else 0) + 10 * int(defenseCrossesInAuto)

	def numRPsForTeam(self, team):
		return sum(map(lambda m: self.RPsGainedFromMatchForTeam(m, team), self.getCompletedMatchesForTeam(team)))

	def totalAvgDefenseCategoryCrossingsForAlliance(self, alliance, defenseCategory):
		totalAvgDefenseCategoryCrossings = 0
		for team in alliance:
			categoryCrossings = self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele', defenseCategory)
			if categoryCrossings != None:
				totalAvgDefenseCategoryCrossings += categoryCrossings
		return totalAvgDefenseCategoryCrossings / (len(alliance))

	def totalAvgDefenseCategoryCrossingsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, timd, defenseCategory):
		totalAvgDefenseCategoryCrossings = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				t = 0
				defenses = timd.timesSuccessfulCrossedDefensesTele[defenseCategory]
				for defense, value in defenses.items():
					t += len(value) 
				totalAvgDefenseCategoryCrossings += t / len(defenses)
			else:
				totalAvgDefenseCategoryCrossings += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele', defenseCategory))
		
		return totalAvgDefenseCategoryCrossings / (len(alliance))


	def avgDefenseCategoryCrossingsForTeam(self, team, key, defenseCategory):	#Use in standard deviation calculation for each defenseCategory
		#print utils.makeDictFromTeam(team)['calculatedData']['avgSuccessfulTimesCrossedDefensesAuto'][defenseCategory]
		#print team.calculatedData
		#print team.calculatedData
		if defenseCategory in team.__dict__['calculatedData'].__dict__[key].keys():
			category = team.__dict__["calculatedData"].__dict__[key][defenseCategory]
		else:
			return None
		#print team.calculatedData
		total = 0
		for defense in category:
			#print "TESTING" + str(value)
			if category[defense] != None:
				total += category[defense]
		if defenseCategory == 'e':
			return total
		if len(category) > 0:
			return total / len(category)
		

	def stanDevSumForDefenseCategory(self, alliance, defenseCategory): #CLEAN UP
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0
		for team in alliance:
			timds = self.getCompletedTIMDsForTeam(team)
			if len(timds) == 0:
				return None
			else:
				difOfAvgSquaresTele = 0
				difOfAvgSquaresAuto = 0
				for timd in timds:	#find the variances for a team's crosses in the specified category in auto, and then the same in tele
					numCrossesForDefenseCategoryInMatchTele = 0
					numCrossesForDefenseCategoryInMatchAuto = 0
					if defenseCategory in timd.timesSuccessfulCrossedDefensesTele.keys():
						for value in timd.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
							numCrossesForDefenseCategoryInMatchTele += len(value) - 1
					if defenseCategory in timd.timesSuccessfulCrossedDefensesAuto.keys():
						for value in timd.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
							if value != None:
								numCrossesForDefenseCategoryInMatchAuto += len(value) - 1
					difOfAvgSquaresTele += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele',  defenseCategory) - numCrossesForDefenseCategoryInMatchTele)**2 
					difOfAvgSquaresAuto += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesAuto',  defenseCategory) - numCrossesForDefenseCategoryInMatchAuto)**2 
				difOfAvgSquaresTele /= (len(timds))			#divide difference from average squared by n
				difOfAvgSquaresAuto /= (len(timds))
				varianceValues.append(difOfAvgSquaresTele)
				varianceValues.append(difOfAvgSquaresAuto)
			for i in varianceValues:	
				stanDevSum += i
			return math.sqrt(stanDevSum)

	def stanDevSumForDefenseCategoryWithExclusion(self, alliance, teamWithMatchesToExclude, sTIMD, defenseCategory): #CLEAN UP
		varianceValues = []			#add variance for each data point to array
		stanDevSum = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				numCrossesForDefenseCategoryInMatchTele = 0
				numCrossesForDefenseCategoryInMatchAuto = 0
				for value in sTIMD.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
					numCrossesForDefenseCategoryInMatchTele += len(value) - 1
				for value in sTIMD.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
					numCrossesForDefenseCategoryInMatchAuto += len(value) - 1
				varianceValues.append(difOfAvgSquaresTele)
				varianceValues.append(difOfAvgSquaresAuto)
			else:
				timds = self.getCompletedTIMDsForTeam(team)
				if len(timds) == 0:
					return None
				else:
					difOfAvgSquaresTele = 0
					difOfAvgSquaresAuto = 0
					for timd in timds:	#find the variances for a team's crosses in the specified category in auto, and then the same in tele
						numCrossesForDefenseCategoryInMatchTele = 0
						numCrossesForDefenseCategoryInMatchAuto = 0
						if defenseCategory in timd.timesSuccessfulCrossedDefensesTele.keys():
							for value in timd.timesSuccessfulCrossedDefensesTele[defenseCategory].values():
								numCrossesForDefenseCategoryInMatchTele += len(value) - 1
						if defenseCategory in timd.timesSuccessfulCrossedDefensesAuto.keys():
							for value in timd.timesSuccessfulCrossedDefensesAuto[defenseCategory].values():
								numCrossesForDefenseCategoryInMatchAuto += len(value) - 1
						difOfAvgSquaresTele += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesTele',  defenseCategory) - numCrossesForDefenseCategoryInMatchTele)**2 
						difOfAvgSquaresAuto += (self.avgDefenseCategoryCrossingsForTeam(team, 'avgSuccessfulTimesCrossedDefensesAuto',  defenseCategory) - numCrossesForDefenseCategoryInMatchAuto)**2 
					difOfAvgSquaresTele /= (len(timds))			#divide difference from average squared by n
					difOfAvgSquaresAuto /= (len(timds))
					varianceValues.append(difOfAvgSquaresTele)
					varianceValues.append(difOfAvgSquaresAuto)
				for i in varianceValues:	
					stanDevSum += i
			return math.sqrt(stanDevSum)

	def numScaleAndChallengePointsForTeam(self, team): 
		if team.calculatedData.siegeAbility != None:
			return team.calculatedData.siegeAbility * len(self.getCompletedTIMDsForTeam(team))

	def numSiegePointsForTIMD(self, timd):
		total = 0
		if timd.didChallengeTele: total += 5
		if timd.didScaleTele: total += 15
		return total

	def totalAvgNumShotPointsForTeam(self, team):
		#print "TESTING" + str(team.calculatedData)
		if team.calculatedData.avgHighShotsTele != None:
			return 5 * (team.calculatedData.avgHighShotsTele) + 10 * team.calculatedData.avgHighShotsAuto + 5 * team.calculatedData.avgLowShotsAuto + 2 * team.calculatedData.avgLowShotsTele
	
	def totalSDShotPointsForTeam(self, team):
		return 5 * team.calculatedData.sdHighShotsTele + 10 * team.calculatedData.sdHighShotsAuto + 5 * team.calculatedData.sdLowShotsAuto + 2 * team.calculatedData.sdLowShotsTele

	def shotDataPoints(self, team):
		return [team.calculatedData.avgHighShotsAuto, team.calculatedData.avgLowShotsTele, team.calculatedData.avgHighShotsTele, team.calculatedData.avgLowShotsAuto]

	def totalAvgNumShotsForAlliance(self, alliance):
		totalAvgNumShots = []
		[totalAvgNumShots.extend(self.shotDataPoints(team)) for team in alliance if team.calculatedData.avgHighShotsTele != None]
		return sum(totalAvgNumShots) / len(alliance)

	def totalAvgNumShotsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, timd):
		totalAvgNumShots = 0
		for team in alliance:
			if team.number == teamWithMatchesToExclude.number:
				totalAvgNumShots += timd.numHighShotsMadeAuto + timd.numHighShotsMadeTele + timd.numLowShotsMadeAuto + timd.numLowShotsMadeTele
			else:
				totalAvgNumShots += team.calculatedData.avgHighShotsAuto + team.calculatedData.avgHighShotsTele + team.calculatedData.avgLowShotsTele + team.calculatedData.avgLowShotsAuto
		return totalAvgNumShots / len(alliance)

	def highShotAccuracyForAlliance(self, alliance):
		overallHighShotAccuracy = []
		[overallHighShotAccuracy.extend([team.calculatedData.highShotAccuracyTele, team.calculatedData.highShotAccuracyAuto]) for team in alliance if team.calculatedData.highShotAccuracyAuto != None]
		return sum(overallHighShotAccuracy) / len(overallHighShotAccuracy)

	def blockedShotPointsForAlliance(self, alliance, opposingAlliance):
		blockedShotPoints = 0
		for team in opposingAlliance:
			if team.calculatedData.avgShotsBlocked != None:
				blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.avgShotsBlocked)
		return blockedShotPoints

	def blockedShotPointsForAllianceSD(self, alliance, opposingAlliance):
		blockedShotPoints = 0.0
		for team in opposingAlliance:
			blockedShotPoints += (self.highShotAccuracyForAlliance(alliance) * team.calculatedData.sdShotsBlocked)
		return 5 * blockedShotPoints

	def reachPointsForAlliance(self, alliance):
		reachPoints = 0.0
		for team in alliance:
			if team.calculatedData.reachPercentage != None:
				reachPoints += 2 * team.calculatedData.reachPercentage
			return reachPoints

	def probabilityDensity(self, x, u, o):
		if x != None and u != None and o != None: return stats.norm.cdf(x, u, o) 

	def sumOfStandardDeviationsOfShotsForAlliance(self, alliance):
		sumOfStanDev = 0.0
		for team in alliance:
			# for timd in self.getCompletedTIMDsForTeam(team):
			for key in ['numHighShotsMadeAuto', 'numLowShotsMadeAuto', 'numHighShotsMadeTele', 'numLowShotsMadeTele']:
				dataPoints = [utils.makeDictFromTIMD(timd)[key] for timd in self.getCompletedTIMDsForTeam(team)]
				if len(dataPoints) > 0:
					sumOfStanDev += sp.var(dataPoints)
		return math.sqrt(sumOfStanDev / (len(alliance) * 4))

	def sumOfStandardDeviationsOfShotsForAllianceWithExclusion(self, alliance, teamWithMatchesToExclude, sTIMD):
		sumSD = 0.0
		sumVar = 0.0
		shotVariances = []
		for team in alliance:
			aHS = np.array([])
			tHS = np.array([])
			aLS = np.array([])
			tLS = np.array([])
			timds = self.getCompletedTIMDsForTeam(team)
			if len(timds) == 0:
				return None
			else:
				if(team.number == teamWithMatchesToExclude.number):
					for timd in timds:
						aHS = np.append(aHS, sTIMD.numHighShotsMadeAuto)
						aLS = np.append(aLS, sTIMD.numLowShotsMadeAuto)
						tHS = np.append(tHS, sTIMD.numHighShotsMadeTele)
						tLS = np.append(tLS, sTIMD.numLowShotsMadeTele)
				for timd in timds:
					aHS = np.append(aHS, timd.numHighShotsMadeAuto)
					aLS = np.append(aLS, timd.numLowShotsMadeAuto)
					tHS = np.append(tHS, timd.numHighShotsMadeTele)
					tLS = np.append(tLS, timd.numLowShotsMadeTele)
				if len(timds) > 1:
					sumVar += sp.stats.tvar(aHS) + sp.stats.tvar(aLS) + np.var(tHS) + sp.stats.tvar(tLS)

		sumVar /= (len(alliance) * 4) 

		return math.sqrt(sumVar)

	def defenseFacedForTIMD(self, timd, defenseKey):
		match = self.getMatchForNumber(timd.matchNumber)
		team = self.getTeamForNumber(timd.teamNumber)
		defensePositions = match.redDefensePositions if self.getTeamAllianceIsRedInMatch(team, match) else match.blueDefensePositions
		return defenseKey in defensePositions

	def numTimesTeamFacedDefense(self, team, defenseKey):
		return len(filter(lambda timd: self.defenseFacedForTIMD(timd, defenseKey), self.getCompletedTIMDsForTeam(team)))

	def numTimesCompetitionFacedDefense(self, defenseKey):
		return sum(map(lambda t: self.numTimesTeamFacedDefense(t, defenseKey), self.teamsWithMatchesCompleted()))

	def competitionProportionForDefense(self, defenseKey):
		competitionDefenseSightings = self.numTimesCompetitionFacedDefense(defenseKey)
		competitionTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsInCompetition())
		return competitionDefenseSightings / competitionTotalNumberOfDefenseSightings if competitionTotalNumberOfDefenseSightings > 0 else 0

	def teamProportionForDefense(self, team, defenseKey):
		teamDefenseSightings = self.numTimesTeamFacedDefense(team, defenseKey)
		teamTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsForTeam(team))
		return teamDefenseSightings / teamTotalNumberOfDefenseSightings if teamTotalNumberOfDefenseSightings > 0 else 0

	def alphaForTeamForDefense(self, team, defenseKey):
		return self.competitionProportionForDefense(defenseKey) + self.teamProportionForDefense(team, defenseKey)

	def betaForTeamForDefense(self, team, defenseKey):
		pdb.set_trace()
		cachedData = self.cachedTeamDatas[team.number]
		defenseAlpha = cachedData.alphas[defenseKey]
		sumDefenseAlphas = sum(map(lambda dKey: cachedData.alphas[dKey], self.defenseList))
		return defenseAlpha / sumDefenseAlphas if sumDefenseAlphas > 0 else None

	def predictedCrosses(self, team, defenseKey):
		defenseRetrievalFunction = self.getDefenseRetrievalFunctionForDefense(lambda t: t.calculatedData.avgSuccessfulTimesCrossedDefensesTele, defenseKey)
		averageOfDefenseCrossingsAcrossCompetition = np.mean([defenseRetrievalFunction(t) for t in self.teamsWithMatchesCompleted() if defenseRetrievalFunction(t) != None])
		teamAverageDefenseCrossings = defenseRetrievalFunction(t)
		competitionDefenseSightings = self.numTimesCompetitionFacedDefense(defenseKey)
		teamDefenseSightings = self.numTimesTeamFacedDefense(team, defenseKey)
		competitionTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsInCompetition())
		print "Hello"
		teamTotalNumberOfDefenseSightings = 5 * len(self.getCompletedTIMDsForTeam(team))
		print "Hi"
		proportionOfCompetitionDefenseSightings = competitionDefenseSightings / competitionTotalNumberOfDefenseSightings if competitionTotalNumberOfDefenseSightings > 0 else 0 
		print "Hallo"
		proportionOfTeamDefenseSightings = teamDefenseSightings / teamTotalNumberOfDefenseSightings if teamTotalNumberOfDefenseSightings > 0 else 0 
		print "Hola"
		theta = sum([self.betaForTeamForDefense(team, dKey) for dKey in self.defenseList if self.betaForTeamForDefense(team, dKey) != None]) # TODO: Rename theta something better
		print "Hello2"
		try: 
			return (averageOfDefenseCrossingsAcrossCompetition * theta + teamAverageDefenseCrossings * teamDefenseSightings) / (teamAverageDefenseCrossings + 1)
		except:
			pass
	
	def listOfSuperDataPointsForTIMD(self, timd):
		return [timd.rankTorque, timd.rankSpeed, timd.rankEvasion, timd.rankDefense, timd.rankBallControl]

	def sdOfRValuesAcrossCompetition(self):
		allSuperDataPoints = []
		[allSuperDataPoints.extend(self.listOfSuperDataPointsForTIMD(timd)) for timd in self.comp.TIMDs if self.timdIsCompleted(timd)]
		return np.std(allSuperDataPoints)

	def RScoreForTeamForRetrievalFunction(self, team, retrievalFunction):
		avgRValue = self.getAverageForDataFunctionForTeam(team, retrievalFunction)
		avgTIMDObjectsForTeams = map(lambda t: self.getAverageForDataFunctionForTeam(t, retrievalFunction), self.teamsWithMatchesCompleted())
		averageRValuesOverComp = np.mean(avgTIMDObjectsForTeams)
		RScore = 2 * stats.norm.pdf(avgRValue, averageRValuesOverComp, self.comp.sdRScores)
		return RScore

	def singleMatchRScore(self, timd, key):
		dtimd = utils.makeDictFromTIMD(timd)
		RValue = dtimd[key]
		averageRValuesOverComp = 0.0
		for team1 in self.comp.teams:
			averageRValuesOverComp += self.averageTIMDObjectOverMatches(team1, key)
		averageRValuesOverComp /= len(self.comp.teams)
		avgRValue = utils.makeDictFromTIMD(timd)[key]
		RScore = 2 * (avgRValue, averageRValuesOverComp, self.comp.sdRScores)
		return RScore

	def sdPredictedScoreForMatch(self, match):
		sdPredictedScoreForMatch = {'blue' : 0, 'red' : 0}
		totalSDNumShots = 0
		blueTeams = []
		for teamNumber in match.blueAllianceTeamNumbers:
			blueTeams.append(self.getTeamForNumber(teamNumber))
			predictedScoreForMatch['blue'] += self.totalSDShotPointsForTeam(team)
		
		redTeams = []
		for teamNumber in match.redAllianceTeamNumbers:
			redTeams.append(self.getTeamForNumber(teamNumber)) 

		predictedScoreForMatch['blue'] -= self.blockedShotPointsForAllianceSD(blueTeams, redTeams)
		predictedScoreForMatch['blue'] += self.reachPointsForAlliance(blueTeams)
		crossPointsForAlliance = 0
		for team in blueTeams:
			for defenseCategory in team.calculatedData.avgSuccessfulTimesCrossedDefensesTele:
				crossPointsForAlliance += min(sum(team.calculatedData.avgSuccessfulTimesCrossedDefensesTele[defenseCategory].values()), 2)
				crossPointsForAlliance += min(sum(team.calculatedData.avgSuccessfulTimesCrossedDefensesAuto[defenseCategory].values()), 2)
		predictedScoreForMatch['blue'] += crossPointsForAlliance

	def drivingAbilityForTIMD(self, timd):
		return (1 * timd.rankTorque) + (1 * timd.rankBallControl) + (1 * timd.rankEvasion) + (1 * timd.rankDefense) + (1 * timd.rankSpeed)

	def drivingAbility(self, team, match):
		return drivingAbilityForTIMD(self.getTIMDForTeamNumberAndMatchNumber(team, match))

	def predictedCrossingsForDefenseCategory(self, team, category):
		return np.mean([self.predictedCrosses(team, dKey) for dKey in self.defenseDictionary[category] if self.predictedCrosses(team, dKey) != None])

	def predictedTeleDefenseCrossingsForTeam(self, team):
		return sum(map(lambda category: self.pointsForDefenseCategory(team, category), self.categories))

	def predictedTeleDefensePointsForAllianceForCategory(self, alliance, category):
		predictedCrossingsRetrievalFunction = lambda t: self.predictedCrossingsForDefenseCategory(t, category)
		unlimitedCrossingsForAllianceForCategory = sum(map(predictedCrossingsRetrievalFunction, alliance))
		return min(unlimitedCrossingsForAllianceForCategory, 2)

	def predictedScoreForAllianceWithNumbers(self, allianceNumbers):
		return self.predictedScoreForAlliance(map(self.getTeamForNumber, allianceNumbers))

	def predictedScoreForAlliance(self, alliance):
		print "Predicting score!1"
		allianceTeleopShotPoints = sum([t.calculatedData.teleopShotAbility for t in alliance if t.calculatedData.teleopShotAbility != None]) # TODO: What do we do if there is a team on the alliance that is None?
		print "Predicting score!2"
		allianceSiegePoints = sum([t.calculatedData.siegeAbility for t in alliance if t.calculatedData.siegeAbility != None])
		print "Predicting score!3"
		allianceAutoPoints = sum([t.calculatedData.autoAbility for t in alliance if t.calculatedData.autoAbility != None])
		print "Predicting score!4"
		alliancePredictedCrossingsRetrievalFunction = lambda c: self.predictedTeleDefensePointsForAllianceForCategory(alliance, c)
		print "Predicting score!5"
		allianceDefensePointsTele = sum(map(alliancePredictedCrossingsRetrievalFunction, self.categories))
		print "Predicting score!6"
		return allianceTeleopShotPoints + allianceSiegePoints + allianceAutoPoints + allianceDefensePointsTele

	def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
		alliance = map(self.getTeamForNumber, match.redAllianceTeamNumbers) if allianceIsRed else map(self.getTeamForNumber, match.blueAllianceTeamNumbers)
		opposingAlliance = [team for team in self.teamsInMatch(match) if team not in alliance]
		breachRPsPerCategory = [self.probabilityDensity(2.0, self.totalAvgDefenseCategoryCrossingsForAlliance(alliance, c), self.stanDevSumForDefenseCategory(alliance, c)) for c in self.categories]
		captureRPs = self.probabilityDensity(8.0, self.totalAvgNumShotsForAlliance(alliance), self.sumOfStandardDeviationsOfShotsForAlliance(alliance))
		scoreRPs = self.scoreRPsGainedFromMatchWithScores(self.predictedScoreForAlliance(alliance), self.predictedScoreForAlliance(opposingAlliance))
		if breachRPsPerCategory != None and captureRPs != None and scoreRPs != None:
			return sum(breachRPsPerCategory) + (captureRPs * np.prod(map(siegeConsistency, alliance))) + scoreRPs

	def predictedTIMDScoreCustomAlliance(self, alliance, teamWithMatchesToExclude, timd):
			predictedScoreCustomAlliance = 0		
			otherTeams = []
			for team in alliance:
				if(team.number == teamWithMatchesToExclude.number):
					predictedScoreCustomAlliance += timd.numHighShotsMadeTele + 10 * timd.numHighShotsMadeAuto + 5 * timd.numLowShotsMadeTele + 2 * timd.numLowShotsMadeAuto #woot
				else:
					totalAvgShotPoints = self.totalAvgNumShotPointsForTeam(team)
					if totalAvgShotPoints != None:
						otherTeams.append(team)
						predictedScoreCustomAlliance += self.totalAvgNumShotPointsForTeam(team)
			for team in otherTeams:
				predictedScoreCustomAlliance += team.calculatedData.reachPercentage * 2
			predictedScoreCustomAlliance += (2 * self.bToI(timd.didReachAuto)) 
			
			productOfScaleAndChallengePercentages = 1

			standardDevCategories = []
			crossPoints = 0
			sdSum = self.sumOfStandardDeviationsOfShotsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd) 
			if sdSum == str(self.ourTeamNum) + " has insufficient data":
				return None
			for category in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesTele:
				crossPoints += min(self.totalAvgDefenseCategoryCrossingsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd, category) / len(category), 2) 
			predictedScoreCustomAlliance += 5 * crossPoints
			for team in alliance:
				if team.number == teamWithMatchesToExclude.number:
					productOfScaleAndChallengePercentages *= self.bToI(timd.didScaleTele or timd.didChallengeTele)
				else:
					productOfScaleAndChallengePercentages *= self.siegeConsistency(team)
			predictedScoreCustomAlliance += 25 * self.probabilityDensity(8.0, self.totalAvgNumShotsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd), sdSum) * productOfScaleAndChallengePercentages 
			breachPercentage = 1

			for defenseCategory in alliance[0].calculatedData.avgSuccessfulTimesCrossedDefensesAuto:
				standardDevCategories.append(self.stanDevSumForDefenseCategoryWithExclusion(alliance, teamWithMatchesToExclude, timd, defenseCategory)) #Make Secondary Version
			standardDevCategories = sorted(standardDevCategories)

			for category in range(1, len(standardDevCategories) + 1):
				category = self.categories[category - 1]
				breachPercentage *= self.probabilityDensity(2.0, totalAvgDefenseCategoryCrossingsForAllianceWithExclusion(alliance, teamWithMatchesToExclude, timd, category), self.stanDevSumForDefenseCategoryWithExclusion(alliance, teamWithMatchesToExclude, timd, defenseCategory)) #Make Secondary Version


			predictedScoreCustomAlliance += 20 * breachPercentage

			return predictedScoreCustomAlliance

	def citrusDPR(self, team):
		teamsInValidMatches = self.teamsWithMatchesCompleted()
		numTimesTogetherFunction = lambda t1, t2: sum(map(lambda m: self.teamsAreOnSameAllianceInMatch(t1, t2, m), self.getCompletedMatchesForTeam(t1)))
		getRowForTeamFunction = lambda t1: map(lambda t: numTimesTogetherFunction(t1, t), teamsInValidMatches)
		matrixOfMatchesTogether = np.matrix(map(getRowForTeamFunction, teamsInValidMatches))
		try:
			inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatchesTogether)
		except:
			print 'Cannot invert matrix.'
			return None
		deltaFunction = lambda t: sum(map(predictedScoreForAlliance, self.getAllTeamOppositionAlliances(t))) - sum(self.getTeamMatchScores(t))
		teamDeltas = map(deltaFunction, teamsInValidMatches)	
		return np.dot(np.matrix(teamDeltas), inverseMatrixOfMatchOccurrences)

	def citrusDPRForTIMD(self, timd):
		ATeam = self.getTeamForNumber(timd.teamNumber)
		teamsWithMatchesPlayed = []
		for team in self.comp.teams:
			if len(self.getCompletedTIMDsForTeam(team)) > 0:
				teamsWithMatchesPlayed.append(team)
		matrixOfMatches = np.zeros((len(teamsWithMatchesPlayed), len(teamsWithMatchesPlayed)))
		for team1 in teamsWithMatchesPlayed:	#Create an array where the values correspond to how many matches two teams played together in the same alliance
			for team2 in teamsWithMatchesPlayed:
				occurrence = 0
				for match in self.matches:
					if (team1.number in match.blueAllianceTeamNumbers and team2.number in match.blueAllianceTeamNumbers) or (team1.number in match.redAllianceTeamNumbers and team2.number in match.redAllianceTeamNumbers):
						occurrence += 1
				matrixOfMatches[teamsWithMatchesPlayed.index(team1), teamsWithMatchesPlayed.index(team2)] = occurrence
		
		inverseMatrixOfMatchOccurrences = np.linalg.inv(matrixOfMatches)	
		teamDeltas = np.array([])
		oppositionPredictedScore = 0
		oppositionActualScore = 0
		for team1 in teamsWithMatchesPlayed:
			oppositionPredictedScore = 0
			oppositionActualScore = 0
			for match in self.getPlayedMatchesForTeam(ATeam):
				if team1.number in match.blueAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedRedScore  
					oppositionActualScore += match.redScore
				elif team1.number in match.redAllianceTeamNumbers:
					oppositionPredictedScore += match.calculatedData.predictedBlueScore
					oppositionActualScore += match.blueScore
			teamDelta = oppositionPredictedScore - oppositionActualScore
			teamDeltas = np.append(teamDeltas, teamDelta)	#Calculate delta of each team (delta(team) = sum of predicted scores - sum of actual scores)
		teamDeltas.shape = (len(teamsWithMatchesPlayed), 1)	 
		citrusDPRMatrix = np.dot(inverseMatrixOfMatchOccurrences, teamDeltas)

		return citrusDPRMatrix

	def firstPickAbility(self, team):
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
		return self.predictedScoreForAlliance([ourTeam, team])

	def teamInMatchFirstPickAbility(self, team, match):
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
		alliance = [ourTeam, team]
		predictedScoreCustomAlliance = self.predictedScoreCustomAlliance(alliance) 
		if math.isnan(predictedScoreCustomAlliance):
			return None
		return self.predictedScoreCustomAlliance(alliance) 

	def allianceWithTeamRemoved(self, team, alliance):
		return filter(lambda t: t.number != team.number)

	def scoreContributionToTeamOnAlliance(self, team, alliance):
		return predictedScoreForAlliance(alliance) - self.predictedScoreForAlliance(self.allianceWithTeamRemoved(team, alliance))

	def secondPickAbilityForTeamWithTeam(self, team1, team2):
		gamma = 0.5
		if gamma != None and team1.calculatedData.citrusDPR != None and self.predictedScoreForAlliance([self.getOurTeam(), team2, team1]) != None:
			return gamma * team1.calculatedData.citrusDPR + (1 - gamma) * self.predictedScoreForAlliance([self.getOurTeam(), team2, team1])

	def secondPickAbility(self, team):
		pdb.set_trace()
		secondPickAbilityDict = {}
		secondPickAbilityFunction = lambda t: utils.setDictionaryValue(secondPickAbilityDict, t.number, self.secondPickAbilityForTeamWithTeam(team, t))
		map(secondPickAbilityFunction, self.teamsWithMatchesCompleted())
		return secondPickAbilityDict

	def overallSecondPickAbility(self, team):
		secondPickAbilityFunction = lambda t: team.calculatedData.secondPickAbility[t.number]
		return np.mean(map(secondPickAbilityFunction, self.teamsSortedByRetrievalFunctions([lambda t: t.calculatedData.firstPickAbility], teamsRetrievalFunction=self.teamsWithCalculatedData)[:16]))

	def teamsSortedByRetrievalFunctions(self, retrievalFunctions, teamsRetrievalFunction=teamsWithMatchesCompleted):
		teams = teamsRetrievalFunction()
		mappableRetrievalFunction = lambda f: teams.sort(key=f)
		map(mappableRetrievalFunction, retrievalFunctions[::-1])
		return teams

	def secondPickAbilityWithExclusion(self, team, timd):
		gamma = 0.5
		teamsArray = []
		for team1 in self.comp.teams:
			if len(self.getCompletedTIMDsForTeam(team)) > 0:
				teamsArray.append(team1)
		secondPickAbility = {}
		ourTeam = self.getTeamForNumber(self.ourTeamNum)
		citrusDPRMatrix = self.citrusDPR(team)
		for team1 in teamsArray:
			if team1.number != self.ourTeamNum and team1.number != team.number:	#Loop through all of the teams and find the score contribution of the team whose
				citrusDPR = citrusDPRMatrix[teamsArray.index(team1) - 1]
				alliance3Robots = [ourTeam, team, team1]				
				alliance2Robots = [ourTeam, team1]
				scoreContribution = self.predictedTIMDScoreCustomAlliance(alliance3Robots, team, timd) - self.predictedTIMDScoreCustomAlliance(alliance2Robots, team, timd)
				secondPickAbility[team1.number] = gamma * scoreContribution * (1 - gamma) * int(citrusDPR)		#gamma is a constant
		for key, spa in secondPickAbility.items():
			if math.isnan(spa): secondPickAbility[key] = -2
		return secondPickAbility

	def breachPercentage(self, team):
		breachPercentage = 0
		for match in self.team.matches:
			if team.number in match.blueAllianceTeamNumbers and match.blueScore != None:
				if match.blueAllianceDidBreach == True:
					breachPercentage += 1
			elif team.number in match.redAllianceTeamNumbers and match.blueScore != None:
				if match.redAllianceDidBreach == True:
					breachPercentage += 1
		return breachPercentage/len(self.team.matches)


	def numDefensesCrossedInMatch(self, allianceIsRed, match):
		alliance = map(self.getTeamForNumber, match.redAllianceTeamNumbers) if allianceIsRed else map(self.getTeamForNumber, match.blueAllianceTeamNumbers)
		crossesForAlliance = 0
		if match.redScore != None and match.blueScore != None:
			for team in alliance:
				timd = self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number)
				for defense in timd.timesSuccessfulCrossedDefensesTele.values():
					crossesForAlliance += len(defense) 
				for defense in timd.timesSuccessfulCrossedDefensesAuto.values():
					crossesForAlliance += len(defense) 
		return crossesForAlliance

	def predictedNumberOfRPs(self, team):
		totalRPForTeam = 0
		overallChallengeAndScalePercentage = 0
		overallBreachPercentage = 0
		matchesToBePlayedCounter = 0

		for match in self.matches:		
			if team.number in match.redAllianceTeamNumbers and match.redScore == None:	#Only award predictedRPs if the match has not been played
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += self.siegeConsistency(team)
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.predictedScoreForMatch(match)['red']['score'] > self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 2
				elif self.predictedScoreForMatch(match)['red']['score'] == self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			elif team.number in match.blueAllianceTeamNumbers and match.blueScore == None:
				matchesToBePlayedCounter += 1
				for teamNumber in match.blueAllianceTeamNumbers:
					team = self.getTeamForNumber(teamNumber)
					overallChallengeAndScalePercentage += team.calculatedData.challengePercentage + team.calculatedData.scalePercentage
					overallBreachPercentage += team.calculatedData.breachPercentage

				if self.predictedScoreForMatch(match)['blue']['score'] > self.predictedScoreForMatch(match)['red']['score']:
					totalRPForTeam += 2
				elif self.predictedScoreForMatch(match)['red']['score'] == self.predictedScoreForMatch(match)['blue']['score']:
					totalRPForTeam += 1

			else:
				print 'This team does not exist or all matches have been played'

		totalRPForTeam += (overallChallengeAndScalePercentage / 3)
		totalRPForTeam += (overallBreachPercentage / 3)

		return totalRPForTeam + self.numRPsForTeam(team)
	
	def scoreContribution(self, timd):
		individualScore = 0
		individualScore += timd.numHighShotsMadeTele + timd.numHighShotsMadeAuto + timd.numLowShotsMadeAuto + timd.numLowShotsMadeTele
		defenseCrossesAuto = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesAuto)
		defenseCrossesTele = self.flattenDictionary(timd.timesSuccessfulCrossedDefensesTele)
		for crosses in defenseCrossesAuto.values():
			if len(crosses) - 1 >= 1:
				individualScore += 10
				break
		for crosses in defenseCrossesTele.values():
			individualScore += 5 * min(len(crosses) - 1, 2)
		if timd.didChallengeTele: individualScore += 5
		if timd.didScaleTele: individualScore += 15
		return individualScore

	def getFieldsForAllianceForMatch(self, allianceIsRed, match):
		return (match.redScore, match.redAllianceDidBreach, match.redAllianceDidCapture) if allianceIsRed else (match.blueScore, match.blueAllianceDidBreach, match.blueAllianceDidCapture)

	def scoreRPsGainedFromMatchWithScores(self, score, opposingScore):
		if score > opposingScore:
			return 2
		elif score == opposingScore:
			return 1
		else: 
			return 0

	def getTeamScoreInMatch(self, team, match):
		return getFieldsForAllianceForMatch(self.getTeamAllianceIsRedInMatch(team, match), match)[0]

	def getTeamMatchScores(self, team):
		return map(lambda m: getTeamMatchScores(team, m), self.getCompletedMatchesForTeam(team))

	def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
		numRPs = 0
		ourFields = self.getFieldsForAllianceForMatch(allianceIsRed, match)
		opposingFields = self.getFieldsForAllianceForMatch(not allianceIsRed, match)
		numRPs += self.scoreRPsGainedFromMatchWithScores(ourFields[0], opposingFields[0])
		numRPs += int(utils.convertFirebaseBoolean(ourFields[1]))
		numRPs += int(utils.convertFirebaseBoolean(ourFields[2]))
		return numRPs

	def getTeamAllianceIsRedInMatch(self, team, match):
		if team.number in match.redAllianceTeamNumbers:
			return True
		elif team.number in match.blueAllianceTeamNumbers:
			return False
		else:
			raise ValueError('Team ' + str(team.number) + ' is not in match ' + str(match.number))

	def RPsGainedFromMatchForTeam(self, match, team):
		return self.RPsGainedFromMatchForAlliance(self.getTeamAllianceIsRedInMatch(team, match), match)

	#Competition wide Metrics
	def avgCompScore(self):
		a = [(match.redScore + match.blueScore) for match in self.matches if (match.blueScore != None and match.redScore != None)]
		return sum(a) / len(self.matches)

	def numPlayedMatchesInCompetition(self):
		return len([match for match in self.matches if self.matchIsPlayed(match)])

	def getRankingForTeamByRetrievalFunctions(self, team, retrievalFunctions):
		return self.teamsSortedByRetrievalFunctions(retrievalFunctions, teamsRetrievalFunction=self.teamsWithCalculatedData).index(team)

	def getSeedingFunctions(self):
		return [lambda t: t.numRPs, lambda t: t.autoAbility, lambda t: t.siegeAbility]

	def getPredictedSeedingFunctions(self):
		predictedAutoPointsFunction = lambda t: self.getPredictedResultOfRetrievalFunctionForTeam(t, lambda t2: t2.autoAbility)
		predictedSiegePointsFunction = lambda t: self.getPredictedResultOfRetrievalFunctionForTeam(t, lambda t2: t2.siegeAbility)
		return [lambda t: t.predictedNumRPs, predictedAutoPointsFunction, predictedSiegePointsFunction]

	def teamsForTeamNumbersOnAlliance(self, alliance):
		return map(self.getTeamForNumber, alliance)

	def getAllianceForMatch(self, match, allianceIsRed):
		return teamsForTeamNumbersOnAlliance(match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers)

	def getAllianceForTeamInMatch(self, team, match):
		return self.getAllianceForMatch(match, self.getTeamAllianceIsRedInMatch(team, match))

	def getPredictedResultOfRetrievalFunctionForAlliance(self, retrievalFunction, alliance):
		return sum(map(retrievalFunction, alliance))

	def getPredictedResultOfRetrievalFunctionForTeamInMatch(self, team, match, retrievalFunction):
		return self.getPredictedResultOfRetrievalFunctionForAlliance(retrievalFunction, self.getAllianceForTeamInMatch(team, match))

	def getPredictedResultOfRetrievalFunctionForTeam(self, retrievalFunction, team):
		return np.mean(map(retrievalFunction, self.getMatchesForTeam(team)))

	def getDefenseLength(self, dict, defenseKey):
		return len(dict[defenseKey]) if defenseKey in dict else None

	def defenseKeysThatAreNotNone(self, defenseDict):
		return filter(lambda dKey: defenseDict[dKey] != None, defenseDict)

	def teamInMatchDatasThatHaveDefenseValueNotNoneForTeam(self, team, retrievalFunction, defenseKey):
		return filter(lambda timd: defenseKey in retrievalFunction(timd), self.getCompletedTIMDsForTeam(team))

	def getDefensesThatTeamHasCrossedForRetrievalFunction(self, team, retrievalFunction):
		return retrievalFunctions(team).keys()

	def getAverageForDefenseDataFunctionForTeam(self, team, retrievalFunction, defenseKey, dataFunction):
		return np.mean(map(dataFunction, self.teamInMatchDatasThatHaveDefenseValueNotNoneForTeam(team, retrievalFunction, defenseKey)))

	def setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForTeam(self, team, keyRetrievalFunction, valuesRetrievalFunction):
		dict = keyRetrievalFunction(team)
		someFunction = lambda dKey, timd: self.getDefenseLength(valuesRetrievalFunction(timd), dKey)
		getAverageFunction = lambda dKey: self.getAverageForDefenseDataFunctionForTeam(team, lambda timd: valuesRetrievalFunction(timd), dKey, lambda timd: someFunction(dKey, timd))
		protectedGetAverageFunction = lambda dKey: getAverageFunction(dKey) if not math.isnan(getAverageFunction(dKey)) else None
		dictionarySetFunction = lambda dKey: utils.setDictionaryValue(dict, dKey, protectedGetAverageFunction(dKey))
		map(dictionarySetFunction, self.defenseList)

	# def getAvgOfDefensesForRetrievalFunctionForTeam(self, team, teamRetrievalFunction):
	# 	defenseRetrievalFunctions = self.getDefenseRetrievalFunctions(teamRetrievalFunction)
	# 	return np.mean(map(lambda retrievalFunction: retrievalFunction(team), defenseRetrievalFunctions))

	# def setDefenseValuesForTeam(self, team, keyRetrievalFunction, valueRetrievalFunction, dataPointModificationFunction):
	# 	dict = keyRetrievalFunction(team)
	# 	defenseRetrievalFunctions = map(lambda dKey: self.getDefenseRetrievalFunctionForDefense(retrievalFunctions, dKey), self.defensesList)
	# 	defenseModifiedFunctions = map(dataPointModificationFunction, defenseRetrievalFunctions)
		
	# 	for d in self.defensesList:
	# 		defenseRetrievalFunction = self.getDefenseRetrievalFunctionForDefense(retrievalFunctions, d)
	# 		defenseLengthFunction = lambda t: len(defenseRetrievalFunction(t))
	# 		self.getAverageForDataFunctionForTeam(team, defenseLengthFunction)


	# 	defenseRetrievalFunctions = self.getDefenseRetrievalFunctions(keyRetrievalFunction)
	# 	defenseValueFunctions = map(len, self.getDefenseRetrievalFunctions(valueRetrievalFunction))
	# 	defenseModifiedFunctions = map(dataPointModificationFunction, defenseValueFunctions)
	# 	setFunction = lambda dKey: utils.setDictionaryValue(dict, dKey, defenseModifiedFunctions)
	# 	map(, self.defenseList)
	# 	defenseSetFunction = lambda dp: utils.setDictionaryKey(keyRetrievalFunction(team), dataPointModificationFunction(self.getDefenseRetrievalFunctionForDefensePairing(valueRetrievalFunction, dp)))
	# 	# defenseRetrievalFunctions = map(self.getDefenseRetrievalFunctionForDefensePairing, self.getDefensePairings())
	# 	map(defenseSetFunction, self.getDefensePairings())

	def getAverageOfDataFunctionAcrossCompetition(self, dataFunction):
		return np.mean(map(lambda timd: dataFunction(timd)), self.TIMDs)

	def getAverageTeam():
		cachedData = self.cachedTeamDatas[team.number]
		map(lambda dKey: utils.setDictionaryValue(cachedData.alphas, dKey, self.alphaForTeamForDefense(team, dKey)), self.defenseList)

		t.avgTorque = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.rankTorque) # Checked
		t.avgSpeed = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.rankSpeed)  # Checked
		t.avgEvasion = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.rankEvasion)  # Checked
		t.avgDefense = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.rankDefense)  # Checked
		t.avgBallControl = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.rankBallControl)  # Checked
		
		t.disabledPercentage = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didGetDisabled)))
		t.incapacitatedPercentage = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didGetIncapacitated)))
		t.disfunctionalPercentage = t.disabledPercentage + t.incapacitatedPercentage 

		#Auto
		t.autoAbility = self.autoAbility(team) ----
		t.avgHighShotsAuto = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.numHighShotsMadeAuto) #Checked
		t.avgLowShotsAuto = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: timd.numLowShotsMadeAuto) #Checked	
		t.reachPercentage = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didReachAuto)))
		t.highShotAccuracyAuto = self.getAverageOfDataFunctionAcrossCompetition(team, self.getTIMDHighShotAccuracyAuto) # Checked
		t.lowShotAccuracyAuto = self.getAverageOfDataFunctionAcrossCompetition(team, self.getTIMDLowShotAccuracyAuto) # Checked
		t.numAutoPoints = self.getAverageOfDataFunctionAcrossCompetition(team, self.numAutoPointsForTIMD) # Checked
		t.avgMidlineBallsIntakedAuto = self.getAverageOfDataFunctionAcrossCompetition(team, lambda timd: len(timd.ballsIntakedAuto))
		----t.sdHighShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto) # Checked
		----t.sdLowShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto) # Checked
		# t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, 'ballsIntakedAuto')
		t.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto) # Checked\
		----self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForTeam(team, lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda timd: timd.timesSuccessfulCrossedDefensesAuto)
		# self.setDefenseValuesForTeam(team, lambda t1: t1.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda timd: timd.timesSuccessfulCrossedDefensesAuto, lambda rF: self.getAverageForDataFunctionForTeam(team, lambda timd: len(rF(timd))))				
	
		# #Tele
		t.scalePercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didScaleTele)))
		t.challengePercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didChallengeTele)))
		t.avgGroundIntakes = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numGroundIntakesTele) # Checked
		t.avgBallsKnockedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto) # Checked
		t.avgShotsBlocked = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numShotsBlockedTele) # Checked
		t.avgHighShotsTele = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeTele) # Checked
		t.avgLowShotsTele = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeTele) # Checked
		t.highShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, self.getTIMDHighShotAccuracyTele) # Checked
		t.lowShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, self.getTIMDLowShotAccuracyTele) # Checked
		# t.blockingAbility = self.blockingAbility(team) # TODO: Move this later
		t.teleopShotAbility = self.teleopShotAbility(team) # Checked
		t.siegeConsistency = self.siegeConsistency(team)# Checked
		t.siegeAbility = self.siegeAbility(team) # Checked
		t.sdHighShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeTele) # Checked
		t.sdLowShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeTele) # Checked
		t.sdGroundIntakes = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numGroundIntakesTele) # Checked
		t.sdShotsBlocked = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numShotsBlockedTele) # Checked
		t.numRPs = self.numRPsForTeam(team) # Checked
		t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team) # Checked


	def doFirstCalculationsForTeam(self, team):
		if len(self.getCompletedTIMDsForTeam(team)) <= 0:
				print "No Complete TIMDs for team " + str(team.number) + ", " + team.name
		else:
			print("Beginning first calculations for team: " + str(team.number) + ", " + team.name)
			#Super Scout Averages

			if not self.calculatedDataHasValues(team.calculatedData):
				team.calculatedData = DataModel.CalculatedTeamData()
			t = team.calculatedData

			cachedData = self.cachedTeamDatas[team.number]
			map(lambda dKey: utils.setDictionaryValue(cachedData.alphas, dKey, self.alphaForTeamForDefense(team, dKey)), self.defenseList)

			t.avgTorque = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankTorque) # Checked
			t.avgSpeed = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankSpeed)  # Checked
			t.avgEvasion = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankEvasion)  # Checked
			t.avgDefense = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankDefense)  # Checked
			t.avgBallControl = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.rankBallControl)  # Checked
			
			t.disabledPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didGetDisabled)))
			t.incapacitatedPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didGetIncapacitated)))
			t.disfunctionalPercentage = t.disabledPercentage + t.incapacitatedPercentage 

			#Auto
			t.autoAbility = self.autoAbility(team)
			t.avgHighShotsAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto) #Checked
			t.avgLowShotsAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto) #Checked	
			t.reachPercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didReachAuto)))
			t.highShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team, self.getTIMDHighShotAccuracyAuto) # Checked
			t.lowShotAccuracyAuto = self.getAverageForDataFunctionForTeam(team, self.getTIMDLowShotAccuracyAuto) # Checked
			t.numAutoPoints = self.getAverageForDataFunctionForTeam(team, self.numAutoPointsForTIMD) # Checked
			t.avgMidlineBallsIntakedAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: len(timd.ballsIntakedAuto))
			t.sdHighShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeAuto) # Checked
			t.sdLowShotsAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeAuto) # Checked
			# t.sdMidlineBallsIntakedAuto = self.getStandardDeviationForDataFunctionForTeam(team, 'ballsIntakedAuto')
			t.sdBallsKnockedOffMidlineAuto = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto) # Checked\
			self.setDefenseValuesForKeyRetrievalFunctionForValuesRetrievalFunctionForTeam(team, lambda tm: tm.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda timd: timd.timesSuccessfulCrossedDefensesAuto)
			# self.setDefenseValuesForTeam(team, lambda t1: t1.calculatedData.avgSuccessfulTimesCrossedDefensesAuto, lambda timd: timd.timesSuccessfulCrossedDefensesAuto, lambda rF: self.getAverageForDataFunctionForTeam(team, lambda timd: len(rF(timd))))				
		
			# #Tele
			t.scalePercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didScaleTele)))
			t.challengePercentage = self.getAverageForDataFunctionForTeam(team, lambda timd: int(utils.convertFirebaseBoolean(timd.didChallengeTele)))
			t.avgGroundIntakes = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numGroundIntakesTele) # Checked
			t.avgBallsKnockedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numBallsKnockedOffMidlineAuto) # Checked
			t.avgShotsBlocked = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numShotsBlockedTele) # Checked
			t.avgHighShotsTele = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeTele) # Checked
			t.avgLowShotsTele = self.getAverageForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeTele) # Checked
			t.highShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, self.getTIMDHighShotAccuracyTele) # Checked
			t.lowShotAccuracyTele = self.getAverageForDataFunctionForTeam(team, self.getTIMDLowShotAccuracyTele) # Checked
			# t.blockingAbility = self.blockingAbility(team) # TODO: Move this later
			t.teleopShotAbility = self.teleopShotAbility(team) # Checked
			t.siegeConsistency = self.siegeConsistency(team)# Checked
			t.siegeAbility = self.siegeAbility(team) # Checked
			t.sdHighShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numHighShotsMadeTele) # Checked
			t.sdLowShotsTele = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numLowShotsMadeTele) # Checked
			t.sdGroundIntakes = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numGroundIntakesTele) # Checked
			t.sdShotsBlocked = self.getStandardDeviationForDataFunctionForTeam(team, lambda timd: timd.numShotsBlockedTele) # Checked
			t.numRPs = self.numRPsForTeam(team) # Checked
			t.numScaleAndChallengePoints = self.numScaleAndChallengePointsForTeam(team) # Checked

	def doSecondCalculationsForTeam(self, team):
		if len(self.getCompletedTIMDsForTeam(team)) <= 0:
				print "No Complete TIMDs for team " + str(team.number) + ", " + team.name
		else:
			print("Beginning second calculations for team: " + str(team.number) + ", " + team.name)
			t = team.calculatedData
			t.RScoreTorque = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankTorque)
			t.RScoreSpeed = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankSpeed)
			t.RScoreEvasion = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankEvasion)
			t.RScoreDefense = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankDefense)
			t.RScoreBallControl = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankBallControl)
			t.RScoreDrivingAbility = self.RScoreForTeamForRetrievalFunction(team, self.drivingAbilityForTIMD)

			t.firstPickAbility = self.firstPickAbility(team) # Checked	
			# t.secondPickAbility = self.secondPickAbility(team) # Checked
			# t.overallSecondPickAbility = self.overallSecondPickAbility(team) # Checked
			# t.citrusDPR = self.citrusDPR(team)
			# t.actualSeeding = self.getRankingForTeamByRetrievalFunctions(team, self.getSeedingFunctions()) # Checked
			# t.predictedSeeding = self.getRankingForTeamByRetrievalFunctions(self.getPredictedSeedingFunctions()) # Checked

	def doFirstCalculationsForTIMD(self, timd):
		print "Beginning first calculations for team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber)
		team = self.getTeamForNumber(timd.teamNumber)
		match = self.getMatchForNumber(timd.matchNumber)

		self.TIMDs = filter(lambda t: (t.teamNumber != timd.teamNumber) == (t.matchNumber != timd.matchNumber), self.comp.TIMDs)
		self.matches = filter(lambda m: self.teamInMatch(team, m), self.comp.matches)

		self.doFirstTeamCalculations()
		self.doMatchesCalculations()
		self.doSecondTeamCalculations()
		
		if not self.calculatedDataHasValues(timd.calculatedData):
			timd.calculatedData = DataModel.CalculatedTeamInMatchData()
		c = timd.calculatedData
		c.highShotAccuracyTele = self.getTIMDHighShotAccuracyTele(timd) # Checked
		c.highShotAccuracyAuto = self.getTIMDHighShotAccuracyAuto(timd) # Checked
		c.lowShotAccuracyTele = self.getTIMDLowShotAccuracyTele(timd) # Checked
		c.lowShotAccuracyAuto = self.getTIMDLowShotAccuracyAuto(timd) # Checked
		c.siegeAbility = self.singleSiegeAbility(timd)
		c.numRPs = self.RPsGainedFromMatchForAlliance(timd.teamNumber in match.redAllianceTeamNumbers, match)
		c.numAutoPoints = self.numAutoPointsForTIMD(timd)
		c.numScaleAndChallengePoints = c.siegeAbility #they are the same		
		c.numBallsIntakedOffMidlineAuto = self.getAverageForDataFunctionForTeam(team, lambda timd: len(timd.ballsIntakedAuto))

	def doSecondCalculationsForTIMD(self, timd):
		print "Beginning second calculations for team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber)
		c = timd.calculatedData
		team = self.getTeamForNumber(timd.teamNumber)
		match = self.getMatchForNumber(timd.matchNumber)

		self.TIMDs = filter(lambda t: (t.teamNumber != timd.teamNumber) == (t.matchNumber != timd.matchNumber), self.comp.TIMDs)
		self.matches = filter(lambda m: self.teamInMatch(team, m), self.comp.matches)

		self.doFirstTeamCalculations()
		self.doMatchesCalculations()
		self.doSecondTeamCalculations()

		c.RScoreTorque = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankTorque)
		c.RScoreSpeed = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankSpeed)
		c.RScoreEvasion = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankEvasion)
		c.RScoreDefense = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankDefense)
		c.RScoreBallControl = self.RScoreForTeamForRetrievalFunction(team, lambda timd: timd.rankBallControl)
		c.RScoreDrivingAbility = self.RScoreForTeamForRetrievalFunction(team, self.drivingAbilityForTIMD)
		c.firstPickAbility = 0
		c.secondPickAbility = {}
		c.overallSecondPickAbility = 0

	def doFirstCalculationsForMatch(self, match):
		if not self.matchIsCompleted(match):
			print "Match " + str(match.number) + " has not been played yet."
		else:
			print "Beginning calculations for match " + str(match.number) + "..."
			# match.calculatedData.predictedBlueScore = self.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
			# print "still going..."
			# match.calculatedData.predictedRedScore = self.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
			# print "still going..."
			# match.calculatedData.predictedBlueRPs = self.predictedRPsForAllianceForMatch(False, match)
			# match.calculatedData.predictedRedRPs = self.predictedRPsForAllianceForMatch(True, match)
			# match.calculatedData.numDefensesCrossedByBlue = self.numDefensesCrossedInMatch(False, match)
			# match.calculatedData.numDefensesCrossedByRed = self.numDefensesCrossedInMatch(True, match)
			# match.calculatedData.actualBlueRPs = self.RPsGainedFromMatchForAlliance(True, match)
			# match.calculatedData.actualRedRPs = self.RPsGainedFromMatchForAlliance(False, match)
			# FBC.addCalculatedMatchDataToFirebase(match.number, match.calculatedData)
			# print("Putting calculations for match " + str(match.number) + " to Firebase.")

	def restoreComp(self):
		self.TIMDs = self.comp.TIMDs
		self.matches = self.comp.matches

	def doFirstTeamCalculations(self):
		for team in self.comp.teams:
			self.doFirstCalculationsForTeam(team)

	def doSecondTeamCalculations(self):
		for team in self.comp.teams:
			self.doSecondCalculationsForTeam(team)

	def doMatchesCalculations(self):
		for match in self.comp.matches:
			self.doFirstCalculationsForMatch(match)

	def doCalculations(self, FBC):
		self.comp.sdRScores = self.sdOfRValuesAcrossCompetition()
		for team in self.comp.teams:
			for timd in self.getCompletedTIMDsForTeam(team):
				self.doFirstCalculationsForTIMD(timd)
			self.restoreComp()
			self.doFirstCalculationsForTeam(team)
		for match in self.comp.matches:
			self.doFirstCalculationsForMatch(match)
		for team in self.comp.teams:
			for timd in self.getCompletedTIMDsForTeam(team):
				self.doSecondCalculationsForTIMD(timd)
			self.restoreComp()
			self.doSecondCalculationsForTeam(team)
		for team in self.comp.teams:
			print "Writing team " + str(team.number) + " to Firebase..."
			FBC.addCalculatedTeamDataToFirebase(team)
		for timd in self.comp.TIMDs:
			print "Writing team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber) + " to Firebase..."
			FBC.addCalculatedTIMDataToFirebase(timd)
		for match in self.comp.matches:
			print "Writing match " + str(match.number) + " to Firebase..."
			FBC.addCalculatedMatchDataToFirebase(match)

		# for team in self.comp.teams:
			# timds = self.getCompletedTIMDsForTeam(team)
#
			# print("Calculating TIMDs for team " + str(team.number)) + "... "
			# for timd in timds:
				# 
			# self.TIMDs = self.comp.TIMDs
			# self.doCalculationsForTeam(team)
				
		#Match Metrics
		# for match in self.matches:
			

		# for team in self.teamsWithCalculatedData():
			
			# FBC.addCalculatedTeamDataToFirebase(team.number, team.calculatedData)

		#Competition metrics
		if self.numPlayedMatchesInCompetition() > 0:
			self.comp.averageScore = self.avgCompScore()
			

