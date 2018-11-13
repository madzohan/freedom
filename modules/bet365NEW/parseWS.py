import time
import re
import json
import pandas as pd
from sqlalchemy import create_engine
import os
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import gc
import objgraph
from sys import getrefcount
import pickle

####数据有漏抓的情况，S1,S3
class basketball():

    def __init__(self,driver):
        self.driver = driver

    def parse(self,gameinfo):
        self.gameinfo = gameinfo
        self.driver.refresh()###要不后面采不到'EV;C1=' in message
        wait = WebDriverWait(self.driver, 120)
        while True:
            messages = self.driver.get_log('performance')
            for message in messages:
                try:
                    message = json.loads(message['message'])['message']['params']['response']['payloadData']
                except KeyError:
                    continue
                if self.Flag:
                    self.parseVC(message)
                    endtime = datetime.datetime.now()
                    if (endtime - starttime) > datetime.timedelta(hours=4):
                        self.save()
                        break
                    if self.GameOver:
                        self.save()
                        break
                else:
                    try:
                        self.parseID(message)
                    except KeyError:
                        continue
                    wait = WebDriverWait(self.driver, 60)
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="比赛现场"]')))
                    element.click()
            if self.GameOver:
                break


   






