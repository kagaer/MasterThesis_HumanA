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

class AdditionalInfo(enum.Enum):
    AlgorithmStartPoint = 1
    EdgeCoordinatesReduced = 2
    EdgeToEdge = 3
    WasAmbigous = 4
    FirstDPofNode = 5
    LastDPofNode = 6
    Updated = 7

class GraphElements(enum.Enum):    
    Node = 1
    Edge = 2
    Undefined = 3


def create_reduced_db_table():

    """create a table in the database that stores the information for the reduced data

    Returns:
    """

    sql_instruction = """
    CREATE TABLE IF NOT EXISTS "dataPoints_reduced"(
    "Id" INTEGER NOT NULL UNIQUE,
    "TrialId" INTEGER NOT NULL,
    "DatapointId" INTEGER NOT NULL,
    "timeStampDataPointStart" NUMERIC,
    "timeStampDataPointEnd" NUMERIC,
    "playerBodyPosition_x" NUMERIC,
    "playerBodyPosition_y" NUMERIC,
    "playerBodyPosition_z" NUMERIC,
    "X_coor_converted" NUMERIC,
    "Z_coor_converted" NUMERIC,
    "X_coor_converted_precise" NUMERIC,
    "Z_coor_converted_precise" NUMERIC,
    "graph_element_type" TEXT,
    "node" NUMERIC,
    "edge_start" NUMERIC,
    "edge_end" NUMERIC,
    "validDatapoint" TEXT,
    "AdditionalInfo" TEXT,
    PRIMARY KEY ("Id" AUTOINCREMENT)
    FOREIGN KEY(TrialId) REFERENCES trials(Id)
    FOREIGN KEY(DatapointId) REFERENCES data_points(Id)
    FOREIGN KEY(node) REFERENCES graph_coordinates(nodeNr)
    FOREIGN KEY(edge_start) REFERENCES graph_coordinates(edgeStart)
    FOREIGN KEY(edge_end) REFERENCES graph_coordinates(edgeEnd)
    );
    """
    cr.execute(sql_instruction)
    connection.commit()

def getParticipants():
    """get all participantIds from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = """
    SELECT DISTINCT participantId FROM trials WHERE validParticipant = 'VALID';
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
    WHERE participantId = {participant} AND validSession = 'VALID';
    """
    
    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    return trialIdx

def getDatapoints(trial):
    """get all datapoints for the current trial, sorted by the timestamp (timeStampDataPointStart), and joined with the trialId and participantId

    Args:
        trial (int): current trial

    Returns:
        list: all datapoints for this trial 
    """

    sql_instruction = f"""
    SELECT trials.participantId, trials.id, data_points.Id, data_points.timeStampDataPointStart, timeStampDataPointEnd,
        data_points.playerBodyPosition_x, data_points.playerBodyPosition_y, 
        data_points.playerBodyPosition_z
    FROM trials
    LEFT JOIN data_points ON trials.id = data_points.trialId
    WHERE trials.id = {trial}
    ORDER BY data_points.timeStampDataPointStart ASC
    ;
        """
    cr.execute(sql_instruction)
    data = cr.fetchall()
    return data

def createColumnForNodes():
    # see if column already exists in database, add only if not exists
    sql_instruction = """SELECT COUNT(*) FROM
            PRAGMA_TABLE_INFO('data_points')
            WHERE name='AssignedNode';"""
    cr.execute(sql_instruction)
    nr_tables = cr.fetchone()
    if nr_tables[0] == 0:
        sql_instruction = """ALTER TABLE data_points ADD COLUMN AssignedNode NUMERIC"""
        cr.execute(sql_instruction)
        connection.commit()

def getMinNodeForDP(x_coor, z_coor):
    centroidX = []
    centroidZ = []
    Radius  = []
    Distance  = []
    minNodes  = []


    sql_instruction = f"""SELECT DISTINCT nodeNr, nodeCentroid_x, nodeCentroid_z, nodeRadius, ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
            ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z)) AS Distance
        FROM graph_coordinates 
        WHERE ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
                ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z)) = (
                SELECT MIN(ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
                    ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z))) 
                FROM graph_coordinates
                WHERE ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
                ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z)) <= graph_coordinates.nodeRadius*graph_coordinates.nodeRadius)"""
    cr.execute(sql_instruction)
    minNodes = cr.fetchall()
    if len(minNodes) == 1:
        
        centroidX = minNodes[0][1]
        centroidZ = minNodes[0][2]
        Radius = minNodes[0][3]
        Distance = minNodes[0][4]
        minNodes = minNodes[0][0]
    return minNodes, centroidX, centroidZ, Radius, Distance

def isSameNode(node,centroidX, centroidZ, Radius, x_coor, z_coor):
    def getDistance(pointA, pointB):
        return np.sqrt( (pointB[0] - pointA[0])**2 + (pointB[1] - pointA[1])**2 )
        #return distance
    
    distance = getDistance((x_coor, z_coor), (centroidX, centroidZ))
    if distance <= Radius:
        return True
    else:
        return False
    
    #minNodes = []
    #if node != []:
        
        #sql_instruction = f"""SELECT DISTINCT nodeNr, nodeCentroid_x, nodeCentroid_z, nodeRadius, ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
        #        ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z)) AS Distance
        #    FROM graph_coordinates 
        #    WHERE ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
        #            ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z)) = (
        #            SELECT MIN(ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
        #                ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z))) 
        #            FROM graph_coordinates
        #            WHERE ABS(({x_coor} - graph_coordinates.nodeCentroid_x)*({x_coor} - graph_coordinates.nodeCentroid_x) + 
        #            ({z_coor} - graph_coordinates.nodeCentroid_z)*({z_coor} - graph_coordinates.nodeCentroid_z)) <= graph_coordinates.nodeRadius*graph_coordinates.nodeRadius)
        #            AND nodeNr = {node}"""
        #cr.execute(sql_instruction)
        #minNodes = cr.fetchall()
        #if len(minNodes) == 1:
        #    minNodes = minNodes[0][0]
    
    #if minNodes == node and minNodes != []:
    #    return True 
    #else:
    #    return False

