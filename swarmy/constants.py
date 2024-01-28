

#These are the 3 color opinions the robot can have
COMMITED_OPINION_A = 0 
COMMITED_OPINION_B = 1
UNCOMMITED_OPTION = 2

STATE_EXPLORATION = 3
STATE_DISSEMINATION = 4

EXP_SELF_SOURCING = 5
EXP_POLLING = 6

D_DIRECT_SWITCH = 7
D_MAJORITY_RULE = 8

PERCENTAGE_COLOR_A = 0.5 #the percentage of the grid you want to be of color 1 519
PERCENTAGE_COLOR_B = 0.5 #the percentage of the grid you want to be of color 2 481
FRAMES_PER_SEC = 60
PROBABILITY_NU = 0.01 #Probabilty to do self soucring instead of polling
D = 0.9 #Probability to do direct switch instead of majority voting
RANGE = 350 #Communiation range of the robot
