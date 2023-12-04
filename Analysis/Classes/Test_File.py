from StrategyMatrix import *
from AgentStrategyMatrix import *
from Matrixes import *
import sqlite3
from pathlib import Path


db_path = Path('E:/HumanA/Data/Database/HumanA_Exp1.db')
connection=sqlite3.connect(db_path)
cr=connection.cursor()

test_matrix = StrategyMatrix(participantId = 1754, cursor = cr)
agentTest_matrix = AgentStrategyMatrix(participantId = 1754, cursor = cr)
#weightedagentTest_matrix = AgentStrategyMatrix(participantId = 1754, cursor = cr, weight=1)
#weightedagentTest_matrix.plotMatrix()
#test_matrix.createMatrix()
#matrix = Matrix(participantId = 1754, cursor = cr)



#sessions = test_matrix.getSessions()
#print(sessions)
#test_matrix.createMatrix()
print(test_matrix.matrix_total)
#test_matrix.plotMatrix()
#print()
