import random,auxFunctions,time
from datetime import datetime


#TEST EMPLOYEE DATA
EMPLOYEE_ROLES = ["Intern","Junior Developer","Senior Developer","Manager","Department Head"]
EMPLOYEE_DATA_FIELDS = ["firstName", "lastName", "Role", "Email", "Phone","Password","Deleted"]




# region GENERATING INDIVIDUAL DATAPOINTS FOR EMPLOYEES
def generateNames(n):
    with open("TestDataGeneration//firstnames.txt","r") as flist:
        fnames = [x.strip().capitalize() for x in flist.readlines()]
    with open("TestDataGeneration//lastnames.txt","r") as llist:
        lnames = [x.strip().capitalize() for x in llist.readlines()]

    for name in range(n):
        yield f"{random.choice(fnames)} {random.choice(lnames)}"

def generatePhoneNumber(n):
    for num in range(n):
        yield f"+254 {''.join([str(random.randrange(0,9)) for x in range(9)])}"

def generateEmailAddress(name):
    fname,lname = name.split(" ")
    return f"{fname.lower()}{lname.lower()}@gmail.com"

def generateRole(n):
    heirarchy = {0.95:"Department Head",0.85:"Manager",0.7:"Senior Developer",0.45:"Junior Developer",0.1:"Intern"}
    for role in range(n):
        ridx = random.random()
        for key,val in heirarchy.items():
            if ridx > key:
                yield val

def generatePassword(n):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    symbols = "@&!.?"
    for pw in range(n):
        yield f"{''.join([(random.choice(alphabet).upper() if random.random() < 0.5 else random.choice(alphabet)) for _ in range(random.randrange(7,12))])}" \
              f"{random.choice(symbols)}{''.join([random.choice(numbers) for _ in range(random.randrange(2,4))])}"
# endregion



#Creating attendance data






#placing test data in the database
def createTestEmployeeDataset(n):
    for name,phone,role,pwd in zip(generateNames(n),generatePhoneNumber(n),generateRole(n),generatePassword(n)):
        newEmployee = {}
        fname,lname = name.split(" ")
        email = generateEmailAddress(name)
        newEmployee["firstName"] = fname
        newEmployee["lastName"] = lname
        newEmployee["Email"] = email
        newEmployee["Phone"] = phone
        newEmployee["Role"] = role
        newEmployee["Password"] = pwd
        newEmployee["Attendance"] = 100
        newEmployee["Deleted"] = False
        try:
            auxFunctions.insertData("Employees", newEmployee)
        except:
            print("SQL ERROR....")


def createTestAttendanceData(n):
    userCount = len(auxFunctions.getTableData("Employees"))
    userRates = [min(100,random.normalvariate(90,5)) for _ in range(userCount+1)]
    for dayspast in range(n,-1,-1):
        baseMTime = (time.time() - time.time()%(3600*24)) - (dayspast*(3600*24)) + (6*3600)
        baseETime = (time.time() - time.time()%(3600*24)) - (dayspast*(3600*24)) + (14*3600)
        for uIdx in range(3,userCount+1):
            if random.random() < userRates[uIdx]/100:
                morningTimestamp = random.normalvariate(baseMTime,1800)
                eveningTimestamp = random.normalvariate(baseETime,3600)
                for ts in [morningTimestamp,eveningTimestamp]:
                    auxFunctions.insertData("Attendance",{"userId":uIdx,"timestamp":datetime.strftime(datetime.fromtimestamp(ts),"%Y-%m-%d %H:%M:%S")})








if __name__ == '__main__':
    #createTestEmployeeDataset(100)
    createTestAttendanceData(100)
    print("done")