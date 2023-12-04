import sqlite3
from pathlib import Path
import pandas
import matplotlib.pyplot as plt

savepath = "E:/HumanA/Analysis/Descriptives/"
# path to databases
print("For which experiment would you like to analyize the data?")
experiment = int(input())
if experiment == 1:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp1.db')
    savepath = savepath + "Exp1/"

elif experiment == 2:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp2.db')
    savepath = savepath + "Exp2/"

# check if path exists
if not db_path or not db_path.exists():
    db_path = ':memory:'

# connect to database
connection=sqlite3.connect(db_path)
cr=connection.cursor()

def getDataFromDB():
    sql_instruction = """SELECT trials.participantId, trials.sessionNr, trials.id, dataPoints_analysis.DatapointId, dataPoints_analysis.node, 
                        participant_decision.last_node_neighbour,participant_decision.decision
                        FROM trials
                        LEFT JOIN dataPoints_analysis ON trials.id = dataPoints_analysis.trialId
                        LEFT JOIN participant_decision ON dataPoints_analysis.datapointId = participant_decision.DatapointId
                        WHERE validSession = 'VALID' AND validParticipant = 'VALID'
                        ORDER BY trials.participantId, trials.sessionNr, dataPoints_analysis.timeStampDataPointStart;"""
    cr.execute(sql_instruction)
    df = pandas.DataFrame(cr.fetchall())
    df = df.rename(columns = {0 : 'ParticipantID', 1: 'SessionNr', 2: 'TrialId', 3: 'DatapointID', 4: 'Node', 5: 'LastNode_Neighbour', 6: 'Decision' })
    return df

data = getDataFromDB()


