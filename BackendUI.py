import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
import random

import auxFunctions
from auxFunctions import *

#CONSTANTS
ALL_EMPLOYEE_DATA = {245:
                  {"firstName":"austin",
                   "lastName":"gathii",
                   "Email":"ag@gmail.com",
                   "Phone":"0723-434834",
                   "Role":"intern",
                   "Password":"password123",
                   "Attendance":100,
                   "Deleted":int(False),
                   "facialData":0}}



#ADDING DUMMY DATA

for i in range(100):
    ALL_EMPLOYEE_DATA[max(ALL_EMPLOYEE_DATA.keys())+1] = {
        "firstName":f"firstName{i}",
        "lastName":f"lastName{i}",
        "Email":f"firstName{i}@gmail.com",
        "Phone":"".join([str(random.randrange(0,9)) for x in range(10)]),
        "Role":random.choice(EMPLOYEE_ROLES),
        "Password":"password123",
        "Deleted":False,
        "facialData":0
    }






#GUI CREATION CODE
class mainWindow(tk.Tk):
    def __init__(self):
        #WINDOW SETTINGS
        super().__init__()
        self.title("EMPLOYEE RECORDS")
        winLeft = str((self.winfo_screenwidth() - 700) // 2)
        winTop = str((self.winfo_screenheight() - 700) // 2 - 20)
        self.geometry("700x700+" + winLeft + "+" + winTop)
        self.resizable(False, False)

        #MAIN FRAME
        self.mainFrame = tk.Frame(self,background = "red")
        self.mainFrame.columnconfigure(0,weight = 1)
        self.mainFrame.rowconfigure(1,weight = 1)
        self.mainFrame.pack(expand = True,fill = "both")



class RecordsTree(ttk.Treeview):
    def __init__(self,root):
        super().__init__(root.mainFrame,columns = VISIBLE_EMPLOYEE_DATA_FIELDS,show = "headings")
        self.grid(column = 0,row = 1,sticky = tk.NS)

        #SEARCH BAR
        self.searchBarFrame = ttk.Frame(root.mainFrame)

        self.searchValue = tk.StringVar()
        self.searchColumn = tk.StringVar()
        self.searchColumn.set("Id")

        self.searchButton = ttk.Button(self.searchBarFrame,text = "SEARCH")
        self.searchSpecifications = tk.OptionMenu(self.searchBarFrame,self.searchColumn,*EMPLOYEE_DATA_FIELDS[:-1])
        self.searchEntry = ttk.Entry(self.searchBarFrame,width = 200,textvariable = self.searchValue)

        self.searchData = [self.searchColumn.get(),self.searchValue.get()]

        for child in self.searchBarFrame.winfo_children():
            child.pack(side = "right",fill = "y",ipadx = 20,ipady = 5)

        self.searchButton.bind("<Button>",self.onClickSearch)
        self.searchBarFrame.grid(column = 0,row = 0,sticky = tk.EW,columnspan = 2)



        #defining headings
        self.heading("Id",text = "Employee Id")
        self.heading("firstName",text = "First Name")
        self.heading("lastName",text = "Last Name")
        self.heading("Role",text = "Title")
        self.heading("Email",text = "Email Address")
        self.heading("Phone",text = "Phone Number")
        #self.heading("Attendance",text = "Attendance Details")

        #Customizing columns
        for head in VISIBLE_EMPLOYEE_DATA_FIELDS:
            self.column(head,width = 120,anchor = tk.CENTER)

        #add item button
        self.addEmployeeButton = ttk.Button(root.mainFrame,text = "ADD NEW EMPLOYEE",padding = 10)
        self.addEmployeeButton.grid(row = 3,column = 0,sticky = tk.NSEW)
        self.addEmployeeButton.bind("<Button>",self.onClickAddNewEmployee)



        # add scrollbars
        scrollbar = ttk.Scrollbar(root.mainFrame, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')

        scrollbar = ttk.Scrollbar(root.mainFrame, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(xscroll=scrollbar.set)
        scrollbar.grid(row=2, column=0, sticky='ew')


        #view individual employee records
        self.bind("<<TreeviewSelect>>",self.onClickIndividualEmployee)

        #update employee records
        self.updateEmployeeRecords()

    def onClickIndividualEmployee(self,event):
        ViewEmployeeDetails(self.item(self.selection()[0])["values"][0],self)


    def onClickAddNewEmployee(self,event):
        AddNewEmployee()

    def onClickSearch(self,event):
        self.searchData = [self.searchColumn.get(),self.searchValue.get()]
        self.clearAllItems()

    def clearAllItems(self):
        for item in self.get_children(""):
            self.delete(item)

    def filterEmployeeData(self):
        return getTableData(MAIN_TABLE,searchField = self.searchData[0],filter = self.searchData[1])
        '''if self.searchData[1] == "":
            return employeeData
        if self.searchData[0] == "Id":
            if int(self.searchData[1]) in employeeData.keys():
                return {int(self.searchData[1]):employeeData[int(self.searchData[1])]}
            return {}
        newEmployeeData = {}
        for key,val in employeeData.items():
            if self.searchData[1] in val[self.searchData[0]]:
                newEmployeeData[key] = val'''
            
        

    def updateEmployeeRecords(self):
        employeeData = self.filterEmployeeData()
        currentItems = [self.item(x) for x in self.get_children("")]
        outliers = set([tuple(list(map(str,x.values()))[:-2]) for x in employeeData.values()]).symmetric_difference(set([tuple(map(str,x["values"])) for x in currentItems]))
        for iid in set([int(x[0]) for x in outliers]):
            if iid in [x["values"][0] for x in currentItems]:
                self.delete(self.get_children("")[[x["values"][0] for x in currentItems].index(iid)])

            if iid in employeeData.keys():
                if not employeeData[iid]["Deleted"]:
                    self.insert("", tk.END, text = list(employeeData[iid].values())[:-2],values=list(employeeData[iid].values())[:-2])




        '''for iid,employee in self.filterEmployeeData().items():
            if iid not in [self.item(x)["values"][0] for x in self.get_children("")] and not ALL_EMPLOYEE_DATA[iid]["Deleted"]:
                them = ALL_EMPLOYEE_DATA[iid]
                content = (
                iid, them["firstName"], them["lastName"], them["Role"], them["Email"], them["Phone"], str(them["Attendance"]))
                self.insert("", tk.END, values=content)'''
        self.after(1000,self.updateEmployeeRecords)



class AddNewEmployee(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("ADD NEW EMPLOYEE")
        self.geometry(f"{400}x{600}+{(self.winfo_screenwidth() - 400) // 2}+{0}")
        self.resizable(False,False)
        
        #MAIN FRAME
        self.mainFrame = ttk.Frame(self)
        self.mainFrame.pack(expand = True,fill = "both")

        # User entries
        self.firstName = tk.StringVar()
        ttk.Label(self.mainFrame, text="First Name :")
        tk.Entry(self.mainFrame, textvariable=self.firstName)

        self.lastName = tk.StringVar()
        ttk.Label(self.mainFrame, text="Last Name :")
        tk.Entry(self.mainFrame, textvariable=self.lastName)

        self.Phone = tk.StringVar()
        ttk.Label(self.mainFrame, text="Phone Number :")
        tk.Entry(self.mainFrame, textvariable=self.Phone)

        self.Email = tk.StringVar()
        ttk.Label(self.mainFrame, text="Email Address :")
        tk.Entry(self.mainFrame, textvariable=self.Email)

        self.Role = tk.StringVar()
        ttk.Label(self.mainFrame,text = "Employee Title/Role :")
        ttk.Combobox(self.mainFrame,textvariable = self.Role,values = EMPLOYEE_ROLES)

        self.Password = tk.StringVar()
        ttk.Label(self.mainFrame, text="Employee Password :")
        tk.Entry(self.mainFrame, textvariable=self.Password, show="*")

        self.confirmPassword = tk.StringVar()
        ttk.Label(self.mainFrame, text="Confirm Employee Password :")
        tk.Entry(self.mainFrame, textvariable=self.confirmPassword, show="*")

        for child in self.mainFrame.winfo_children():
            child.pack(fill = "x",pady = 10,padx = 20)

        self.createEmployeeButton = ttk.Button(self.mainFrame, text="ADD NEW EMPLOYEE")
        self.createEmployeeButton.bind("<Button>", self.onClickCreateEmployee)
        self.createEmployeeButton.pack(fill="x", ipady=10, pady=5)


    def onClickCreateEmployee(self,event):
        #check if all fields filled
        if all(x.get() != "" for x in [self.firstName,self.lastName,self.Email,self.Phone,self.Password,self.confirmPassword,self.Role]):
            #check if Password strong -- to be done later

            #check if Passwords match
            if self.Password.get() == self.confirmPassword.get():
                #add new user
                newEmployee = {}
                newEmployee["firstName"] = self.firstName.get()
                newEmployee["lastName"] = self.lastName.get()
                newEmployee["Email"] = self.Email.get()
                newEmployee["Phone"] = self.Phone.get()
                newEmployee["Role"] = self.Role.get()
                newEmployee["Password"] = self.Password.get()
                newEmployee["Attendance"] = 100
                newEmployee["Deleted"] = False
                #newEmployee["facialData"] = 0

                try:
                    insertData(MAIN_TABLE,newEmployee)
                except:
                    print("SQL ERROR....")

                mb.showinfo("Successfullly added Employee",f"The new employee has been succesfully added to the system...")
                self.destroy()
            else:
                mb.showerror("Passwords do not match","Your Password and its confirmation do not match")
        else:
            mb.showerror("Missing Fields","Please fill in all fields in the form")


class ViewEmployeeDetails(tk.Toplevel):
    def __init__(self,Id,Tree):
        super().__init__()
        self.ogEmployeeData = getTableData(MAIN_TABLE,"Id",Id)[Id]
        self.title(f"Employee {Id} : {self.ogEmployeeData['firstName']} {self.ogEmployeeData['lastName']}")
        self.geometry(f"{400}x{600}+{(self.winfo_screenwidth() - 400) // 2}+{0}")
        self.resizable(False, False)
        self.Id = Id
        self.Tree = Tree

        # MAIN FRAME
        self.mainFrame = tk.Frame(self,background = "red")
        self.mainFrame.rowconfigure(0,weight = 1)
        self.mainFrame.columnconfigure(0,weight = 1)

        self.mainFrame.pack(expand=True, fill="both")


        #FUNCTION BUTTONS
        self.buttonsFrame = ttk.Frame(self.mainFrame)
        self.buttonsFrame.grid(row = 1,column = 0,sticky = tk.NSEW,ipady = 10)

        self.deleteEmployeeButton = ttk.Button(self.buttonsFrame,text = "DELETE THIS EMPLOYEE")
        self.editEmployeeDetailsButton = ttk.Button(self.buttonsFrame,text = "EDIT EMPLOYEE DETAILS")

        self.editEmployeeDetailsButton.bind("<Button>",self.onClickEditEmployeeDetails)
        self.deleteEmployeeButton.bind("<Button>",self.onClickDeleteEmployee)

        self.editEmployeeDetailsButton.pack(side = "right",expand = True,fill = "both")
        self.deleteEmployeeButton.pack(side = "left",expand = True,fill = "both")

        #terminated employee label
        self.terminatedEmployeeLabel = tk.Label(self.mainFrame,text = "This Employee has been Terminated...".upper(),foreground = "red")




        #EMPLOYEE DETAILS
        self.detailsFrame = ttk.Frame(self.mainFrame)
        self.detailsFrame.grid(row = 0,column = 0,sticky = tk.NSEW)

        self.employeeData = {}
        for field in EMPLOYEE_DATA_FIELDS[1:]:
            self.employeeData[field] = tk.StringVar()
            self.employeeData[field].set(self.ogEmployeeData[field])

        ttk.Label(self.detailsFrame, text="First Name :")
        tk.Entry(self.detailsFrame, textvariable=self.employeeData["firstName"])

        ttk.Label(self.detailsFrame, text="Last Name :")
        tk.Entry(self.detailsFrame, textvariable=self.employeeData["lastName"])

        ttk.Label(self.detailsFrame, text="Phone Number :")
        tk.Entry(self.detailsFrame, textvariable=self.employeeData["Phone"])

        ttk.Label(self.detailsFrame, text="Email Address :")
        tk.Entry(self.detailsFrame, textvariable=self.employeeData["Email"])

        ttk.Label(self.detailsFrame, text="Employee Title/Role :")
        ttk.Combobox(self.detailsFrame, textvariable = self.employeeData["Role"],values =  EMPLOYEE_ROLES)

        for child in self.detailsFrame.winfo_children():
            child.pack(fill = "x",padx = 20,pady = 5,ipady = 5)
            if child.winfo_class() == "Entry" or child.winfo_class() == "TCombobox":
                child.configure(state = "disable")

        print("wait")
        #ATTENDANCE DETAILS


    def onClickEditEmployeeDetails(self,event):
        if event.widget["text"] == "EDIT EMPLOYEE DETAILS":
            for child in self.detailsFrame.winfo_children():
                if child.winfo_class() == "Entry" or child.winfo_class() == "TCombobox":
                    child.configure(state = "normal")
            event.widget["text"] = "SAVE EMPLOYEE DETAILS"

        else:
            if mb.askyesno("Confirmation","Are you sure that all the altered information is correct..."):
                thisEmployeeData = {}
                for field in self.employeeData.keys():
                    thisEmployeeData[field] = self.employeeData[field].get()
                try:
                    updateData(MAIN_TABLE,self.Id,thisEmployeeData)
                except:
                    print("SQL ERROR.....")
                self.ogEmployeeData = getTableData(MAIN_TABLE, "Id", self.Id)[self.Id]

                #self.Tree.clearAllItems()#look into this

            else:
                for field in EMPLOYEE_DATA_FIELDS[1:]:
                    self.employeeData[field].set(self.ogEmployeeData[field])

            for child in self.detailsFrame.winfo_children():
                if child.winfo_class() == "Entry" or child.winfo_class() == "TCombobox":
                    child.configure(state="disable")
            event.widget["text"] = "EDIT EMPLOYEE DETAILS"

    def onClickDeleteEmployee(self,event):
        if mb.askyesno("Confirmation","Are you sure you would like to Terminate this Employee?"):
            updateData(MAIN_TABLE,self.Id,{"Deleted":1})
            self.ogEmployeeData = getTableData(MAIN_TABLE, "Id", self.Id)[self.Id]
            #self.Tree.clearAllItems()#look into this
            event.widget["state"] = "disable"
            self.editEmployeeDetailsButton["state"] = "disable"
            self.terminatedEmployeeLabel.grid(row = 2,column = 0,sticky = tk.EW,ipady = 5)


if __name__ == '__main__':
    #SQL TESTING
    #getTableData(MAIN_TABLE)
    root = mainWindow()
    tree = RecordsTree(root)
    root.mainloop()

