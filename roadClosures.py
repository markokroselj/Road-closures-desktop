import os
import sys 
import time
import pytz
import requests
import tkinter as tk
from datetime import datetime
from bs4 import BeautifulSoup

request = requests.get("https://www.cameroncounty.us/spacex/")
soup = BeautifulSoup(request.text, 'html.parser')


class Closure:
    def __init__(self, date, timeCDT, timeCET,  status):
        self.date = date
        self.timeCDT = timeCDT
        self.timeCET = timeCET
        self.status = status

def get_current_date():
    return datetime.today().strftime('%B %d, %Y')


def get_utc_dt(x):
    if 'a.m.' in x:
        x = x.replace('a.m.', 'am')
    else:   
        x = x.replace('p.m.', 'pm') 

    local = pytz.timezone("America/Mexico_City")
    naive = datetime.strptime(x, '%A, %B %d, %Y %I:%M %p')
    local_dt = local.localize(naive, is_dst=None)
    return local_dt.astimezone(pytz.utc)  


def get_closures():
    closures = []
    i = 0
    while i < len(soup.table.tbody.find_all('tr')):
        #get closure date
        closure_date = soup.table.tbody.find_all('tr')[i].find_all('td')[1].get_text(strip=True)
        current_date1 = time.strptime(get_current_date(), '%B %d, %Y')
        closure_date1 = time.strptime(closure_date, '%A, %B %d, %Y')

        #get closure time
        clsoure_time = soup.table.tbody.find_all('tr')[i].find_all('td')[2].get_text(strip=True)

        #remove dots from closure time
        if 'a.m.' in clsoure_time:
            clsoure_time = clsoure_time.replace('a.m.', 'am')
        else:   
            clsoure_time = clsoure_time.replace('p.m.', 'pm') 

        #get closure start time in cet
        utc_dt = get_utc_dt(closure_date + ' ' + clsoure_time.split('to')[0].strip())
        timezone = 'Europe/Ljubljana'
        localDatetime = utc_dt.astimezone(pytz.timezone(timezone))
        localFormat = "%H:%M"
        localDatetimeStart = localDatetime.strftime(localFormat)

        #get closure end time in cet
        utc_dt = get_utc_dt(closure_date + ' ' + clsoure_time.split('to')[1].strip())
        timezone = 'Europe/Ljubljana'
        localDatetime = utc_dt.astimezone(pytz.timezone(timezone))
        localFormat = "%H:%M"
        localDatetimeEnd = localDatetime.strftime(localFormat)

        #combine two cet times
        closure_timeCET = str(localDatetimeStart) + ' to ' + str(localDatetimeEnd) + ' CET'

        #add "cdt" to closure time
        clsoure_time = clsoure_time + ' CDT'

        #get road status
        status = soup.table.tbody.find_all('tr')[i].find_all('td')[3].text
        i += 1
        #check if date is biger or equal as current date and check if closure is scheduled
        if((closure_date1 < current_date1) or ("closure scheduled" not in status.lower())):
            continue
        
        #add closure object to array
        closures.append(Closure(closure_date, clsoure_time, closure_timeCET, status))
       
    return closures




class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text = '')
        self.label.pack(side="top")
        self.label = tk.Label(self, text = 'Starbase road closures', font='Helvetica 18')
        self.label.pack(side="top")

                 
        for x in get_closures():
            print(x.date + ' ' + x.timeCDT + ' ' + x.timeCET + ' ' + x.status)
            self.label = tk.Label(self, text = x.date + '   ' + x.timeCDT + '   ' + x.timeCET + '   ')
            self.label.pack(side="top")

       

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.geometry("520x350")
root.iconbitmap(resource_path('icon.ico'))
root.title('Road closures')
copyrightLabel = tk.Label(root,text = '©Marko Krošelj', font='Tahoma 7 italic')
copyrightLabel.place(relx = 0.0, rely = 1.0, anchor ='sw')
app = Application(master=root)
app.mainloop()