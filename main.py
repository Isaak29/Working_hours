from fastapi import FastAPI
import pyrebase, uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import calendar
import time

config = {
    "apiKey": "AIzaSyCMp8OJqHy8CkWr6AfYZ0DMMi40wKI98VM",
    "authDomain": "marketing-data-d141d.firebaseapp.com",
    "databaseURL": "https://marketing-data-d141d-default-rtdb.firebaseio.com",
    "projectId": "marketing-data-d141d",
    "storageBucket": "marketing-data-d141d.appspot.com",
    "messagingSenderId": "566962550940",
    "appId": "1:566962550940:web:eee189eca2bb49309e5559",
    "measurementId": "G-Z54PR6Y2ZP"
    }

firebase = pyrebase.initialize_app(config)
db = firebase.database()
app = FastAPI(docs_url='/')
templates = Jinja2Templates(directory="templates")

def find_todays_present():
    attendance = db.child("attendance").get().val()
    todaysDate = datetime.today()
    thisDa = todaysDate.strftime("%d")
    currentyear = todaysDate.strftime("%Y")
    currentmonth = todaysDate.strftime("%m")
    todays_present_list = []
    attend = attendance[currentyear][currentmonth][thisDa]
    for uid in attend:
        uid = uid
        if attendance[currentyear][currentmonth][thisDa][uid]:
            todays_present_list.append(uid)

    return todays_present_list        

@app.get('/Absent_Staff_Name')
async def Absentees():
    todays_present_list = find_todays_present()
    staff_data = db.child("staff").get().val()
    absent_uid_list=[] 
    nameList = []    
    for uid in staff_data:
        if uid not in todays_present_list:
            absent_uid_list.append(uid)
            nameList.append(staff_data[uid]['name'])
    return (f"Today's Absentees = {len(absent_uid_list)}",nameList)

@app.get('/Present_Staff_Name')
async def Present():
    todays_present_list = find_todays_present()
    staff_data = db.child("staff").get().val()  
    nameList = []    
    for uid in todays_present_list:
        nameList.append(staff_data[uid]['name'])
    return (f"Today's Present Staff = {len(todays_present_list)}",nameList)

