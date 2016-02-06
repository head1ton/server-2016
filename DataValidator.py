# Data Validation Module, by Bryton Moeller, Feb 4, 2016
import DataModel
import firebaseCommunicator
import utils

class DataValidator(object):
	"""docstring for DataValidator"""
	def __init__(self, competition):
		super(DataValidator, self).__init__()
		self.competition = competition
		self.defensesDict = {
		 	'a' : {'pc' : -1, 'cdf' : -1},
			'b' : {'mt' : -1, 'rp' : -1},
			'c' : {'db' : -1, 'sp' : -1},
			'd' : {'rw' : -1, 'rt' : -1},
			'e' : {'lb' : -1}
		}
		self.valueNotUploaded = [-1, -1.0, "-1", ['-1'], self.defensesDict, False, {}, ['lb', '', '', '', '']]

	def validateFirebase(self):
		print("Teams Validation Problems: " + str(self.validateTeams(self.competition.teams)))
		print("Matches Validation Problems: " + str(self.validateMatches(self.competition.matches)))
		#self.validateTIMDs(self.competition.TIMDs)
		#self.validateCompetitionHighestLevelData(self.competition)

	def validateTeams(self, teams):
		problems = []
		for team in teams:
			thereHasBeenANegetive1 = False
			thereHasBeenANonNegetive = False
			for key, value in utils.makeDictFromTeam(team).items():
				
				if key == "calculatedData":
					ctdProblems = self.validateCalculatedTeamData(value)
					if ctdProblems != []:
						problems.append(ctdProblems)
				
				if key == "teamInMatchDatas":
					continue
					# for TIMD in value:
					# 	timdProblems = self.validateTIMDs(utils.makeDictFromTIMD(TIMD))
					# 	if timdProblems != []:
					# 		problems.append(timdProblems)

				if (value in self.valueNotUploaded) and key != "name" and key != "number":
					thereHasBeenANegetive1 = True
				else:
					thereHasBeenANonNegetive = True
				
				if thereHasBeenANegetive1 and thereHasBeenANonNegetive:
					problems.append(str(team.number) + ": Has a -1 in one value, but not in another.\n")

		return problems



	def validateCalculatedTeamData(self, CTD):
		problems = []
		for key, value in CTD.items():
			thereHasBeenANegetive1 = False
			thereHasBeenANonNegetive = False
			if (value in self.valueNotUploaded) and key != "name" and key != "number":
				thereHasBeenANegetive1 = True
			else:
				thereHasBeenANonNegetive = True
			
			if thereHasBeenANegetive1 and thereHasBeenANonNegetive:
				problems.append(str(team.number) + ": Has a -1 in one CALCULATED DATA value, but not in another.\n")

		return problems

	def validateTeamInMatchData(self, TIMD):
		problems = []
		for key, value in TIMD.items():
			thereHasBeenANegetive1 = False
			thereHasBeenANonNegetive = False
			if (value in self.valueNotUploaded) and key != "name" and key != "number":
				thereHasBeenANegetive1 = True
			else:
				thereHasBeenANonNegetive = True
			
			if thereHasBeenANegetive1 and thereHasBeenANonNegetive:
				problems.append(str(team.number) + ": Has a -1 in one TEAM IN MATCH DATA value, but not in another.")

		return problems



	def validateMatches(self, matches):
		problems = []
		for match in matches:
			match = utils.makeDictFromMatch(match)
			if match["redScore"] > -0.5 or match["blueScore"] > -0.5:
				for timd in match["TIMDs"]:
					if timd.rankTorque < 0:
						problems.append("TIMD: " + str(timd.teamNumber) + "Q" + str(timd.matchNumber) + " should be played but isn't.\n")

