import json
from pathlib import Path
import sqlite3
import os
import re

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


DATAPOINT_FIELDS = (
    'timeStampDataPointStart',
    'timeStampDataPointEnd',
    'timeStampGetVerboseData',
    'eyeOpennessLeft',
    'eyeOpennessRight',
    'pupilDiameterMillimetersLeft',
    'pupilDiameterMillimetersRight',
    'eyePositionCombinedWorld_x',
    'eyePositionCombinedWorld_y',
    'eyePositionCombinedWorld_z',
    'eyeDirectionCombinedWorld_x',
    'eyeDirectionCombinedWorld_y',
    'eyeDirectionCombinedWorld_z',
    'eyeDirectionCombinedLocal_x',
    'eyeDirectionCombinedLocal_y',
    'eyeDirectionCombinedLocal_z',
    'eyePositionLeftWorld_x',
    'eyePositionLeftWorld_y',
    'eyePositionLeftWorld_z',
    'eyeDirectionLeftWorld_x',
    'eyeDirectionLeftWorld_y',
    'eyeDirectionLeftWorld_z',
    'eyeDirectionLeftLocal_x',
    'eyeDirectionLeftLocal_y',
    'eyeDirectionLeftLocal_z',
    'eyePositionRightWorld_x',
    'eyePositionRightWorld_y',
    'eyePositionRightWorld_z',
    'eyeDirectionRightWorld_x',
    'eyeDirectionRightWorld_y',
    'eyeDirectionRightWorld_z',
    'eyeDirectionRightLocal_x',
    'eyeDirectionRightLocal_y',
    'eyeDirectionRightLocal_z',
    'leftGazeValidityBitmask',
    'rightGazeValidityBitmask',
    'hmdPosition_x',
    'hmdPosition_y',
    'hmdPosition_z',
    'hmdDirectionForward_x',
    'hmdDirectionForward_y',
    'hmdDirectionForward_z',
    'hmdDirectionRight_x',
    'hmdDirectionRight_y',
    'hmdDirectionRight_z',
    'hmdRotation_x',
    'hmdRotation_y',
    'hmdRotation_z',
    'hmdDirectionUp_x',
    'hmdDirectionUp_y',
    'hmdDirectionUp_z',
    'handLeftPosition_x',
    'handLeftPosition_y',
    'handLeftPosition_z',
    'handLeftRotation_x',
    'handLeftRotation_y',
    'handLeftRotation_z',
    'handLeftScale_x',
    'handLeftScale_y',
    'handLeftScale_z',
    'handLeftDirectionForward_x',
    'handLeftDirectionForward_y',
    'handLeftDirectionForward_z',
    'handLeftDirectionRight_x',
    'handLeftDirectionRight_y',
    'handLeftDirectionRight_z',
    'handLeftDirectionUp_x',
    'handLeftDirectionUp_y',
    'handLeftDirectionUp_z',
    'handRightPosition_x',
    'handRightPosition_y',
    'handRightPosition_z',
    'handRightRotation_x',
    'handRightRotation_y',
    'handRightRotation_z',
    'handRightScale_x',
    'handRightScale_y',
    'handRightScale_z',
    'handRightDirectionForward_x',
    'handRightDirectionForward_y',
    'handRightDirectionForward_z',
    'handRightDirectionRight_x',
    'handRightDirectionRight_y',
    'handRightDirectionRight_z',
    'handRightDirectionUp_x',
    'handRightDirectionUp_y',
    'handRightDirectionUp_z',
    'playerBodyPosition_x',
    'playerBodyPosition_y',
    'playerBodyPosition_z',
    'bodyTrackerPosition_x',
    'bodyTrackerPosition_y',
    'bodyTrackerPosition_z',
    'bodyTrackerRotation_x',
    'bodyTrackerRotation_y',
    'bodyTrackerRotation_z',
)

RAYCAST_FIELDS = (
    'hitPointOnObject_x',
    'hitPointOnObject_y',
    'hitPointOnObject_z',
    'hitObjectColliderName',
    'hitColliderType',
    'hitObjectColliderBoundsCenter_x',
    'hitObjectColliderBoundsCenter_y',
    'hitObjectColliderBoundsCenter_z',
    'ordinalOfHit',
)

def _extract_dataPoints(dataPoint):
    def get(field:str):
        if '_x' in field:
            return dataPoint[field[:-2]]['x']
        elif '_y' in field:
            return dataPoint[field[:-2]]['y']
        elif '_z' in field:
            return dataPoint[field[:-2]]['z']
        else:
            return dataPoint[field]
    return (get(field)for field in DATAPOINT_FIELDS)

# TODO: can you make this more efficient? 
def _extract_rayCastHits(rayCast):
    def get(field:str):
        if '_x' in field:
            if isinstance(rayCast[field[:-2]]['x'],str):
                rayCastStr = rayCast[field[:-2]]['x']
                return f'"{rayCastStr}"'
            else:
                return rayCast[field[:-2]]['x']
        elif '_y' in field:
            if isinstance(rayCast[field[:-2]]['y'],str):
                rayCastStr = rayCast[field[:-2]]['y']
                return f'"{rayCastStr}"'
            else:
                return rayCast[field[:-2]]['y']
        elif '_z' in field:
            if isinstance(rayCast[field[:-2]]['z'],str):
                rayCastStr = rayCast[field[:-2]]['z']
                return f'"{rayCastStr}"'
            else:
                return rayCast[field[:-2]]['z']
        else:
            if isinstance(rayCast[field],str):
                rayCastStr = rayCast[field]
                return f'"{rayCastStr}"'
            else:
                return rayCast[field]
    return (get(field)for field in RAYCAST_FIELDS)