def dailyworkhours(date1):
    date_parts = date1.split("-")
    tyear = date_parts[0]
    tmonth = date_parts[1]
    tday = date_parts[2]
    staffDB = db.child("staff").get().val()
    attendance = db.child("attendance").get().val()
    for uid in staffDB:
        checkin = attendance[tyear][tmonth][tday].get(uid,{}).get("check_in",None)
        checkout= attendance[tyear][tmonth][tday].get(uid,{}).get("check_out",None)
        try:
            if checkin is not None and checkout is not None:
                date_format = "%Y-%m-%d %H:%M:%S"
                common_date = datetime.now().date()
                datetime1 = datetime.strptime(str(common_date) + " " + checkin, date_format)
                datetime2 = datetime.strptime(str(common_date) + " " + checkout, date_format)
                datetimeall1 = datetime.strptime(str(datetime1), date_format)
                datetimeall2 = datetime.strptime(str(datetime2), date_format)
                time_string1 = datetimeall1.strftime("%I:%M:%S %p")
                time_string2 = datetimeall2.strftime("%I:%M:%S %p")
                time_format = "%I:%M:%S %p"
                time1 = datetime.strptime(time_string1, time_format)
                time2 = datetime.strptime(time_string2, time_format)
                working_hours = time2 - time1
                hours, remainder = divmod(working_hours.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                formatted_working_hours = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
                db.child("attendance").child(tyear).child(tmonth).child(tday).child(uid).update({"working_hours": formatted_working_hours})     
            elif checkin is not None:      
                db.child("attendance").child(tyear).child(tmonth).child(tday).child(uid).update({"working_hours": "08:30:00"})     
        except:
            pass
    



@app.get("/Working_hours", response_class=HTMLResponse)
async def Working_hours(request: Request):
    attendance = db.child("attendance").get().val()
    staffDB = db.child("staff").get().val()
    todaysDate = datetime.today()
    thisDa = todaysDate.strftime("%d")
    currentyear = todaysDate.strftime("%Y")
    currentmonth = todaysDate.strftime("%m")
    staffuid=[]
    staffnamelist=[]
    attendenceloginlist=[]
    attendencelogoutlist=[]
    workinghourlist=[]
    staffdate=[]
    attype=[]
    outtype=[]
    absentstaff =[]
    absentworkinghours=[]
    workinghourlistall=[]
    
    todaysDate = datetime.today()
    yesterdayDate = todaysDate - timedelta(days=1)
    formattedYesterdayDate = yesterdayDate.strftime("%Y-%m-%d")
    dates = [formattedYesterdayDate]
    # dates=["2023-10-06"]
    for date1 in dates:
        dailyworkhours(date1)
        date_parts = date1.split("-")
        tyear = date_parts[0]
        tmonth = date_parts[1]
        tday = date_parts[2] 
    

    yesterdaydate = dates[0].strip("'")    

    attend = attendance[tyear][tmonth][tday]
    
    for staff in staffDB:
        if staffDB[staff]['department'] != "ADMIN":
            try:
                checkin = attend[staff].get("check_in", None)
                checkout = attend[staff].get("check_out", None)
                workinghour = attend[staff]["working_hours"]

                try:
                    if checkin is not None and checkout is not None and workinghour is not None:     
                        date_format = "%Y-%m-%d %H:%M:%S"
                        common_date = datetime.now().date()
                        datetime1 = datetime.strptime(str(common_date) + " " + checkin, date_format)
                        datetime2 = datetime.strptime(str(common_date) + " " + checkout, date_format)
                        datetimeall1 = datetime.strptime(str(datetime1), date_format)
                        datetimeall2 = datetime.strptime(str(datetime2), date_format)
                        time_string1 = datetimeall1.strftime("%I:%M:%S %p")
                        time_string2 = datetimeall2.strftime("%I:%M:%S %p")

                        staffnamelist.append(staffDB[staff]["name"])
                        attendenceloginlist.append(time_string1)
                        attendencelogoutlist.append(time_string2)
                        workinghourlist.append(workinghour)
                        staffuid.append(staff)
                        staffdate.append(yesterdaydate)
   
                        try:
                            checkintype = attend[staff]["proxy_in"]
                            attype.append("proxy")
                        except:
                            attype.append("Id Card")   
                        try:     
                            checkouttype = attend[staff]["proxy_out"]
                            outtype.append("proxy")
                        except:
                            outtype.append("Id Card")

                    elif checkin is not None and workinghour is not None:
                        date_format = "%Y-%m-%d %H:%M:%S"
                        common_date = datetime.now().date()
                        datetime1 = datetime.strptime(str(common_date) + " " + checkin, date_format)
                        datetimeall1 = datetime.strptime(str(datetime1), date_format)
                        time_string1 = datetimeall1.strftime("%I:%M:%S %p")

                        staffnamelist.append(staffDB[staff]["name"])
                        attendenceloginlist.append(time_string1)
                        attendencelogoutlist.append("No entry")
                        workinghourlist.append(workinghour)
                        staffuid.append(staff)
                        staffdate.append(yesterdaydate) 
                        try:
                            checkintype = attend[staff]["proxy_in"]
                            attype.append("proxy")
                        except:
                            attype.append("Id Card")   
                        try:     
                            checkouttype = attend[staff]["proxy_out"]
                            outtype.append("proxy")
                        except:
                            outtype.append("No entry")
                    


                    try:
                        total = attendance[currentyear][currentmonth]
                        totalhours = 0   
                        for date in total:
                            dailyhours = total.get(date,{}).get(staff, {}).get("working_hours",0)       
                            try:   
                                hours, minutes, seconds = map(int, dailyhours.split(':')) 
                                workinghourall = hours * 3600 + minutes * 60 + seconds
                            except:
                                workinghourall = 0    
                            totalhours+=workinghourall 

                        total_hours, remainder = divmod(totalhours, 3600)
                        total_minutes, total_seconds = divmod(remainder, 60)
                        workinghourlistall.append(f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}")
                    except:
                        workinghourlistall.append("No Logs")        
                except:
                    pass        
            
            except:
                absentstaff.append(staffDB[staff]["name"])
                try:
                    total = attendance[currentyear][currentmonth]
                    totalhours = 0   
                    for date in total:
                        dailyhours = total.get(date,{}).get(staff, {}).get("working_hours",0)
                        try:   
                            hours, minutes, seconds = map(int, dailyhours.split(':')) 
                            workinghourall = hours * 3600 + minutes * 60 + seconds
                        except:
                            workinghourall = 0    
                        totalhours+=workinghourall 
                    total_hours, remainder = divmod(totalhours, 3600)
                    total_minutes, total_seconds = divmod(remainder, 60)
                    # staffnamelist.append(data[staffuid]["name"])
                    absentworkinghours.append(f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}")
                except:
                    absentworkinghours.append("No Logs")
    
    total_staff_count = len(staffDB)
    present_staff_count = total_staff_count - len(absentstaff)
    absent_staff_count = len(absentstaff)

    sorted_finallist = sorted(zip(staffnamelist,attendenceloginlist,attendencelogoutlist,workinghourlist,workinghourlistall,attype,outtype), key=lambda x: x[0])
    absentworkinghourlist = sorted(zip(absentstaff, absentworkinghours), key=lambda x: x[0])
    return templates.TemplateResponse("working.html", {
        "request": request,
        "finallist": sorted_finallist,
        "absenteeslist":absentworkinghourlist,
        "date":yesterdaydate,
        "totalcount":total_staff_count,
        "presentcount":present_staff_count,
        "absentcount":absent_staff_count,
        
        })


     

@app.get("/user_monthly_attendence")
async def user_monthly_attendence(request: Request, name: str, month: int):
    attendance = db.child("attendance").get().val()
    staffDB = db.child("staff").get().val()
    formatted_month = f"{month:02}"
    todaysDate = datetime.today()
    thisDa = todaysDate.strftime("%d")
    currentyear = todaysDate.strftime("%Y")
    currentmonth = todaysDate.strftime("%m")
    
    # Find the uid based on the provided name
    uid = None
    for staff_uid, staff_data in staffDB.items():
        if staff_data.get("name") == name:
            uid = staff_uid
            break

    if uid is None:
        return {"error": f"No uid found for name: {name}"}
    
    presentlist = []
    absentlist = []
    totalworkinghours = []
    
    try:
        attend = attendance[currentyear][formatted_month]
    except KeyError:
        return {"error": f"No attendance data found for year: {currentyear}, month: {formatted_month}"}
    
    totalhours = 0 
    for date in attend:
         
        try:
            present = attend[date].get(uid)
            if present:
                presentlist.append(present)
            else:
                # Check if the date is not a Sunday
                year = int(currentyear)
                month = int(formatted_month)
                day = int(date)
                day_of_week = calendar.weekday(year, month, day)
                if day_of_week != calendar.SUNDAY:
                    # Format the date as "dd:mm:yyyy"
                    formatted_date = datetime(year, month, day).strftime("%d:%m:%Y")
                    absentlist.append(formatted_date)
        except:
            year = int(currentyear)
            month = int(formatted_month)
            day = int(date)
            day_of_week = calendar.weekday(year, month, day)
            if day_of_week != calendar.SUNDAY:
                # Format the date as "dd:mm:yyyy"
                formatted_date = datetime(year, month, day).strftime("%d:%m:%Y")
                absentlist.append(formatted_date)

        
        dailyhours = attend.get(date, {}).get(uid, {}).get("working_hours",0)
        try:
            hours, minutes, seconds = map(int, dailyhours.split(':')) 
            workinghourall = hours * 3600 + minutes * 60 + seconds
        except:
            workinghourall = 0 
        totalhours+=workinghourall      
  

    total_hours, remainder = divmod(totalhours, 3600)
    total_minutes, total_seconds = divmod(remainder, 60)
    totalworkinghours.append(f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}")

    presentcount = len(presentlist)
    absentcount = len(absentlist)

    return {
        "name": name,
        "month": formatted_month,
        "present": presentcount,
        "absent": absentlist,
        "total_hours": totalworkinghours,
    }


@app.get("/alluser_monthly_attendence")
async def alluser_monthly_attendence(request: Request, month: int):
    attendance = db.child("attendance").get().val()
    staffDB = db.child("staff").get().val()
    formatted_month = f"{month:02}"
    todaysDate = datetime.today()
    currentyear = todaysDate.strftime("%Y")
    
    result = []

    try:
        attend = attendance[currentyear][formatted_month]
    except KeyError:
        return {"error": f"No attendance data found for year: {currentyear}, month: {formatted_month}"}

    for staff_uid, staff_data in staffDB.items():
        if staffDB[staff_uid]['department'] != "ADMIN":
            user_name = staff_data.get("name", "Unknown")
            present_dates = []
            absent_dates = []
            totalworkinghours = []
            totalhours = 0
            for date, user_attendance in attend.items():
                if staff_uid in user_attendance:
                    present_dates.append(date)
                else:
                    year = int(currentyear)
                    month = int(formatted_month)
                    day = int(date)
                    day_of_week = calendar.weekday(year, month, day)

                    if day_of_week != calendar.SUNDAY:
                        formatted_date = datetime(year, month, day).strftime("%d:%m:%Y")
                        absent_dates.append(formatted_date)

                dailyhours = attend.get(date, {}).get(staff_uid, {}).get("working_hours",0)
                
                try:
                    hours, minutes, seconds = map(int, dailyhours.split(':')) 
                    workinghourall = hours * 3600 + minutes * 60 + seconds
                except:
                    workinghourall = 0 
                totalhours+=workinghourall      
        

            total_hours, remainder = divmod(totalhours, 3600)
            total_minutes, total_seconds = divmod(remainder, 60)
            totalworkinghours.append(f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}")        

            result.append({
                "uid": staff_uid,
                "name": user_name,
                "present_count": len(present_dates),
                "absent_dates": absent_dates,
                "total_hours": totalworkinghours
            })

    return {"result": result} 

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.1.8", port=5001)         