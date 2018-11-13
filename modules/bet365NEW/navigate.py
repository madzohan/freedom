import PyChromeDevTools
import re
import time
from bs4 import BeautifulSoup

class chrome():

    def __init__(self,teamAway,teamHome,league):
        self.teamAway =teamAway
        self.teamHome = teamHome
        self.league = league
        chrome = PyChromeDevTools.ChromeInterface()
        new_tab = chrome.Target.createTarget(url="https://www.7788365365.com/?&cb=105812118651#/IP/")
        self.targetID = new_tab["result"]["targetId"][1:-1]
        # print('targetID：'+targetID)
        chrome = PyChromeDevTools.ChromeInterface() ##不能删，什么用来着
        chrome.connect_targetID(self.targetID)
        chrome.Network.enable()
        chrome.Page.enable()
        chrome.DOM.enable()
        chrome.Page.javascriptDialogOpening()
        chrome.Page.handleJavaScriptDialog()
        chrome.Page.deleteCookie()
        Date = str(time.localtime()[0]) +str(time.localtime()[1])+str(time.localtime()[2])
        time.sleep(1)
        self.chrome = chrome

    def mouseLeftClick(self,nodeStr,index):
        document = self.chrome.DOM.getDocument(depth =-1)
        node_id=self.chrome.DOM.querySelectorAll(nodeId=document['result']['root']['nodeId'],selector = nodeStr)
        box = self.chrome.DOM.getBoxModel(nodeId=node_id['result']['nodeIds'][index])
        x = box['result']['model']['border'][0]
        y = box['result']['model']['border'][1]
        delta_x = box['result']['model']['width']
        delta_y = box['result']['model']['height']
        # print(nodeStr,x,y,delta_x,delta_y)
        # for index,id in enumerate(node_id['result']['nodeIds']):
        #     print(self.chrome.DOM.getOuterHTML(nodeId=id )['result']['outerHTML'])
        self.chrome.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                        button='left')
        self.chrome.Input.dispatchMouseEvent(type="mousePressed", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                        button='left')
        self.chrome.Input.dispatchMouseEvent(type="mouseReleased", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                        button='left')
    def mouse_dragDown(self):
        document = self.chrome.DOM.getDocument(depth =-1)
        bar_id=self.chrome.DOM.querySelectorAll(nodeId=document['result']['root']['nodeId'],selector = 'div.ipf-FloatScroller_ScrollBar')
        bar_box = self.chrome.DOM.getBoxModel(nodeId=bar_id['result']['nodeIds'][0])
        container_id = self.chrome.DOM.querySelectorAll(nodeId=document['result']['root']['nodeId'],
                                                   selector='div.ipf-FloatScroller_ScrollContainer')
        container_box = self.chrome.DOM.getBoxModel(nodeId=container_id['result']['nodeIds'][0])
        x = bar_box['result']['model']['border'][0]
        y = bar_box['result']['model']['border'][1]
        # y_dif =  container_box['result']['model']['height'] -bar_box['result']['model']['height']-2
        y_m = container_box['result']['model']['border'][5]-2
        delta_x = bar_box['result']['model']['width']
        delta_y = bar_box['result']['model']['height']
        self.chrome.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                        button='left')
        self.chrome.Input.dispatchMouseEvent(type="mousePressed", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                        button='left')

        self.chrome.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y + y_m, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                             button='left')
        self.chrome.Input.dispatchMouseEvent(type="mouseReleased", x=x, y=y + y_m, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                        button='left')
    def expandTheHidden(self):
        document = self.chrome.DOM.getDocument(depth =-1)
        node_id=self.chrome.DOM.querySelectorAll(nodeId=document['result']['root']['nodeId'],selector = 'dic.ipf-competition_Header')
        for id in node_id['result']['nodeIds']:
            box = self.chrome.DOM.getBoxModel(nodeId=id)
            x = box['result']['model']['border'][0]
            y = box['result']['model']['border'][1]
            delta_x = box['result']['model']['width']
            delta_y = box['result']['model']['height']
            self.chrome.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                            button='left')
            self.chrome.Input.dispatchMouseEvent(type="mousePressed", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                            button='left')
            self.chrome.Input.dispatchMouseEvent(type="mouseReleased", x=x, y=y, deltaX=delta_x, deltaY=delta_y, clickCount=1,
                                            button='left')
            try:
                self.mouse_dragDown()
            except:
                continue

    def click(self):
        while True:
            try:
                self.mouseLeftClick('a.hm-BigButton', 1)
                # time.sleep(1)
                break
            except:
                self.chrome.Page.reload()
                self.chrome.Page.javascriptDialogOpening()
                self.chrome.Page.handleJavaScriptDialog()
                time.sleep(5)
        while True:
            try:
                self.mouseLeftClick('div.ip-ControlBar_BBarItem', 1)
                break
            except:
                self.chrome.Page.reload()
                self.chrome.Page.javascriptDialogOpening()
                self.chrome.Page.handleJavaScriptDialog()
                time.sleep(5)
        while True:
            try:
                self.mouseLeftClick('span.ipn-ControlBar_CollapseButton', 0)
                break
            except:
                self.chrome.Page.reload()
                self.chrome.Page.javascriptDialogOpening()
                self.chrome.Page.handleJavaScriptDialog()
                time.sleep(5)

    def page_varidation(self):
        flag = False
        document = self.chrome.DOM.getDocument(depth =-1)
        bar_id=self.chrome.DOM.querySelectorAll(nodeId=document['result']['root']['nodeId'],selector = 'div.ipe-ScoreGridCell_TextTeamName')
        h = self.chrome.DOM.getOuterHTML(nodeId=bar_id['result']['nodeIds'][0])['result']['outerHTML']
        soup = BeautifulSoup(h)
        soup.text
        if soup.text==self.teamAway:
            flag = True
            print('已进入比赛页面'+soup.text)
        return flag

    def game_check(self):
        time.sleep(1)
        flag = False
        document = self.chrome.DOM.getDocument(depth =-1)
        node_id=self.chrome.DOM.querySelectorAll(nodeId=document['result']['root']['nodeId'],selector = 'div.ipf-Fixture_TeamName')
        for index,id in enumerate(node_id['result']['nodeIds']):
            h = self.chrome.DOM.getOuterHTML(nodeId=id )['result']['outerHTML']
            soup = BeautifulSoup(h)
            teams = re.split(r' @ | vs | v ',soup.text)
            # print(teams,self.teamAway)
            if teams[0]==self.teamAway and teams[-1]==self.teamHome:
                # print('！！')
                self.mouseLeftClick('div.ipf-Fixture_TeamName', index)
                flag = True
                break
        return flag


    def basketball(self):
        self.click()# 元素位置不变
        while True:
            time.sleep(5)  # 等待网页加载完成
            self.mouseLeftClick('div.ipn-ClassificationButton_Classification-18', 0)
            time.sleep(1)  # 等待网页加载完成
            self.game_check()
            time.sleep(1)
            flag = self.page_varidation()
            if flag:
                break
            else:
                try:
                    self.mouse_dragDown()
                    time.sleep(1)  # 等待网页加载完成
                    self.game_check()
                    time.sleep(1)
                    flag = self.page_varidation()
                    if flag:
                        break
                    else:
                        self.expandTheHidden()
                        time.sleep(1)  # 等待网页加载完成
                        self.game_check()
                        self.chrome.Page.disable()
                        break
                except:
                    self.expandTheHidden()
                    time.sleep(1)  # 等待网页加载完成
                    self.game_check()
                    break