def set_up_db():
    cr.execute("""
        CREATE TABLE IF NOT EXISTS "trials" (
            "id"	INTEGER NOT NULL UNIQUE,
            "participantId" INTEGER,
            "sessionNr" INTEGER,
            "trialId"	INTEGER,
            "fileName"	TEXT NOT NULL UNIQUE,
            "someRandomInformation"	TEXT,
            "timeTrialMeasurementStarted"	NUMERIC,
            "timeTrialMeasurementStopped"	NUMERIC,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """)

    data_structure = ',\n'.join(f"{field} NUMERIC" for field in DATAPOINT_FIELDS)
    cr.execute(f"""
    CREATE TABLE IF NOT EXISTS "data_points" (
        "id"	INTEGER NOT NULL UNIQUE,
        trialId INTEGER NOT NULL,
        {data_structure},
        PRIMARY KEY("id" AUTOINCREMENT)
        FOREIGN KEY(trialId) REFERENCES trials(id)
    );
    """)

    cr.execute(f"""
    CREATE TABLE IF NOT EXISTS "raycast_hits" (
        "id"	INTEGER NOT NULL UNIQUE,
        'datapointId' INTEGER NOT NULL,
        'hitPointOnObject_x' NUMERIC,
        'hitPointOnObject_y' NUMERIC,
        'hitPointOnObject_z' NUMERIC,
        'hitObjectColliderName' TEXT,
        'hitColliderType' TEXT,
        'hitObjectColliderBoundsCenter_x' NUMERIC,
        'hitObjectColliderBoundsCenter_y' NUMERIC,
        'hitObjectColliderBoundsCenter_z' NUMERIC,
        'ordinalOfHit' INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT)
        FOREIGN KEY(datapointId) REFERENCES data_points(id)
    );
    """)


def fileInDB(filename):
    # instruction to select all data from database
    sql_instruction = """
    SELECT fileName FROM trials
    """

    # show result
    cr.execute(sql_instruction)
    content = cr.fetchall()
    if (filename,) in content:
        return True
    else:
        return False

if __name__ == '__main__':
    connection=sqlite3.connect(db_path)
    cr=connection.cursor()
    set_up_db()
    obj = {}

    # READ RAW DATA
    for filename in os.listdir(path):
        if "Expl_" in filename:
            if "OnQuit" not in filename and "EyeValidation" not in filename:
                if not fileInDB(filename):
                    print(filename)
                    filepath = path/filename

                    # get participantID
                    regex_sub = '\A[0-9]{4}'
                    subId = re.findall(regex_sub, filename)
                    participantID = int(subId[0])

                    # get SessionNr
                    regex_ses = '_S_..'
                    ses_intermed = str(re.findall(regex_ses, filename))
                    regex_ses = '[1-5]'
                    sesId = re.findall(regex_ses, ses_intermed)
                    sessionNr = int(sesId[0])

                    # open file
                    with open(filepath) as json_file:
                        obj = json.load(json_file)

                    # add information to "trials table"
                    trial = obj['trials'][0]
                    trialId = cr.execute(f"""INSERT INTO trials
                        (participantId,sessionNr, trialId, fileName, someRandomInformation, timeTrialMeasurementStarted, timeTrialMeasurementStopped)
                        VALUES (
                            {participantID},{sessionNr}, {trial['trialId']}, '{str(filename)}', '{trial['someRandomInformation']}', 
                            {trial['timeTrialMeasurementStarted']}, {trial['timeTrialMeasurementStopped']}
                        );""").lastrowid

                    i = 0
                    j = 10000

                    # add information to "datapoints table" & "raycast table"
                    while trial['dataPoints'][i:j]:
                        print(f'EXECUTE {i} to {j}')
                        values = (
                            str((trialId,) + tuple(_extract_dataPoints(dataPoint=dataPoint)))
                            for dataPoint in trial['dataPoints'][i:j]
                        )

                        stop_id = cr.execute(f"""INSERT INTO data_points
                            (trialId, {', '.join(DATAPOINT_FIELDS)})
                            VALUES {', '.join(values)}
                            ;""").lastrowid

                        ray_cast_values = ',\n'.join(
                            ', '.join(
                                (f'({stop_id-k}, {", ".join(str(v) for v in _extract_rayCastHits(rayCast))})')
                                for rayCast
                                in dataPoint['rayCastHitsCombinedEyes']
                            )
                            for k, dataPoint
                            in enumerate(reversed(trial['dataPoints'][i:j])) 
                            if dataPoint['rayCastHitsCombinedEyes']
                        )
                        cr.execute(f"""INSERT INTO raycast_hits
                            (datapointId, {', '.join(RAYCAST_FIELDS)})
                            VALUES {ray_cast_values}
                            ;""")
                        
                        i = j+1
                        j = j+10000
                    connection.commit()
print("Finished loading files into Database")
connection.close()
