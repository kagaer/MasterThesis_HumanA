from pathlib import Path
import sqlite3
import enum
from DatabaseFunctions import *

print("For which experiment would you like to add Data to the Database?")
experiment = int(input())
if experiment == 1:
    db_path = Path('E:/HumanA/Data/DataBase/HumanA_Exp1.db')
    path = Path('E:/HumanA/Data/Exp1/')
elif experiment == 2:
    db_path = Path('E:/HumanA/Data/DataBase/HumanA_Exp2.db')
    path = Path('E:/HumanA/Data/Exp2/')

#db_path = Path("E:/HumanA/Data/Database/test.db")

if not db_path or not db_path.exists():
    db_path = ':memory:'


if not path.exists():
    raise Exception('Path not exists')      

connection=sqlite3.connect(db_path)
cr=connection.cursor()

class Validity(enum.Enum):
    VALID = 1
    TOOSHORT = 2
    TOOLONG = 3


# TODO: Create column for trials with validity for session and participant
def addColumnToDBForValidity():
    # see if column already exists in database, add only if not exists
    sql_instruction = """SELECT COUNT(*) FROM
            PRAGMA_TABLE_INFO('trials')
            WHERE name='validSession';"""
    cr.execute(sql_instruction)
    nr_tables = cr.fetchone()
    if nr_tables[0] == 0:
        sql_instruction = """ALTER TABLE trials ADD COLUMN validSession TEXT"""
        cr.execute(sql_instruction)
        connection.commit()
    sql_instruction = """SELECT COUNT(*) FROM
            PRAGMA_TABLE_INFO('trials')
            WHERE name='validParticipant';"""
    cr.execute(sql_instruction)
    nr_tables = cr.fetchone()
    if nr_tables[0] == 0:
        sql_instruction = """ALTER TABLE trials ADD COLUMN validParticipant TEXT"""
        cr.execute(sql_instruction)

def checkValiditySessions():
    sql_instruction = f"""SELECT participantId, sessionNr, ROUND(SUM((timeTrialMeasurementStopped - timeTrialMeasurementStarted)/60),2) FROM trials
    WHERE validSession IS NULL OR NOT validSession = 'INVALID'
    GROUP BY participantId, sessionNr
    """
    cr.execute(sql_instruction)
    sessionInfo = cr.fetchall()

    for participantId, sessionNr, trialDuration in sessionInfo:
        trials = getTrialNrs(participantId, sessionNr, cr)
        if len(trials) == 1:
            if trialDuration < 29.99:
                sql_instruction = f"""UPDATE trials SET validSession = '{str(Validity(2).name)}' WHERE id = {trials[0]}"""
            elif trialDuration > 31.00:
                sql_instruction = f"""UPDATE trials SET validSession = '{str(Validity(3).name)}' WHERE id = {trials[0]}"""
            else:
                sql_instruction = f"""UPDATE trials SET validSession = '{str(Validity(1).name)}' WHERE id = {trials[0]}"""
        elif len(trials) > 1:
            if trialDuration < 29.99:
                sql_instruction = f"""UPDATE trials SET validSession = '{str(Validity(2).name)}' WHERE id IN {trials}"""
            elif trialDuration > 31.00:
                sql_instruction = f"""UPDATE trials SET validSession = '{str(Validity(3).name)}' WHERE id IN {trials}"""
            else:
                sql_instruction = f"""UPDATE trials SET validSession = '{str(Validity(1).name)}' WHERE id IN {trials}"""
        cr.execute(sql_instruction)
    connection.commit()
            
def checkValidityParticipant():
    sql_instruction = f"""SELECT participantId, ROUND(SUM((timeTrialMeasurementStopped - timeTrialMeasurementStarted)/60),2) FROM trials
    WHERE validSession IS NULL OR NOT validSession = 'INVALID'
    GROUP BY participantId
    """
    cr.execute(sql_instruction)
    participantInfo = cr.fetchall()

    for participantId, trialDuration in participantInfo:
        trials = getTrialsParticipant(participantId, cr)
        if len(trials) == 1:
            if trialDuration < 149.00:
                sql_instruction = f"""UPDATE trials SET validParticipant = '{str(Validity(2).name)}' WHERE id = {trials[0]}"""
            elif trialDuration > 151.00:
                sql_instruction = f"""UPDATE trials SET validParticipant = '{str(Validity(3).name)}' WHERE id = {trials[0]}"""
            else:
                sql_instruction = f"""UPDATE trials SET validParticipant = '{str(Validity(1).name)}' WHERE id = {trials[0]}"""
        elif len(trials) > 1:
            if trialDuration < 149.00:
                sql_instruction = f"""UPDATE trials SET validParticipant = '{str(Validity(2).name)}' WHERE id IN {trials}"""
            elif trialDuration > 151.00:
                sql_instruction = f"""UPDATE trials SET validParticipant = '{str(Validity(3).name)}' WHERE id IN {trials}"""
            else:
                sql_instruction = f"""UPDATE trials SET validParticipant = '{str(Validity(1).name)}' WHERE id IN {trials}"""
        cr.execute(sql_instruction)
    connection.commit()            


addColumnToDBForValidity()
checkValiditySessions()
checkValidityParticipant()
# TODO: check if the duration of the session is ~30min, if not session is invalid (if too long check session notes and manually adjust, 
# if there is something in the session notes)


# TODO: check if the duration of all sessions is ~150min, if not the participant is invalid


# get the total duration of sessions for the participant: less than ~150 minutes is not complete
sql_instruction = f"""SELECT participantId, ROUND(SUM((timeTrialMeasurementStopped - timeTrialMeasurementStarted)/60),2) AS trialDuration FROM trials
        GROUP BY participantId
        ORDER BY trialDuration"""