def trial_in_db(trial):
    """check if the current trial is already in the database (reduced data table)

    Args:
        trial (int): current trialId

    Returns:
        bool: true if trial is in database
    """

    sql_instruction = """
    SELECT TrialId FROM dataPoints_reduced
    """
    cr.execute(sql_instruction)
    content = cr.fetchall()
    if (trial,) in content:
        return True
    else:
        return False

def convert_coordinate(coordinate:Union[Tuple[float,float], List[float]], meters:int)->Tuple[int, int]:
    """convert coordinates to pixel value

    Args:
        coordinate (float): pair of x and y coordinates to be converted
        meters (int): size of the pixel value of the graph

    Returns:
        tuple: pair of converted x and y coordinates (int)
    """
    step = meters
    x = round((np.abs(xMin) + coordinate[0]) / step)
    y = round((np.abs(zMin) + coordinate[1]) / step)
    return x, y

def convert_coordinate_more_precise(coordinate:Union[Tuple[float,float], List[float]], meters:int)->Tuple[float, float]:
    """convert coordinates to a more precise pixel value

    Args:
        coordinate (float): pair of x and y coordinates to be converted
        meters (int): size of the pixel value of the graph

    Returns:
        tuple: pair of converted x and y coordinates (float)
    """
    step = meters
    x = (np.abs(xMin) + coordinate[0]) / step
    y = (np.abs(zMin) + coordinate[1]) / step
    return x, y

def addNodeToDB(datapoint,element, validity, additionalInfo):
    coor = (datapoint[5], datapoint[7])
    coor_conv = convert_coordinate(coor,4)
    coor_conv_prec = convert_coordinate_more_precise(coor,4)
    datapoint = list(datapoint[1:])
    valuesForDb = datapoint + [coor_conv[0], coor_conv[1], coor_conv_prec[0], coor_conv_prec[1], 
        str(GraphElements(1).name), element, validity]
    if additionalInfo is None:
        valuesForDb = tuple(valuesForDb)
        sql_instruction = f"""INSERT INTO dataPoints_reduced (TrialId, DatapointId, timeStampDataPointStart, 
                                            timeStampDataPointEnd, playerBodyPosition_x, playerBodyPosition_y, 
                                            playerBodyPosition_z, X_coor_converted, Z_coor_converted, X_coor_converted_precise, 
                                            Z_coor_converted_precise, graph_element_type, node, validDatapoint)
                                            VALUES {valuesForDb};"""
    else:
        valuesForDb += [additionalInfo]
        valuesForDb = tuple(valuesForDb)
        sql_instruction = f"""INSERT INTO dataPoints_reduced (TrialId, DatapointId, timeStampDataPointStart, 
                                    timeStampDataPointEnd, playerBodyPosition_x, playerBodyPosition_y, 
                                    playerBodyPosition_z, X_coor_converted, Z_coor_converted, X_coor_converted_precise, 
                                    Z_coor_converted_precise, graph_element_type, node, validDatapoint, AdditionalInfo)
                                    VALUES {valuesForDb};"""
        
    cr.execute(sql_instruction)

