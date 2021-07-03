from tkinter import *
from tkhtmlview import HTMLLabel
from GetINFO import Fetch
import json

class MyApp(Tk):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def getData(self):
        with open("data.json", "r") as f:
            return json.load(f)

    def setupUI(self):
        self.data = self.getData()
        myFont = "Monospace 13"
        self.title("NBA_Viewer")
        self.teamList = Listbox(self, width=25, height=40, font=myFont)
        self.playerList = Listbox(self, width=25, height=20, font=myFont)
        self.teamIMG = HTMLLabel(self, width=25, height=15, font=myFont)
        self.teamDatas = [Label(self, width=25, font=myFont) for i in range(4)]
        self.updateLB = Label(self, text="Update Time: {}".format(self.data["updateTime"]),
                              font=myFont)
        # Teams label
        Label(self, text="Teams", font=myFont).grid(row=0, column=0)
        # Reload button
        Button(self, text="Reload", font=myFont, command=self.reloadData).grid(row=6, column=3, sticky="e")
        # Close button
        Button(self, text="Close", font=myFont, command=self.quit).grid(row=0, column=3, sticky="e")
        # Show player button
        Button(self, text="Show Info",font=myFont,command=self.popOutPlayer).grid(row=6,column=1, columnspan=2)
        self.teamList.grid(row=1, column=0, rowspan=5)
        self.teamIMG.grid(row=1, column=1, rowspan=4)
        for i in range(4):
            self.teamDatas[i].grid(row=i+1, column=2)
        self.playerList.grid(row=5, column=1, columnspan=2)
        self.updateLB.grid(row=6)
        # Set all teams
        self.setTeam()

    def reloadData(self):
        # Clear all
        for item in self.grid_slaves():
            item.destroy()
        updating = Label(self, text="Updating...", font="Monospace 20")
        updating.pack()
        self.update()
        # Reload data
        Fetch().start()
        updating.destroy()
        # Redraw
        self.setupUI()

    def setTeam(self):
        self.teamList.insert(END, *self.data["teams"].keys())
        self.teamList.bind("<<ListboxSelect>>", self.teamSelected)

    def teamSelected(self, event):
        selection = self.teamList.curselection()
        self.team = self.teamList.get(selection)
        self.showTeam()
        self.setPlayer()

    def showTeam(self):
        IMG = self.data["teams"][self.team]["teamData"]["IMG"]
        self.teamIMG.set_html('<img src="{}" width="250" height="200">'.format(IMG))
        dataSet= ["PPG", "RPG", "APG", "OPPG"]
        for i in range(4):
            self.teamDatas[i].config(text=
                                     dataSet[i]
                                     + ": "
                                     + self.data["teams"][self.team]["teamData"][dataSet[i]])

    def setPlayer(self):
        players = self.data["teams"][self.team]["playerData"].keys()
        self.playerList.delete(0, END)
        self.playerList.insert(END, *players)

    def popOutPlayer(self):
        pSelection = self.playerList.curselection()
        tSelection = self.teamList.curselection()
        player=self.playerList.get(pSelection[0])
        win =Toplevel(width=400,height=500)
        win.wm_title(player+"'s Info")
        name = Label(win, text=player,font='(,50,)')
        team=Label(win,text=self.team,font='(,30,)')
        infoframe=Frame(win)
        frame1=Frame(infoframe)
        frame2=Frame(infoframe)
        for info in self.data["teams"][self.team]["playerData"][player]["Info"]:
            data=info+":    "+self.data["teams"][self.team]["playerData"][player]["Info"][info]
            keylabel=Label(infoframe,text=data,font='(,30,)')
            #valuelabel=Label(win)
            keylabel.pack()
            #valuelabel.pack()
        frame1.pack()
        imageframe=Frame(win)
        stateframe=Frame(win)
        for state in self.data["teams"][self.team]["playerData"][player]["State"]:
            data=state+":    "+self.data["teams"][self.team]["playerData"][player]["State"][state]
            keylabel=Label(stateframe,text=data,font='(,50,)')
            #valuelabel=Label(win)
            keylabel.pack(side=LEFT)
            #valuelabel.pack()
        self.postPlayerImage(self.team,player,imageframe)
        b = Button(win, text="Okay", command=win.destroy)
        name.pack()
        team.pack()
        imageframe.pack(anchor=E)
        stateframe.pack()
        infoframe.pack()
        b.pack(side='bottom')

    def postPlayerImage(self,team,player,frame):
        url=self.data["teams"][team]["playerData"][player]["playerIMG"]
        html="<img src="+url+" width=\"600\" height=\"440\"> </img>"
        lbl = HTMLLabel(frame, html=html)
        lbl.pack(anchor=E)

if __name__ == "__main__":
    myApp = MyApp()
    myApp.mainloop()
