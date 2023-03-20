import sqlite3
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
import enum

# path to databases
print("For which experiment would you like to reduce the data?")
experiment = int(input())
if experiment == 1:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp1.db')
    #db_path = Path('E:/HumanA/Data/HumanA_Exp1_WorkingData.db')
elif experiment == 2:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp2.db')
    #db_path = Path('E:/HumanA/Data/HumanA_Exp2_WorkingData.db')

# check if path exists
if not db_path or not db_path.exists():
    db_path = ':memory:'

# connect to database
connection=sqlite3.connect(db_path)
cr=connection.cursor()

class ValidityDatapoints(enum.Enum):
    VALID = 1
    ADJUSTED = 2
    INVALID = 3
    IRRELEVANT = 4

class AdditionalInfo(enum.Enum):
    AlgorithmStartPoint = 1
    EdgeCoordinatesReduced = 2
    EdgeToEdge = 3
    WasAmbigous = 4
    FirstDPofNode = 5
    LastDPofNode = 6
    Updated = 7
    SameNode = 8
    NeighbouringNode = 9
    ShortestDistance = 10


def getParticipants():
    """get all participantIds from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = """
    SELECT DISTINCT participantId FROM trials
    WHERE validParticipant = 'VALID' ;
    """
    cr.execute(sql_instruction)
    participants = tuple(did[0] for did in cr.fetchall())
    return participants

def getTrialNrs(participant):
    """get all trialIds for the current participant

    Args:
        participant (int): current participant

    Returns:
        tuple: all trialIds 
    """

    sql_instruction = f"""
    SELECT DISTINCT id 
    FROM trials
    WHERE participantId = {participant} AND id NOT IN (SELECT DISTINCT trialId FROM dataPoints_analysis)
    ;
    """

    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    return trialIdx

def getMissingElementDatapoints(trial):
    """get all datapoints for the current trial, sorted by the timestamp (timeStampDataPointStart), and joined with the trialId and participantId

    Args:
        trial (int): current trial

    Returns:
        list: all datapoints for this trial 
    """

    sql_instruction = f"""
    SELECT dataPoints_reduced.DatapointId, dataPoints_reduced.timeStampDataPointStart,dataPoints_reduced.graph_element_type, 
    dataPoints_reduced.node, dataPoints_reduced.AdditionalInfo
    FROM dataPoints_reduced
    WHERE dataPoints_reduced.trialId = {trial} AND dataPoints_reduced.graph_element_type IS NULL
    ORDER BY dataPoints_reduced.timeStampDataPointStart ASC
    ;
        """
    cr.execute(sql_instruction)
    data = cr.fetchall()
    return data

def getPreviousAndNextKnownDatapoints(trialId, datapointId):
    sql_instruction = f"""SELECT datapointId, node 
        FROM dataPoints_reduced 
        WHERE datapointId IN (SELECT MAX(datapointId) 
            FROM dataPoints_reduced 
            WHERE (datapointId < {datapointId} AND TrialId = {trialId}))   
        OR datapointId IN (SELECT MIN(datapointId) 
            FROM dataPoints_reduced 
            WHERE (datapointId > {datapointId} AND TrialId = {trialId}))"""
    
    cr.execute(sql_instruction)
    data = cr.fetchall()
    if len(data) > 1:
        previousNode = data[0][1]
        nextNode = data[1][1]
    else:
        previousNode = None
        nextNode = None
    return previousNode,nextNode

def isTrialAdjusted(trial):
    sql_instruction = f"""SELECT id 
    FROM trials 
    WHERE id = {trial}   
    AND adjusted IS NULL"""
    cr.execute(sql_instruction)
    trialInDB = cr.fetchall()
    if (trial,) in trialInDB:
        return False
    else: 
        return True

def updateDatapointInDB(datapointId,element, additionalInfo):
    validity = str(ValidityDatapoints(2).name)
    if isinstance(element, int):
        sql_instruction = f""" UPDATE dataPoints_reduced SET graph_element_type = 'Node', node = {element}, validDatapoint = '{validity}', 
                additionalInfo = '{additionalInfo}'
            WHERE datapointId = {datapointId} AND validDatapoint IS NULL"""
    elif isinstance(element,list):
        sql_instruction = f""" UPDATE dataPoints_reduced SET graph_element_type = 'Edge', edge_start = {element[0]},edge_end = {element[1]}, 
                validDatapoint = '{validity}', additionalInfo = '{additionalInfo}'
            WHERE datapointId = {datapointId} AND validDatapoint IS NULL"""
    cr.execute(sql_instruction)

def updateDatapointIrrelevant(datapointId,additionalInfo):
    validity = str(ValidityDatapoints(4).name)
    #additionalInfo = str(AdditionalInfo(9).name)
    sql_instruction = f""" UPDATE dataPoints_reduced SET validDatapoint = '{validity}', additionalInfo = '{additionalInfo}'
    WHERE datapointId = {datapointId} AND validDatapoint IS NULL"""
    cr.execute(sql_instruction)

def datapointInReducedDP(dpId):
    sql_instruction = f"""SELECT * FROM dataPoints_reduced WHERE DatapointId = {dpId}"""
    cr.execute(sql_instruction)
    content = cr.fetchall()
    if content != []:
        return True
    else: 
        return False

def getPlaceholderDatapoints(trial, dp_id,datapointIds):
    isInDBIds = False
    for id in range(datapointIds[0], datapointIds[1]+1):
        if id != dp_id:
            isInDBIds = datapointInReducedDP(id)
        #if not datapointInReducedDP(id):
    if not isInDBIds:
        sql_instruction = f"""SELECT * FROM data_points WHERE (id BETWEEN {datapointIds[0]} AND {datapointIds[1]}) 
            AND trialId = {trial}"""
        cr.execute(sql_instruction)
        datapoints = cr.fetchall()
    else:    
            print("Ids are already in Database")
    return datapoints
    #TODO: insert into reduced table & add additional Information

def addPlaceholderDatapoint(datapoint,node):
    validity = str(ValidityDatapoints(2).name)
    additionalInfo = str(AdditionalInfo(10).name)
    values = str((datapoint[1],datapoint[0],datapoint[2],datapoint[3] ,datapoint[4],datapoint[5],datapoint[6], 
        'Node', node,validity, additionalInfo))
    sql_instruction = f"""INSERT INTO dataPoints_reduced (TrialId, DatapointId, timeStampDataPointStart, 
                            timeStampDataPointEnd, playerBodyPosition_x, playerBodyPosition_y, 
                            playerBodyPosition_z, graph_element_type, node, validDatapoint, additionalInfo)
                            VALUES {values}"""
    cr.execute(sql_instruction)
    #connection.commit()


def getNodesNeighbours(nodes):
    if isinstance(nodes, int):
        sql_instruction = f"""SELECT * FROM node_neighbours WHERE FirstNode = {nodes} or SecondNode = {nodes}"""
    else:
        sql_instruction = f"""SELECT * FROM node_neighbours WHERE FirstNode IN {nodes} or SecondNode IN {nodes}"""
    cr.execute(sql_instruction)
    all_neighbours = cr.fetchall()
    neighbours = []

    if isinstance(nodes, int):
        neighbours = all_neighbours
        #for neighbour in all_neighbours:
            #if neighbour[0] == nodes:
            #    neighbours.append(neighbour[1])
            #if neighbour[1] == nodes:
            #    neighbours.append(neighbour[0])    
    else:
        for node in nodes:
            for neighbour in all_neighbours:
                if neighbour not in neighbours:
                    neighbours.append(neighbour)
                #if neighbour[0] == node:
                #    neighbours.append(neighbour[1])
                #if neighbour[1] == node:
                #    neighbours.append(neighbour[0])
    return neighbours


def findShortestPath(startNode, destinationNode, rec_depth = 0):
    #startNode = tuple(startNode)
    rec_depth += 1
    #if startNode is None:
    #    print("")
    neighbours_startNode = getNodesNeighbours(startNode)
    #first_nodes = [node1 for node1, node2 in neighbours_startNode]
    #second_nodes = [node2 for node1,node2 in neighbours_startNode]
    #path = []
    path = [item for item in neighbours_startNode if destinationNode in item]
    if path != []:
        neighbour = [node for node in path[0] if node != destinationNode]
        path = [neighbour[0],destinationNode]
        #path = path[0]
    else:
        neighbours = [node for neighbours in neighbours_startNode for node in neighbours]
        neighbours = tuple([*set(neighbours)]) 
        if rec_depth <= 20:  
            path =  findShortestPath(neighbours, destinationNode, rec_depth)
            #if len(path) == 2:
            #    neighbouringNode = [node for node in path if node != destinationNode]
            #    neighbouringNode = neighbouringNode[0]
            #else:
            if path != []:
                neighbouringNode = path[0]
                if neighbouringNode != []:
                    previousConnection = [item for item in neighbours_startNode if neighbouringNode in item]
                    previousNode = [node for node in previousConnection[0] if node != neighbouringNode]
                    if previousNode[0] not in path:
                        path.insert(0,previousNode[0])
        else:
            path = []
        #if path != [] and neighbouringNode not in path:
        #    path.insert(0,neighbouringNode)
        #    print("Yay")
        
    #if destinationNode in first_nodes:
    #    index = neighbours_startNode.index(destinationNode)
    #    path = [neighbours_startNode[index],destinationNode]
    #    print("Path: " + str(path))
    #    #TODO: destinationNode is neighbour of Startnode
    #else:
    #    neighbours_startNode = tuple(neighbours_startNode)
    #    path = findShortestPath(neighbours_startNode, destinationNode)

    #neighbours_destinationNode = getNodesNeighbours(destinationNode)
    return list(path)

def createColumnForAdjustInfo():
    # see if column already exists in database, add only if not exists
    sql_instruction = """SELECT COUNT(*) FROM
            PRAGMA_TABLE_INFO('trials')
            WHERE name='adjusted';"""
    cr.execute(sql_instruction)
    nr_tables = cr.fetchone()
    if nr_tables[0] == 0:
        sql_instruction = """ALTER TABLE trials ADD COLUMN adjusted TEXT"""
        cr.execute(sql_instruction)
        connection.commit()

def trial_in_db(trial):
    """check if the current trial is already in the database (participant_decision)

    Args:
        trial (int): current trialId

    Returns:
        bool: true if trial is in database
    """

    sql_instruction = """
    SELECT DISTINCT trialId FROM datapoints_reduced
    """
    cr.execute(sql_instruction)
    content = cr.fetchall()
    if (trial,) in content:
        return True
    else:
        return False

createColumnForAdjustInfo()

participants = getParticipants()
countEdgeToEdge = 0
for participant in participants:
    trials = getTrialNrs(participant)
    for trial in trials:
        if trial_in_db(trial):
            if not isTrialAdjusted(trial):
                print("Participant: " +str(participant) + " Trial: " + str(trial))
                missingElementData = getMissingElementDatapoints(trial)
                for datapoint in missingElementData:

                    dp_id = datapoint[0]
                    previousNode, nextNode = getPreviousAndNextKnownDatapoints(trial,dp_id)
                    if previousNode is not None and nextNode is not None:
                        if previousNode == nextNode:
                            additionalInfo = str(AdditionalInfo(8).name)
                            updateDatapointIrrelevant(dp_id,additionalInfo)
                            #updateDatapointInDB(dp_id,previousNode,additionalInfo)
                            "Do some fancy stuff"
                            #TODO: just add same node to db for that missing dp
                        elif previousNode != nextNode:
                            shortestPath = findShortestPath(previousNode,nextNode)
                            if len(shortestPath) == 2:
                                additionalInfo = str(AdditionalInfo(9).name)
                                updateDatapointIrrelevant(dp_id,additionalInfo)
                                # Start node and Destination are neighbours
                                #TODO: Delete datapoint
                                "Neighbouring Nodes"
                                #print("StartNode: " + str(previousNode) + " EndNode: " + str(nextNode) )
                                #print("Shortest Path: " + str(shortestPath))
                            elif len(shortestPath) > 2:                 
                                print("StartNode: " + str(previousNode) + " EndNode: " + str(nextNode) )
                                print("Shortest Path: " + str(shortestPath))
                                #next_dp_id = dp_id+1
                                datapointIds = (dp_id, (dp_id + len(shortestPath)-3))
                                placeh_datapoints = getPlaceholderDatapoints(trial,dp_id, datapointIds)
                                for node, datapoint in zip(shortestPath[1:-1], placeh_datapoints):
                                    #if datapoint[]
                                    if datapoint[0] == dp_id:
                                        updateDatapointInDB(dp_id,node,str(AdditionalInfo(10).name))
                                    else:
                                        addPlaceholderDatapoint(datapoint, node)
                                    #if node != previousNode and node != nextNode:
                                    #    for datapoint in placeh_datapoints:


                                countEdgeToEdge += 1
                            elif len(shortestPath) == 0:
                                print("StartNode: " + str(previousNode) + " EndNode: " + str(nextNode) )
                                print("Could not find a connection between nodes with less than 20 steps")
                            "Do some fancy stuff"

            sql_instruction = f""" UPDATE trials SET adjusted = 'TRUE'
            WHERE id = {trial}"""
            cr.execute(sql_instruction)                #TODO: check for the shortest distance between nodes
            connection.commit()
print("All paths fixed")
print("Total number of multiple EdgeToEdge: " + str(countEdgeToEdge))
