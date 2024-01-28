# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   18/02/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
"""
Description:
In this module one specific experiment can be executed.
The module initilizes pygame.
The parameters for the simulation are:
    - simulation speed
    - maximum agent speed
    - number of agents
    - number of obstacles
    - total number of tokens
    - number of sources and sinks
    - source and sink interaction radius
    - token difficulty level
    - communication properties: range, noise
"""


# =============================================================================
# Imports
# =============================================================================
import pygame
import time
import random
import numpy as np

# import internal object classes
from .environment import Environment
from .item import Source
from .item import Sink
from .item import Obstacle
from .agent import Agent
from .constants import *
import os
import datetime
from collections import deque
import matplotlib.pyplot as plt
import csv

# =============================================================================
# Class
# =============================================================================
class Experiment():
    
    def __init__(self):
        super(Experiment, self).__init__()

        
    def run(self, numberOfAgents, rendering, measFolderPath, captFolderPath, xParams):
        """
        Start swarm simulation expermiment
        
        Args:
            numberOfAgents          (int):   choose number of agents for experiment
            rendering               (int):   1 = show simulation; -1 = hide simulation; 0 = black screen (capture mode)           
            measFolderPath       (string):   path to measurement results folder or None if unused
            captFolderPath       (string):   path to image capture folder or None if unused
            xParams                (list):   list with experiment specific parameters. [0] = sensibility rssi fiter; [1] = boolean broadcast token acknowledge
        """
        
        # prepare directories, filenames and measurement file
        filenameExperiment = "" + datetime.datetime.now().strftime("%Y%m%d - Experiment.txt")
        filenameCaptureTemplate = "" + datetime.datetime.now().strftime("%Y%m%d %H%M%S - Capture - ")
            
        if captFolderPath != None:
            os.makedirs(os.path.dirname(captFolderPath), exist_ok=True)
        
        if measFolderPath != None:
            os.makedirs(os.path.dirname(measFolderPath), exist_ok=True)
            measFile = open(measFolderPath + filenameExperiment, "a")
        
        # pygame presets
        pygame.init()  					        # initialize pygame
        running = True  				        # termination condition
            
        # tracking variables
        time_simulation = 0
        timesteps_counter = 0
        timesteps_allTokensInSink = 0           # discarded all tokens in sink
        timesteps_allTokensFromSource = 0       # picked up all tokens from source
        totalCollisions_counter = 0             # collisions of the whole swarm per experiment
        totalReceivedMessages_counter = 0       # Received messages for the whole swarm 
        totalBroadcastedMessages_counter = 0    # Broadcasted messages for the whole swarm 

        # -----------------------------------------------------------------------------
        # instantiations

        # instantiate environment
        environment = Environment(rendering) 
        w = environment.width
        h = environment.height
        
        # instantiate sources
        sourceList = []
        # source1 = Source(1, environment, 0+100, h/2, 75, 75, 3, 10) ## add a new source on a fixed position
        # sourceList.append(source1)
        
        # instantiate sinks
        sinkList = []
        # sink1 = Sink(1, environment, w-100, h/2, 75, 75, 3)
        # sinkList.append(sink1)
        
        # instatiate obstacles
        obstacleList = []
        # obstacle1 = Obstacle(environment, w/2, h/2, 20, 300, 3)    
        # obstacleList.append(obstacle1)
        # obstacle2 = Obstacle(environment, w/4, h/4, 50, 50, 3)       
        # obstacleList.append(obstacle2)

        # instatiate agents
        agentList = []
        count = 0
        while count < numberOfAgents:
            # the agent list is added by reference not by value --> agents have at the end a complete list of all agents
            newAgent = Agent(count+1, [random.randint(10, w-10), random.randint(10, h-10)], random.randint(0, 360), 
                             environment, agentList, sourceList, sinkList, obstacleList, xParams, 
                             np.random.choice([COMMITED_OPINION_A,COMMITED_OPINION_B],p=[PERCENTAGE_COLOR_A, PERCENTAGE_COLOR_B]),
                             np.random.choice([EXP_SELF_SOURCING,EXP_POLLING],p=[PROBABILITY_NU, 1 - PROBABILITY_NU]),
                             np.random.choice([D_DIRECT_SWITCH,D_MAJORITY_RULE],p=[D,1-D]))
            positonAvailable = not newAgent.perception.collisionSensor()
            if(positonAvailable):
                count = count + 1
                agentList.append(newAgent)
        
        # -----------------------------------------------------------------------------
        # initializations
        cntOptAIntit=0
        cntOptBIntit=0
        for a in agentList:
            if a.color_opinion == COMMITED_OPINION_A:
                cntOptAIntit+=1
            if a.color_opinion == COMMITED_OPINION_B:
                cntOptBIntit+=1
        print(f"Initial Opinion Proportion = {cntOptAIntit/cntOptBIntit}")
        agentList[0].body.helperLUT()   # global lookup table needs to be calculated only once

        
        # update after all agents were instantiated
        for agent in agentList:
            agent.perception.helperOAO()  # update other agents list and obstacles list


        # =============================================================================
        # Run experiment: Loop-Processing
        # =============================================================================
        locked = [False,False]   # needed to monitor the timesteps for specific events
        time_start = time.time() # simulation start time
        last_values = deque(maxlen=1000)
        while running:
            timesteps_counter += 1        
            
            #-----------------------------------------------------------------------------
            # ASYNCHRON 
            
            if(timesteps_counter % FRAMES_PER_SEC == 0):
                #Calculate proportion
                countA=0
                countB=0
                countU=0
                for a in agentList:
                    if a.color_opinion == COMMITED_OPINION_A:
                        countA+=1
                    if a.color_opinion == COMMITED_OPINION_B:
                        countB+=1
                    if a.color_opinion == UNCOMMITED_OPTION:
                        countU+=1
                prop = (countA-countB)/(len(agentList) - countU)
                last_values.append(prop)
                print(f"Last Values Length = {len(last_values)}. Proportion = {prop}")


            # get the set of keys pressed and check for user input
            pressedKeys = pygame.key.get_pressed()
                       
            # handle user input
            for event in pygame.event.get():
                
                if event.type == pygame.KEYDOWN:    # Check for KEYDOWN event
                                    
                    # capture current image
                    if event.key == pygame.K_SPACE:
                        for agent in agentList:
                            agent.body.render()
                            #agent.nesting.communication.renderCommRadius()
                        environment.render()
                        if(captFolderPath != None):
                            filenameCapture = filenameCaptureTemplate + str(timesteps_counter) + ".png"
                            filename = captFolderPath + filenameCapture
                            pygame.image.save(environment.getDisplay(), filename) # capture image of current step
                    
                    # print current frames per second
                    elif event.key == pygame.K_f:
                        environment.printFPS()
                        
                    # print all tokens in source
                    elif event.key == pygame.K_q:
                        pass
                        # source1.printTokens()

                    # print all tokens in sink
                    elif event.key == pygame.K_s:
                        pass
                        # sink1.printTokens()                       

                    # print all tokens carried by agents
                    elif event.key == pygame.K_1:
                        allTokens = "Tokens - "
                        for agent in agentList:
                            if(len(agent.nesting.communication.tokens)>0):
                                allTokens = allTokens + "A" + str(agent.ID) + ":" + str( agent.nesting.communication.tokens) + str(" ")
                        print(allTokens)

                    # print number of tokens per token type
                    elif event.key == pygame.K_2:
                        pass
                        # allTokens = []
                        # countTokens = []
                        # for agent in agentList:
                        #     for t in agent.nesting.communication.tokens:
                        #         allTokens.append(t)  
                        # for x in range(10):        
                        #     countTokens.append(allTokens.count("T" + str(x+1)))        
                        # print("Tokens per type: " + str(countTokens))
                    
                    # print number of tokens per agent
                    elif event.key == pygame.K_3:
                        pass
                        # countAgentTokens = []
                        # for agent in agentList:
                        #     countAgentTokens.append(len(agent.nesting.communication.tokens))
                        # print("Tokens per agent: " + str(countAgentTokens))
                      
                    # print number of tokens per agent
                    elif event.key == pygame.K_e:
                        pass
                        # print("Battery Capcity in mAh: " + str(agentList[0].energy.battery))
                        # print("Steps: " + str(timesteps_counter))
                    # If the Esc key is pressed, then exit the main loop
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == pygame.QUIT:
                    running = False
     
            #-----------------------------------------------------------------------------
            # SYNCHRON         
     
            # update agents                                     
            for agent in random.sample(agentList, len(agentList)):
                agent.processing.perform(pressedKeys)
                # agent.energy.dischargeBatteryOneStep()     
            

            # display results
            if(rendering == 1):          
                for agent in agentList:             
                    agent.body.render()         # update agent body           
                    #agent.nesting.communication.renderCommRadius()
                environment.render()     # update content on display
            
                    
                     
        # =============================================================================
        # Save measurement results
        # =============================================================================       
        timestep = 1/environment.FPS
        if measFolderPath != None:
            measFile.write(str(numberOfAgents) + ";")  # number of agents 
            measFile.write(str(round((timestep),6)) + ";")                                     # number of agents
            measFile.write(str(time_simulation) + ";")                              # simulation time
            measFile.write(str(timesteps_allTokensFromSource) + ";")                # performance - all tokens collected from source - number of timesteps
            measFile.write(str(timesteps_allTokensInSink) + ";")                    # performance - all tokens discarded in sink - number of timesteps
            measFile.write(str(round((totalCollisions_counter),2)) + ";")           # collisions in total
            measFile.write(str(round((totalReceivedMessages_counter),2)) + ";")     # received messages in total
            measFile.write(str(round((totalBroadcastedMessages_counter),2)) + ";")  # broadcasts per agent in total
            measFile.write(str(xParams[0]) + ";")                                   # Broadcasting range
            measFile.write(str(xParams[1]))                                         # tokenExchange 
            measFile.write("\n")                                                    # new line
            measFile.close()
        
        # =============================================================================
        # Print measurement results
        # =============================================================================  
        print("\n------------------------------------")    
        print("Number of Agents: " + str(numberOfAgents))
        print("Simulation time: " + str(time_simulation) + " s")
        print("Natural time: " + str(round((timesteps_allTokensInSink*timestep),2)) + " s")        
        print("Collected all tokens from source: " + str(timesteps_allTokensFromSource) + " steps")        
        print("Discarded all tokens in sink: " + str(timesteps_allTokensInSink) + " steps")
        print("Collisions per agent: " + str(round((totalCollisions_counter/numberOfAgents),2)))     # collisions per agent        
        print("Simulation terminated!")
        cnt_a = 0
        cnt_b = 0
        cnt_u = 0
        for agent in agentList:
            if(agent.color_opinion == 0): cnt_a+=1
            if(agent.color_opinion == 1): cnt_b+=1
            if(agent.color_opinion == 2): cnt_u+=1

        print(f"Cnt Opinion A = {cnt_a}. Cnt Opinion B = {cnt_b}. Cnt Opinion undecided = {cnt_u}")

        plt.hist(last_values, bins=50, color='blue', alpha=0.7)

        # Add labels and title
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title('Histogram of Last 1000 Values')
        
        csv_file_path = 'last_values.csv'

        # Write the contents of the deque to the CSV file
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write the header if needed
            # csv_writer.writerow(['Value'])  # Uncomment this line if you want a header

            # Write each value in the deque to a new row
            csv_writer.writerows(map(lambda x: [x], last_values))
        plt.show()
        # DEBUG
        # print q-tables for each agent
        # for agent in agentList:
        #     print("Agent " + str(agent.ID))
        #     print("Cumulated Rewards:"  + str(agent.processing.monitoring["cumulatedRewards"]))
        #     print(agent.processing.learning.qTable)
        #     print("----------------------")            

        pygame.quit()
        return str(measFolderPath) + filenameExperiment
