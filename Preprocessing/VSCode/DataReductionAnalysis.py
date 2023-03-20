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

def create_analysis_db_table():

    """create a table in the database that stores the information for the reduced data

    Returns:
    """

    sql_instruction = """
    CREATE TABLE IF NOT EXISTS "dataPoints_analysis"(
    "Id" INTEGER NOT NULL UNIQUE,
    "TrialId" INTEGER NOT NULL,
    "DatapointId" INTEGER NOT NULL,
    "timeStampDataPointStart" NUMERIC,
    "node" NUMERIC,
    "validDatapoint" TEXT,
    "AdditionalInfo" TEXT,
    PRIMARY KEY ("Id" AUTOINCREMENT)
    FOREIGN KEY(TrialId) REFERENCES trials(Id)
    FOREIGN KEY(DatapointId) REFERENCES data_points(Id)
    FOREIGN KEY(node) REFERENCES graph_coordinates(nodeNr)
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
    WHERE participantId = {participant} AND id NOT IN (SELECT DISTINCT trialId FROM dataPoints_analysis);
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
    SELECT trialId,DatapointId, timeStampDataPointStart,node,validDatapoint,AdditionalInfo
    FROM dataPoints_reduced WHERE trialId = {trial} AND (ValidDatapoint = 'VALID' OR ValidDatapoint = 'ADJUSTED')
    ORDER BY dataPoints_reduced.timeStampDataPointStart ASC
    ;
        """
    cr.execute(sql_instruction)
    data = cr.fetchall()
    return data

def trial_in_db(trial):
    """check if the current trial is already in the database (analysis data table)

    Args:
        trial (int): current trialId

    Returns:
        bool: true if trial is in database
    """

    sql_instruction = """
    SELECT TrialId FROM dataPoints_analysis
    """
    cr.execute(sql_instruction)
    content = cr.fetchall()
    if (trial,) in content:
        return True
    else:
        return False

def addNodeToDB(datapoint):
    #if datapoint[3] is not None and datapoint[4] is not None:
    #    sql_instruction = f"""INSERT INTO dataPoints_analysis (TrialId, DatapointId, timeStampDataPointStart,X_coor_converted_precise,Z_coor_converted_precise,node, 
    #        validDatapoint, AdditionalInfo)
    #        VALUES {datapoint};"""
    #else:

    #datapoint = (datapoint[0],datapoint[1], datapoint[2], datapoint[5], datapoint[6], datapoint[7])
    sql_instruction = f"""INSERT INTO dataPoints_analysis (TrialId, DatapointId, timeStampDataPointStart,node, 
        validDatapoint, AdditionalInfo)
        VALUES {datapoint};"""
        
    cr.execute(sql_instruction)

create_analysis_db_table()
participants = getParticipants()
for participant in participants:
    trials = getTrialNrs(participant)
    for trial in trials:
        last_dp = []
        #if not trial_in_db(trial):
        
        data = getDatapoints(trial)
        if data != []:
            print("Participant: " +str(participant) + " Trial: " + str(trial))
        for datapoint in data:
            if last_dp == []:
                addNodeToDB(datapoint)
            elif last_dp[3] != datapoint[3]:
                addNodeToDB(datapoint)
            last_dp = datapoint
        connection.commit()
print("All done")
