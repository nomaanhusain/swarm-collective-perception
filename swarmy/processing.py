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
import numpy as np
import random
import math
from .constants import *



# =============================================================================
# Class
# =============================================================================
class Processing():

    time_step_counter = 0
    turn_timestep_counter = 0
    state_timestep_counter = 0
    exploration_time_calculated = False
    dessimation_time_calculated = True
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
        self.straightMovementTimeDetermined = False
        self.straightMoveDuration = 5
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
        if not self.straightMovementTimeDetermined:
            self.straightMoveDuration = random.randrange(8,12)
            self.straightMovementTimeDetermined = True
        # --- self monitoring ---
        # self.selfMonitoring()

        #TODO This is where the count Ti, Ci and qi  calculations, state change algo etc. should go
        positionX = self.agent.body.rect.centerx
        positonY = self.agent.body.rect.centery

        # if(self.agent.ID == 1):
        #     if(self.agent.state == STATE_EXPLORATION and self.agent.Qi < 0.5):
        #         print(f"State Exploration, qi = {self.agent.Qi}. ExploreTime = {self.state_timestep_counter}. Exp_State = {self.agent.exp_state}")
        #     if(self.agent.state == STATE_DESSEMINATION and self.agent.Qi < 0.5):
        #         print(f"State Dessimation, qi = {self.agent.Qi}. DessTime = {self.state_timestep_counter}. Exp_State = {self.agent.exp_state}")

        if(not self.exploration_time_calculated):
            self.state_timestep_counter = self.calculateExplorationTime() * FRAMES_PER_SEC
            self.exploration_time_calculated = True
        
        if(not self.dessimation_time_calculated):
            self.state_timestep_counter = self.calculateDessiminationTime() * FRAMES_PER_SEC
            self.dessimation_time_calculated = True
        #When in exploration state
        if(self.agent.state == STATE_EXPLORATION):
            self.state_timestep_counter -= 1
            
            localRects = self.agent.environment.rectList
            for r in range(0,len(localRects)):
                if (localRects[r].collidepoint(positionX, positonY)):
                    if not r in self.visitedCellSet:
                        self.visitedCellSet.add(r)
                        self.Ti+=1
                        color_from_sensor = self.agent.environment.displaySurface.get_at((int(positionX) , int(positonY)+10)) #added 10 as height of robot is 10, it looks just infront of it.
                        colr_opinion = self.getColorOpinion(color_from_sensor) #returns color option
                        # print(f"color = {color_from_sensor}, opinion = {colr_opinion}")

                        #If grid collor same as agent opinion increase Ci
                        if colr_opinion == self.agent.color_opinion:
                            self.Ci+=1
                        
                    #print(f"Rect ID = {r}")
                    break
            #End of exploration phase
            if(self.state_timestep_counter == 0):
                #TODO check if current agent is in exploration state and polling state 
                # Calculate distance of current agent to all other agent and if in range and other agent in dessimination state, get its 
                #opinion, if different from current agent opinion, go undecided. 
                #If our agent is undecided then get opinion of neighbor by majority rule

                if(self.agent.exp_state == EXP_POLLING):
                    agentList = self.agent.agents
                    neighbourList = list()
                    for a in agentList:
                        if(a.state == STATE_DESSEMINATION):
                            nXPos = a.body.rect.centerx
                            nYPos = a.body.rect.centery
                            eqDist = self.calculateEquladianDistance(positionX,nXPos,positonY,nYPos)
                            if(eqDist < 150):
                                neighbourList.append(a)

                    if(len(neighbourList)!=0):
                        cnt_op_A = 0
                        cnt_op_B = 0
                        cnt_undicided = 0
                        final_opinion = -1
                        for n in neighbourList:
                            if(n.color_opinion == COMMITED_OPINION_A):
                                cnt_op_A+=1
                            if(n.color_opinion == COMMITED_OPINION_B):
                                cnt_op_B+=1
                            if(n.color_opinion == UNCOMMITED_OPTION):
                                cnt_undicided+=1

                        # we see the majority of these three values and take that as the opinion we want, if same cnt then choose randomly
                        if(cnt_op_A > cnt_op_B and cnt_op_A > cnt_undicided):
                            final_opinion = COMMITED_OPINION_A
                        if(cnt_op_B > cnt_op_A and cnt_op_B > cnt_undicided):
                            final_opinion = COMMITED_OPINION_B
                        if(cnt_undicided > cnt_op_A and cnt_undicided > cnt_op_B):
                            final_opinion = UNCOMMITED_OPTION
                        if(cnt_op_A == cnt_op_B and cnt_op_A > cnt_undicided):
                            final_opinion = np.random.choice([COMMITED_OPINION_A,COMMITED_OPINION_B])
                        if(cnt_op_A == cnt_undicided and cnt_op_A > cnt_op_B):
                            final_opinion = np.random.choice([COMMITED_OPINION_A,UNCOMMITED_OPTION])
                        if(cnt_op_B == cnt_undicided and cnt_op_B > cnt_op_A):
                            final_opinion = np.random.choice([COMMITED_OPINION_B,UNCOMMITED_OPTION])
                        if(cnt_op_A == cnt_op_B and cnt_op_A == cnt_undicided):
                            final_opinion == np.random.choice([COMMITED_OPINION_A,COMMITED_OPINION_B,UNCOMMITED_OPTION])
                        
                        prevOp = self.agent.color_opinion

                        #If not same as self, become undecided
                        if(self.agent.color_opinion != final_opinion and self.agent.color_opinion != UNCOMMITED_OPTION):
                            print("Going uncommited")
                            self.agent.color_opinion = UNCOMMITED_OPTION
                        #if uncommided, take the majority opinion
                        else:
                            print("taking an opinion")
                            self.agent.color_opinion = final_opinion

                        print(f" for agent {self.agent.ID} Opinion Updated from {prevOp} to {self.agent.color_opinion}")


                       


                if(self.agent.exp_state == EXP_SELF_SOURCING):
                    qi = min(1, (2*self.Ci)/self.Ti)
                    # if(self.agent.ID == 1):
                    #     print(f"Calculated qi = {qi} Ci = {self.Ci} Ti = {self.Ti}")
                    if qi >= 0.5:
                        self.agent.Qi = 1
                    else:
                        self.agent.Qi = qi
                self.dessimation_time_calculated = False
                self.exploration_time_calculated = True
                self.visitedCellSet.clear()
                self.Ti = 0
                self.Ci = 0
                self.agent.state = STATE_DESSEMINATION
                
        
        if(self.agent.state == STATE_DESSEMINATION):
            self.state_timestep_counter -= 1
            #TODO dessimination stuff



            #End of dessimation phase
            if(self.state_timestep_counter == 0):
                #At the end of dessimination state robot decides to either go to polling or self sourcing
                self.agent.exp_state = np.random.choice([EXP_SELF_SOURCING,EXP_POLLING],p=[PROBABILITY_N, 1 - PROBABILITY_N])
                self.dessimation_time_calculated = True
                self.exploration_time_calculated = False
                self.agent.state = STATE_EXPLORATION

        
        



              
            

            


            
        
        #Move Straight for 10 sec
        if(self.time_step_counter < FRAMES_PER_SEC * self.straightMoveDuration):
            
            # --- innate behaviour ---
            self.innate.communicate()   
            self.innate.explore()
            self.innate.forage()
            self.time_step_counter += 1
        else:
            self.innate.turn()
            self.time_step_counter = 0
            self.turn_timestep_counter = 0
            self.straightMovementTimeDetermined = False
        
        # --- learning procedure ---
        #self.learning.rl_qLearning()
        
        
    # def selfMonitoring(self):
    #     # self-monitoring status
    #     if(self.agent.nesting.communication.tokens): # if agent has tokens 
    #         self.agent.processing.state["carries token"] = 1
    #     else:
    #         self.agent.processing.state["carries token"] = 0
    
    # Returns the color choice from the two colors
    def getColorOpinion(self,x):
        if(x == (242,245,66)):
            return 0
        if(x == (48,138,255)):
            return 1
        else:
            return -1
        
    def calculateExplorationTime(self):
        if(self.agent.color_opinion == UNCOMMITED_OPTION):
            return int(0.5 * 400 * 32 * 0.001)
        else:
            return 100

    def calculateDessiminationTime(self):
        if(self.agent.color_opinion == UNCOMMITED_OPTION):
            return int(0.5 * 400 * 32 * 0.001)
        else:
            return int(self.agent.Qi * 1300 * 32 * 0.001)
        
    def calculateEquladianDistance(self,x1,x2,y1,y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)