import firebaseCommunicator
import utils
import random
# Classes That Reflect Firebase Data Structure

class Competition(object):
	"""docstring for Competition"""
	def __init__(self):
		super(Competition, self).__init__()
		self.code = ""
		self.teams = TeamList([])
		self.matches = []
		self.TIMDs = []
		self.averageScore = -1
		self.predictedSeeding = []
		self.actualSeeding = []
	def updateTeamsAndMatchesFromFirebase(self):
		self.teams = utils.makeTeamsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Teams"))
		self.matches = utils.makeMatchesFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Matches"))
	def updateTIMDsFromFirebase(self):
		self.TIMDs = utils.makeTIMDsFromDicts(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/TeamInMatchDatas"))
		for team in self.teams:
			for TIMD in self.TIMDs:
				if TIMD.teamNumber == team.number:
					team.teamInMatchDatas.append(TIMD) #These loops are nested too far, but not a lot we can do about it.
		for match in self.matches:
			for TIMD in self.TIMDs:
				if TIMD.matchNumber == match.number:
					match.TIMDs.append(TIMD)
		

class CalculatedTeamData(object):
	"""The calculatedData for an FRC Team object"""
	def __init__(self, **args):
		super(CalculatedTeamData, self).__init__()
		self.secondPickAbility = {
			1678 : -1.0
		}
		self.avgSuccessfulTimesCrossedDefenses = {
			'a' : {'pc' : -1.0, 'cdf' : -1.0},
			'b' : {'mt' : -1.0, 'rp' : -1.0},
			'c' : {'db' : -1.0, 'sp' : -1.0},
			'd' : {'rw' : -1.0, 'rt' : -1.0},
			'e' : {'lb' : -1.0}
		}
		self.firstPickAbility = -1.0
		self.overallSecondPickAbility = -1.0
		self.citrusDPR = -1.0
		self.highShotAccuracyAuto = -1.0 #Works
		self.lowShotAccuracyAuto = -1.0 #Works
		self.highShotAccuracyTele = -1.0 #Works
		self.lowShotAccuracyTele = -1.0 #Works
		self.avgGroundIntakes = -1.0 #Works
		self.avgHighShotsTele = -1.0 #Works
		self.avgLowShotsTele = -1.0 #Works
		self.avgShotsBlocked = -1.0 #Works
		self.avgHighShotsAuto = -1.0 #Works
		self.avgLowShotsAuto = -1.0 #Works
		self.avgMidlineBallsIntakedAuto = -1.0 #Works
		self.avgBallsKnockedOffMidlineAuto = -1.0 #Works
		self.avgTorque = -1.0
		self.avgSpeed = -1.0
		self.avgEvasion = -1.0
		self.avgDefense = -1.0
		self.avgBallControl = -1.0
		self.blockingAbility = -1.0
		self.disfunctionalPercentage = -1.0
		self.reachPercentage = -1.0
		self.disabledPercentage = -1.0
		self.incapacitatedPercentage = -1.0
		self.scalePercentage = -1.0
		self.challengePercentage = -1.0
		self.breachPercentage = -1.0
		self.avgSuccessfulTimesCrossedDefensesAuto = { #Works
		  	'a' : {'pc' : -1.0, 'cdf' : -1.0},
			'b' : {'mt' : -1.0, 'rp' : -1.0},
			'c' : {'db' : -1.0, 'sp' : -1.0},
			'd' : {'rw' : -1.0, 'rt' : -1.0},
			'e' : {'lb' : -1.0}
		}
		self.avgSuccessfulTimesCrossedDefensesTele = { #Works
		  	'a' : {'pc' : -1.0, 'cdf' : -1.0},
			'b' : {'mt' : -1.0, 'rp' : -1.0},
			'c' : {'db' : -1.0, 'sp' : -1.0},
			'd' : {'rw' : -1.0, 'rt' : -1.0},
			'e' : {'lb' : -1.0}
		}
		self.avgFailedTimesCrossedDefensesAuto = {
		 	'a' : {'pc' : -1.0, 'cdf' : -1.0},
			'b' : {'mt' : -1.0, 'rp' : -1.0},
			'c' : {'db' : -1.0, 'sp' : -1.0},
			'd' : {'rw' : -1.0, 'rt' : -1.0},
			'e' : {'lb' : -1.0}
		}
		self.avgFailedTimesCrossedDefensesTele = {
		 	'a' : {'pc' : -1.0, 'cdf' : -1.0},
			'b' : {'mt' : -1.0, 'rp' : -1.0},
			'c' : {'db' : -1.0, 'sp' : -1.0},
			'd' : {'rw' : -1.0, 'rt' : -1.0},
			'e' : {'lb' : -1.0}
		}
		self.siegePower = -1.0
		self.siegeConsistency = -1.0
		self.siegeAbility = -1.0
		self.predictedNumRPs = -1.0
		self.numRPs = -1
		self.numAutoPoints = -1
		self.numScaleAndChallengePoints = -1
		self.sdHighShotsAuto = -1
		self.sdHighShotsTele = -1
		self.sdLowShotsAuto = -1
		self.sdLowShotsTele = -1
		self.sdGroundIntakes = -1
		self.sdShotsBlocked = -1
		self.sdMidlineBallsIntakedAuto = -1
		self.sdBallsKnockedOffMidlineAuto = -1
		self.sdSuccessfulDefenseCrossesAuto = {
			'a' : {'pc' : -1, 'cdf' : -1},
			'b' : {'mt' : -1, 'rp' : -1},
			'c' : {'db' : -1, 'sp' : -1},
			'd' : {'rw' : -1, 'rt' : -1},
			'e' : {'lb' : -1}
		}
		self.sdSuccessfulDefenseCrossesTele = {
			'a' : {'pc' : -1, 'cdf' : -1},
			'b' : {'mt' : -1, 'rp' : -1},
			'c' : {'db' : -1, 'sp' : -1},
			'd' : {'rw' : -1, 'rt' : -1},
			'e' : {'lb' : -1}
		}
		self.sdFailedDefenseCrossesAuto = {
			'a' : {'pc' : -1, 'cdf' : -1},
			'b' : {'mt' : -1, 'rp' : -1},
			'c' : {'db' : -1, 'sp' : -1},
			'd' : {'rw' : -1, 'rt' : -1},
			'e' : {'lb' : -1}
		}
		self.sdFailedDefenseCrossesTele = {
			'a' : {'pc' : -1, 'cdf' : -1},
			'b' : {'mt' : -1, 'rp' : -1},
			'c' : {'db' : -1, 'sp' : -1},
			'd' : {'rw' : -1, 'rt' : -1},
			'e' : {'lb' : -1}
		}
		self.RScoreTorque = -1.0
		self.RScoreSpeed = -1.0
		self.RScoreEvasion = -1.0		
		self.RScoreDefense = -1.0
		self.RScoreBallControl = -1.0
		self.RScoreDrivingAbility = -1.0
		self.predictedSeed = -1
		self.actualSeed = -1
		self.__dict__.update(args)

		

class Team(object):
	"""An FRC Team object"""
	def __init__(self, **args):
		super(Team, self).__init__()
		self.name = ""
		self.number = -1
		self.matches = []
		self.teamInMatchDatas = []
		self.calculatedData = CalculatedTeamData()
		self.selectedImageUrl = '-1'
		self.otherImageUrls = {
			 'not0' : '-1'
		}
		self.pitHeightOfBallLeavingShooter = -1.0
		self.pitLowBarCapability = False
		self.pitPotentialLowBarCapability = -1
		#self.pitPotentialCDFAndPCCapability = -1
		self.pitPotentialMidlineBallCapability = -1
		#self.pitFrontBumperWidth = -1.0
		self.pitDriveBaseWidth = -1.0
		self.pitDriveBaseLength = -1.0
		self.pitBumperHeight = -1.0
		self.pitPotentialShotBlockerCapability = -1
		self.pitNotes = "-1"
		self.pitOrganization = -1
		self.pitNumberOfWheels = -1
		#self.pitHeightOfRobot = -1
		self.__dict__.update(args)


class CalculatedMatchData(object):
	"""docstring for CalculatedMatchData"""
	def __init__(self, **args):
		super(CalculatedMatchData, self).__init__()
		self.predictedRedScore = -1.0
		self.predictedBlueScore = -1.0	

		self.numDefensesCrossedByBlue = -1
		self.numDefensesCrossedByRed = -1 
		self.redScoresForDefenses = {'-1' : -1}
		self.redWinningChanceForDefenses = {'-1' : -1}
		self.redBreachChanceForDefenses = {'-1' : -1}
		self.redRPsForDefenses = {'-1' : -1}
		self.blueScoresForDefenses = {'-1' : -1}
		self.blueWinningChanceForDefenses = {'-1' : -1}
		self.blueBreachChanceForDefenses = {'-1' : -1}
		self.blueRPsForDefenses = {'-1': -1}
		self.redWinChance = -1.0
		self.redBreachChance = -1.0
		self.redCaptureChance = -1.0
		self.blueWinChance = -1.0
		self.blueBreachChance = -1.0
		self.blueCaptureChance = -1.0
		self.predictedBlueRPs = -1.0
		self.actualBlueRPs = -1
		self.predictedRedRPs = -1.0
		self.actualRedRPs = -1	
		self.redAllianceDidBreach = False
		self.blueAllianceDidBreach = False
		self.optimalRedDefenses = ['pc', 'mt', 'sp', 'rw']
		self.optimalBlueDefenses = ['pc', 'mt', 'sp', 'rw']

		self.__dict__.update(args)


class Match(object):
	"""An FRC Match Object"""
	def __init__(self, **args):
		super(Match, self).__init__()
		self.number = -1
		self.calculatedData = CalculatedMatchData()
		self.redAllianceTeamNumbers = []
		self.blueAllianceTeamNumbers = []
		self.redScore = -1
		self.blueScore = -1
		self.redDefensePositions = ['lb', '', '', '', '']
		self.blueDefensePositions = ['lb', '', '', '', '']
		self.redAllianceDidCapture = False
		self.blueAllianceDidCapture = False
		self.blueAllianceDidBreach = False
		self.redAllianceDidBreach = False
		self.TIMDs = []
		self.__dict__.update(args)
		
class TeamInMatchData(object):
	"""An FRC TeamInMatchData Object"""
	def __init__(self, **args):
		super(TeamInMatchData, self).__init__()
		
		self.calculatedData = CalculatedTeamInMatchData()
		self.teamNumber = -1
		self.matchNumber = -1
		self.scoutName = 'no_name'

		self.didGetIncapacitated = False
		self.didGetDisabled = False
		self.rankTorque = -1
		self.rankSpeed = -1
		self.rankEvasion = -1
		self.rankDefense = -1
		self.rankBallControl = -1

		#Auto
		self.ballsIntakedAuto = []
		self.numBallsKnockedOffMidlineAuto = -1
		# self.timesCrossedDefensesAuto = {
		# 	'a' : {'pc' : {'successes' : [-1], 'fails' : [-1]}, 'cdf' : {'successes' : [-1], 'fails' : [-1]}},
		# 	'b' : {'mt' : {'successes' : [-1], 'fails' : [-1]}, 'rp' : {'successes' : [-1], 'fails' : [-1]}},
		# 	'c' : {'db' : {'successes' : [-1], 'fails' : [-1]}, 'sp' : {'successes' : [-1], 'fails' : [-1]}},
		# 	'd' : {'rw' : {'successes' : [-1], 'fails' : [-1]}, 'rt' : {'successes' : [-1], 'fails' : [-1]}},
		# 	'e' : {'lb' : {'successes' : [-1], 'fails' : [-1]}}
		# }

		self.timesSuccessfulCrossedDefensesAuto = {
			'a' : {'pc' : [-1], 'cdf' : [-1]},
			'b' : {'mt' : [-1], 'rp' : [-1]},
			'c' : {'db' : [-1], 'sp' : [-1]},
			'd' : {'rw' : [-1], 'rt' : [-1]},
			'e' : {'lb' : [-1]}
		}

		self.timesFailedCrossedDefensesAuto = {
			'a' : {'pc' : [-1], 'cdf' : [-1]},
			'b' : {'mt' : [-1], 'rp' : [-1]},
			'c' : {'db' : [-1], 'sp' : [-1]},
			'd' : {'rw' : [-1], 'rt' : [-1]},
			'e' : {'lb' : [-1]}
		}

		self.numHighShotsMadeAuto = -1
		self.numLowShotsMadeAuto = -1
		self.numHighShotsMissedAuto = -1
		self.numLowShotsMissedAuto = -1
		self.didReachAuto = False

		#Tele
		self.numHighShotsMadeTele = -1
		self.numLowShotsMadeTele = -1
		self.numHighShotsMissedTele = -1
		self.numLowShotsMissedTele = -1
		self.numGroundIntakesTele = -1
		self.numShotsBlockedTele = -1
		self.didScaleTele = False
		self.didChallengeTele = False
		# self.timesCrossedDefensesTele = {
	 # 		'a' : {'pc' : {'successes' : [-1], 'fails' : [-1]}, 'cdf' : {'successes' : [-1], 'fails' : [-1]}},
	 # 		'b' : {'mt' : {'successes' : [-1], 'fails' : [-1]}, 'rp' : {'successes' : [-1], 'fails' : [-1]}},
	 # 		'c' : {'db' : {'successes' : [-1], 'fails' : [-1]}, 'sp' : {'successes' : [-1], 'fails' : [-1]}},
	 # 		'd' : {'rw' : {'successes' : [-1], 'fails' : [-1]}, 'rt' : {'successes' : [-1], 'fails' : [-1]}},
		# 	'e' : {'lb' : {'successes' : [-1], 'fails' : [-1]}}
		#  }

		self.timesSuccessfulCrossedDefensesTele = {
			'a' : {'pc' : [-1], 'cdf' : [-1]},
			'b' : {'mt' : [-1], 'rp' : [-1]},
			'c' : {'db' : [-1], 'sp' : [-1]},
			'd' : {'rw' : [-1], 'rt' : [-1]},
			'e' : {'lb' : [-1]}
		}

		self.timesFailedCrossedDefensesTele = {
			'a' : {'pc' : [-1], 'cdf' : [-1]},
			'b' : {'mt' : [-1], 'rp' : [-1]},
			'c' : {'db' : [-1], 'sp' : [-1]},
			'd' : {'rw' : [-1], 'rt' : [-1]},
			'e' : {'lb' : [-1]}
		}
		self.superNotes = '-1'

		self.__dict__.update(args)		

class CalculatedTeamInMatchData(object):
	"""docstring for CalculatedTeamInMatchData"""
	def __init__(self, **args):
		super(CalculatedTeamInMatchData, self).__init__()
		self.highShotAccuracyAuto = -1.0 #
		self.lowShotAccuracyAuto = -1.0 #
		self.highShotAccuracyTele = -1.0 #
		self.lowShotAccuracyTele = -1.0 #
		self.siegeAbility = -1.0#
		self.numRPs = -1#
		self.numAutoPoints = -1#
		self.numScaleAndChallengePoints = -1#
		
		self.RScoreTorque = -1.0
		self.RScoreSpeed = -1.0
		self.RScoreEvasion = -1.0		
		self.RScoreDefense = -1.0
		self.RScoreBallControl = -1.0
		self.RScoreDrivingAbility = -1.0
		self.citrusDPR = -1.0 
		self.firstPickAbility = -1.0
		self.secondPickAbility = {
			1678 : -1.0
		}
		self.overallSecondPickAbility = -1.0
		self.scoreContribution = -1.0 #

		self.__dict__.update(args)

#Making Fake Type safety is very much NOT A PYTHON PRACTICE, but may be needed. 
class TeamList(list):
    def __init__(self, iterable=None):
        """Override initializer which can accept iterable"""
        super(TeamList, self).__init__()
        if iterable:
            for item in iterable:
                self.append(item)

    def append(self, item):
        if isinstance(item, Team):
            super(TeamList, self).append(item)
        else:
            raise ValueError('Teams allowed only')

    def insert(self, index, item):
        if isinstance(item, Team):
            super(TeamList, self).insert(index, item)
        else:
            raise ValueError('Teams allowed only')

    def __add__(self, item):
        if isinstance(item, Team):
            super(TeamList, self).__add__(item)
        else:
            raise ValueError('Teams allowed only')

    def __iadd__(self, item):
        if isinstance(item, Team):
            super(TeamList, self).__iadd__(item)
        else:
            raise ValueError('Teams allowed only')
