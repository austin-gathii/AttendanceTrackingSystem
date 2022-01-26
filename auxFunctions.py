import sqlite3,json

#CONSTANTS
DATABASE = "userData.db"
MAIN_TABLE = "Employees"
EMPLOYEE_ROLES = ["Intern","Junior Developer","Senior Developer","Manager","Department Head","CEO"]
EMPLOYEE_DATA_FIELDS = ["Id", "firstName", "lastName", "Role", "Email", "Phone","Password","Deleted","facialData"]
VISIBLE_EMPLOYEE_DATA_FIELDS = EMPLOYEE_DATA_FIELDS[:-3]


#AUXILLIARY FUNCTIONS
def convertValToSQL(val,stringUp = True,search = False):
    if search:
        decorator = "%"
    else:
        decorator = ""
    if isinstance(val, str) and stringUp:
        return f''' "{decorator}{val}{decorator}" '''
    return f''' {val} '''

def convertListToSQL(lst,stringUp = False):
    sqlStr = ''''''
    for i in lst:
        sqlStr += convertValToSQL(i,stringUp)
        if i != lst[-1]:
            sqlStr+=''','''
    return sqlStr



#DATABASE INTERFACING CODE
def createAConnection():
    conn = sqlite3.connect(DATABASE)
    return conn

def createAnEmployeesTable(name):
    conn = createAConnection()
    conn.execute(f'''CREATE TABLE {name}
             (Id INTEGER PRIMARY KEY  AUTOINCREMENT,
             firstName           VARCHAR(20)    NOT NULL,
            lastName           VARCHAR(20)    NOT NULL,
             Email           VARCHAR(50)    NOT NULL,
             Phone            VARCHAR(10)     NOT NULL,
             Role         VARCHAR(20)   NOT NULL,
             Password       VARCHAR(50)    NOT NULL,
             Deleted      BIT      NOT NULL,
             facialData  BLOB);''')
    conn.close()

def createAnAttendanceTable(name):
    conn = createAConnection()
    conn.execute(f'''CREATE TABLE {name}
             (
             attId INTEGER PRIMARY KEY  AUTOINCREMENT,
             userId           INTEGER    NOT NULL,
            timestamp           TIMESTAMP    NOT NULL
             );''')
    conn.close()

def deleteATable(tableName):
    conn = createAConnection()
    conn.execute(f'''DROP TABLE {tableName};''')
    conn.close()


def insertData(table,vals):
    valFields = list(filter(lambda x:x in EMPLOYEE_DATA_FIELDS[1:],vals.keys())) if table == "Employees" else list(vals.keys())
    conn = createAConnection()
    conn.execute(f'''INSERT INTO {table} ({convertListToSQL(valFields)}) 
                        VALUES ({convertListToSQL([vals[x] for x in valFields],True)});''')
    conn.commit()
    conn.close()


def updateData(table,id,vals):
    conn = createAConnection()
    for key,val in vals.items():
        conn.execute(f'''UPDATE {table} set {key} = {convertValToSQL(val)} WHERE Id = {id}''')
    conn.commit()
    conn.close()

def getAttendanceData(date = None):
    conn = createAConnection()
    if date == None:
        cursor = conn.execute(f'''SELECT attId,userId,timestamp FROM Attendance''')
    else:
        cursor = conn.execute(f'''SELECT attId,userId,timestamp FROM Attendance WHERE timestamp LIKE '%{date}%' ''')

    attendances = []
    for row in cursor:
        thisAttendance = {"attId":row[0],"userId":row[1],"timestamp":row[2]}
        attendances.append(thisAttendance)
    conn.close()
    return attendances

def getTableData(table,searchField = None,filter = None):
    allEmployeeData = {}
    conn = createAConnection()
    if searchField == None and filter == None:
        cursor = conn.execute(f'''SELECT {",".join(EMPLOYEE_DATA_FIELDS)} FROM {table}''')
    else:
        cursor = conn.execute(f'''SELECT {",".join(EMPLOYEE_DATA_FIELDS)} FROM {table} WHERE {searchField} LIKE {convertValToSQL(filter,search = True)}''')

    for row in cursor:
        thisEmployee = {}
        for field,column in zip(EMPLOYEE_DATA_FIELDS,row):
            thisEmployee[field] = column
        allEmployeeData[row[0]] = thisEmployee
    conn.close()
    return allEmployeeData

if __name__ == '__main__':
    createAnAttendanceTable("Attendance")