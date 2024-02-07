
#NON-ADJUSTABLE OPTION (Do not change these values)
#These are the 3 color opinions the robot can have
COMMITED_OPINION_A = 0 
COMMITED_OPINION_B = 1
UNCOMMITED_OPTION = 2

#Robots states
STATE_EXPLORATION = 3
STATE_DISSEMINATION = 4

#Option of polling or self-sourcing
EXP_SELF_SOURCING = 5
EXP_POLLING = 6

#Option for robot's voting model
D_VOTER_MODEL = 7
D_MAJORITY_RULE = 8
FRAMES_PER_SEC = 60

#ADJUSTABLE PARAMETERS (These values can be changed)

PERCENTAGE_COLOR_A = 0.5 #the percentage of the grid you want to be of color 1
PERCENTAGE_COLOR_B = 1 - PERCENTAGE_COLOR_A #the percentage of the grid that is color 2

PROBABILITY_NU = 0.01 #Probabilty to do self soucring instead of polling aka Noise
D = 0.1 # Voter Model percentage
RANGE = 400 #Communiation range of the robot
