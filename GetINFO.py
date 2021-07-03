from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from datetime import datetime
import os, json

class Fetch:
    def __init__(self):
        self.badGateway = "An error (502 Bad Gateway) has occurred in response to this request."
        if not (os.path.exists("data.json") and os.path.exists("./teamPic/")):
            self.start()

    def start(self):
        if not os.path.exists("./teamPic"):
            os.mkdir("./teamPic")
        self.data = {}
        self.setBrowser()
        self.progress = tqdm(total=30)
        self.getTeams()
        self.writeData()
        self.end()

    def setBrowser(self):
        with open("drivePath.txt", "r") as f:
            self.drivePath = f.read()[:-1]
        options = webdriver.ChromeOptions()
        options.add_argument("-headless")
        self.browser = webdriver.Chrome(executable_path=self.drivePath,
                                        options=options)

    def getTeams(self):
        url = "https://www.nba.com/teams"
        self.browser.get(url)
        self.data["teams"] = {}
        bsObj = BeautifulSoup(self.browser.page_source, "html.parser")
        teamsInfo = bsObj.findAll("div", {"class": "TeamFigure_tf__2RSkP"})
        for teamInfo in teamsInfo:
            teamName = teamInfo.find("a", {"class": "TeamFigure_tfMainLink__mH93D Anchor_external__Mh-vB Anchor_complexLink__2NtkO"}).get_text()
            profile = teamInfo.find("a", {"class": "TeamFigureLink_teamFigureLink__3uOct Anchor_complexLink__2NtkO"})["href"]
            profileLink = urljoin(url, profile)
            self.data["teams"][teamName] = {"teamData":{}, "playerData": {}}
            self.getTeamDatas(teamName, profileLink)
            self.progress.update()

    def getTeamDatas(self, teamName, link):
        self.browser.get(link)
        if self.browser.find_element_by_tag_name("body").text == self.badGateway:
            self.getTeamDatas(teamName, link)
        else:
            teamINFO = self.browser.find_elements_by_class_name("TeamHeader_rankValue__1pj3i")
            dataColumn = ["PPG", "RPG", "APG", "OPPG"]
            for i in range(4):
                self.data["teams"][teamName]["teamData"][dataColumn[i]] = teamINFO[i].text
            imgURL = self.browser.find_element_by_class_name("TeamHeader_teamLogoBW__QkK7w.TeamLogo_logo__1CmT9").get_attribute("src")
            self.getPlayerName(link,teamName)
            self.getTeamIMG(teamName, imgURL)

    def getTeamIMG(self, teamName, imgURL):
        self.browser.get(imgURL)
        imgPath = "./teamPic/{}.png".format(teamName)
        self.browser.save_screenshot(imgPath)
        self.data["teams"][teamName]["teamData"]["IMG"] = imgPath

    def getPlayerName(self,link,teamName):
        html=self.browser.page_source
        bsobj=BeautifulSoup(html,"html.parser")
        playername2=bsobj.findAll('td',{'class':'primary text'})
        playernum=bsobj.findAll('td',{'class':'text TeamRoster_extraPadding__2E9RF'})
        playerpos=bsobj.findAll('td',{'class':'text'})
        playerlink=[]
        q=0
        t=0
        for i in playername2:
            if(playernum[q].get_text()!=""):
                self.data["teams"][teamName]["playerData"][i.get_text()]={"Info":{},"State":{}}
                self.data["teams"][teamName]["playerData"][i.get_text()]["Info"]["PLAYER_POSITION"]=playerpos[2+q*9].get_text()
                self.data["teams"][teamName]["playerData"][i.get_text()]["Info"]["PLAYER_NUMBER"]=playernum[q].get_text()
                links=i.findAll('a')
                playerlink.append("https://www.nba.com"+links[0]["href"])
            q+=1
        for plink in playerlink:
            self.getPlayerInfo(plink,teamName)

    def getPlayerInfo(self,link,thisteam):
        self.browser.get(link)
        if self.browser.find_element_by_tag_name("body").text == self.badGateway:
            self.getPlayerInfo(link,thisteam)
        else:
            html=self.browser.page_source
            bsobj=BeautifulSoup(html,"html.parser")
            playerINFO = bsobj.findAll('p',{"class":"PlayerSummary_playerStatValue__3hvQY"})
            dataColumn = ["PPG", "RPG", "APG", "PIE"]
            nameofplayer=bsobj.findAll('p',{"class":"PlayerSummary_playerNameText__K7ZXO"})
            datanum=0
            IMG = bsobj.findAll('img',{'class':'PlayerImage_image__1smob w-10/12 mx-auto mt-16 md:mt-24'})
            self.data["teams"][thisteam]["playerData"][nameofplayer[0].get_text()+" "+nameofplayer[1].get_text()]["playerIMG"] = IMG[0]["src"]
            for i in playerINFO:
                self.data["teams"][thisteam]["playerData"][nameofplayer[0].get_text()+" "+nameofplayer[1].get_text()]["State"][dataColumn[datanum]] = i.get_text()  #teamlist=tname
                datanum+=1
            infoOfPlayer=bsobj.findAll('p',{"class":"PlayerSummary_playerInfoValue__mSfou"})
            infolabel=bsobj.findAll('p',{"class":"PlayerSummary_playerInfoLabel__gBXXP"})
            infolist=[]
            for k in infolabel:
                infolist.append(k.get_text())
            infonum=0
            for ii in infoOfPlayer:
                self.data["teams"][thisteam]["playerData"][nameofplayer[0].get_text()+" "+nameofplayer[1].get_text()]["Info"][infolist[infonum]] = ii.get_text()  #teamlist=tname
                infonum+=1

    def writeData(self):
        self.data["updateTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("data.json", "w") as f:
            json.dump(self.data, f)

    def end(self):
        self.browser.close()

if __name__ == "__main__":
    Fetch()