def addDPForEdge(datapoint):
    coor = (datapoint[5], datapoint[7])
    coor_conv = convert_coordinate(coor,4)
    coor_conv_prec = convert_coordinate_more_precise(coor,4)
    datapoint = list(datapoint[1:])
    valuesForDb = datapoint + [coor_conv[0], coor_conv[1], coor_conv_prec[0], coor_conv_prec[1]]
    valuesForDb = tuple(valuesForDb)
    sql_instruction = f"""INSERT INTO dataPoints_reduced (TrialId, DatapointId, timeStampDataPointStart, 
                                        timeStampDataPointEnd, playerBodyPosition_x, playerBodyPosition_y, 
                                        playerBodyPosition_z, X_coor_converted, Z_coor_converted, X_coor_converted_precise, 
                                        Z_coor_converted_precise)
                                        VALUES {valuesForDb};"""
        
    cr.execute(sql_instruction)


xMin, xMax, zMin, zMax = -442.87, 439.76, -280.14, 301.68
create_reduced_db_table()
createColumnForNodes()
participants = getParticipants()


for participant in participants: 
    trials = getTrialNrs(participant)
    for trial in trials:         
        if not trial_in_db(trial):
            print("Participant: " + str(participant) + " TrialId: " + str(trial))
            lastNode = []
            lastDP = []
            firstDatapoint = True
            data = getDatapoints(trial)
            for datapoint in data:
                x_coor = datapoint[5]
                z_coor = datapoint[7]
                coor_conv = convert_coordinate_more_precise([x_coor,z_coor],4)
                if firstDatapoint:
                    minNode, centroidX, centroidZ, radius, distance = getMinNodeForDP(coor_conv[0], coor_conv[1])
                    if minNode != []:
                        addNodeToDB(datapoint, minNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(5).name))
                        #print("New Node in Trial: " + str(minNode))
                    else:
                        addDPForEdge(datapoint) 
                    firstDatapoint = False
                else:
                    if lastNode == [] and minNode == []:
                        minNode, centroidX, centroidZ, radius, distance = getMinNodeForDP(coor_conv[0], coor_conv[1])
                        if minNode != []:
                            addNodeToDB(datapoint, minNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(5).name))
                            #print("New Node in Trial: " + str(minNode)) 
                    elif not isSameNode(lastNode,centroidX, centroidZ, radius,coor_conv[0], coor_conv[1]):                       
                        minNode, centroidX, centroidZ, radius, distance = getMinNodeForDP(coor_conv[0], coor_conv[1])
                        if minNode != [] and lastNode != []:
                            #print("From Node to Node: " + str(minNode))
                            addNodeToDB(lastDP, lastNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(6).name))
                            addNodeToDB(datapoint, minNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(5).name))
                        elif minNode != [] and lastNode == []:
                            #print("From Node to Edge: " + str(minNode))
                            addNodeToDB(datapoint, minNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(5).name))
                            addDPForEdge(lastDP)
                        elif minNode == [] and lastNode != []:
                            #print("From Edge To Node: " + str(lastNode))
                            addNodeToDB(lastDP, lastNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(6).name))
                            addDPForEdge(datapoint)

                            #addNodeToDB(datapoint, minNode, str(ValidityDatapoints(1).name), str(AdditionalInfo(5).name))


                lastNode = minNode
                lastDP = datapoint
        connection.commit()
print("All Nodes added")
connection.close()