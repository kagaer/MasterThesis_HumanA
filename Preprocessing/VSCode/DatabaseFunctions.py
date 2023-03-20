from pathlib import Path
import sqlite3
import enum
#from DatabaseFunctions import *

#print("For which experiment would you like to add Data to the Database?")
#experiment = int(input())
#if experiment == 1:
#    db_path = Path('E:/HumanA/Data/DataBase/HumanA_Exp1.db')
#    path = Path('E:/HumanA/Data/Exp1/')
#elif experiment == 2:
#    db_path = Path('E:/HumanA/Data/DataBase/HumanA_Exp2.db')
#    path = Path('E:/HumanA/Data/Exp2/')

#db_path = Path("E:/HumanA/Data/Database/test.db")
#
#if not db_path or not db_path.exists():
#    db_path = ':memory:'


#if not path.exists():
#    raise Exception('Path not exists')      

#connection=sqlite3.connect(db_path)
#cr=connection.cursor()

def getParticipants(cr):
    """get all participantIds from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = """
    SELECT DISTINCT participantId FROM trials;
    """
    cr.execute(sql_instruction)
    participants = tuple(did[0] for did in cr.fetchall())
    return participants

def getSessions(participant, cr):
    """get all sessionNrs for the current participant from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = f"""
    SELECT DISTINCT sessionNr FROM trials WHERE participantId = {participant}
    ORDER BY sessionNr;
    """
    cr.execute(sql_instruction)
    sessions = tuple(did[0] for did in cr.fetchall())
    return sessions

def getTrialNrs(participant, session, cr):
    """get all trialIds for the current participant, current session

    Args:
        participant (int): current participant

    Returns:
        tuple: all trialIds 
    """

    sql_instruction = f"""
    SELECT DISTINCT id 
    FROM trials
    WHERE participantId = {participant} AND sessionNr = {session} AND ((validSession IS NULL OR NOT validSession = 'INVALID') AND NOT validParticipant = 'INVALID')
    """
    
    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    return trialIdx

def getTrialsParticipant(participant, cr):
    """get all trialIds for the current participant

    Args:
        participant (int): current participant

    Returns:
        tuple: all trialIds 
    """

    sql_instruction = f"""
    SELECT DISTINCT id 
    FROM trials
    WHERE participantId = {participant} AND ((validSession IS NULL OR NOT validSession = 'INVALID') AND NOT validParticipant = 'INVALID')
    """
    
    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    return trialIdx
