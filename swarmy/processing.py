# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   15/02/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
"""
Description:
This module includes all computation procedures of an agent.
"""

# =============================================================================
# Imports
# =============================================================================
import itertools
from .innate import Innate
from .learning import Learning
import time
from .constants import *



# =============================================================================
# Class
# =============================================================================
class Processing():

    TIME_STEP_COUNTER = 0
    TURN_TIMESTEP_COUNTER = 0
    """
    In the processing object all computation procedures of an agent are represented.
    
    Args:
        a (agent.py): instance of the agent
        t (int):    ToF turn distance
    """    
    def __init__(self, a):
        """
        Initialize processing object.
        """    
        self.agent = a
        self.Ti = 0
        self.Ci = 0
        self.qi = 0.0
        self.visitedCellSet = set()
        
        # current agent state
        self.state = {
            "processing state":  0,  # Current processing state --> 
            "carries token":     0,  # Does the agent carry a token? --> boolean {0:no 1:yes}
            "source detected":   0,  # Has the agent detected a source? --> boolean {0:no 1:yes}
            "sink detected":     0,  # Has the agent detected a sink? --> boolean {0:no 1:yes}    
            "token detected":    0   # Has the agent detected a token in a sink? --> boolean {0:no 1:yes}    
        }

        # possible values for each substate
        self.stateValues = [[0,1], [0,1], [0,1], [0,1]]        
        
         # list of tuples that represent all combinations for the state
        self.stateCombinations = list(itertools.product(*self.stateValues)) # cartesian product

        # self monitoring
        self.monitoring = {
            "rewards":          0,       # Current rewards
            "cumulatedRewards": 0,       # Cumulated rewards      
            "collisions":       0        # How many collisions had the agent?
        }
        
        self.actionCodes = {
            "move forward":    0,  # Does the agent carry a token?
            "collect token":   1,  # Has the agent detected a source?
            "discard token":   2,  # Has the agent detected a sink?    
            "wait":            3   # Has the agent detected a token in a sink?                
        }
                
               
        # instantiate processing units
        self.innate = Innate(self)
        self.learning = Learning(self)
        

    def perform(self, pressedKeys):
        """
        Update agent processing for one timestep
        """

        
        # control the agent with ID=1 via keyboard
        #if(self.agent.ID == 1):
        self.agent.actuation.processUserInput(pressedKeys)         
        start_time = 0
        # --- self monitoring ---
        # self.selfMonitoring()

        #TODO This is where the count Ti, Ci and qi  calculations, state change algo etc. should go
        positionX = self.agent.body.rect.centerx
        positonY = self.agent.body.rect.centery


        #When in exploration state
        if(self.agent.state == STATE_EXPLORATION):
            # print(self.agent.environment.displaySurface.get_at((int(positionX) , int(positonY)+10))) #added 10 as height of robot is 10, it looks just infront of it.
            localRects = self.agent.environment.rectList
            for r in range(0,len(localRects)):
                if (localRects[r].collidepoint(positionX, positonY)):
                    #TODO do exploration calculation stuff
                    if not r in self.visitedCellSet:
                        self.visitedCellSet.add(r)
                        self.Ti+=1
                        color_from_sensor = self.agent.environment.displaySurface.get_at((int(positionX) , int(positonY)+10))
                        colr_opinion = self.getColorOpinion(color_from_sensor)
                        # print(f"color = {color_from_sensor}, opinion = {colr_opinion}")
                        if colr_opinion == self.agent.color_opinion:
                            self.Ci+=1
                        
                    #print(f"Rect ID = {r}")
                    break

            if(self.agent.ID == 1):
                print(f"Ci = {self.Ci} and Ti = {self.Ti}")

            


        #Rotation Phase for 5 sec
        if(self.TURN_TIMESTEP_COUNTER > FRAMES_PER_SEC * 5):
            self.TIME_STEP_COUNTER = 0
            self.TURN_TIMESTEP_COUNTER = 0
        
        #Move Straight for 10 sec
        if(self.TIME_STEP_COUNTER < FRAMES_PER_SEC * 10):
            
            # --- innate behaviour ---
            self.innate.communicate()   
            self.innate.explore()
            self.innate.forage()
            self.TIME_STEP_COUNTER += 1
        else:
            self.innate.turn()
            self.TURN_TIMESTEP_COUNTER += 1
        
        # --- learning procedure ---
        #self.learning.rl_qLearning()
        
        
    # def selfMonitoring(self):
    #     # self-monitoring status
    #     if(self.agent.nesting.communication.tokens): # if agent has tokens 
    #         self.agent.processing.state["carries token"] = 1
    #     else:
    #         self.agent.processing.state["carries token"] = 0
    
    def getColorOpinion(self,x):
        if(x == (242,245,66)):
            return 0
        if(x == (48,138,255)):
            return 1
        else:
            return -1