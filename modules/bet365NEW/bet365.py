from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import datetime
import time
import random,re
import json,redis
import pickle

class inplay():

    def __init__(self):
        self.Date = datetime.datetime.today().strftime('%Y%m%d')
        self.caps = DesiredCapabilities.CHROME
        self.caps['loggingPrefs'] = {'performance': 'INFO'}
        self.chrome_options = Options()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        self.chrome_options.add_argument(f'user-agent={user_agent}')
        # self.chrome_options.add_argument("--headless")
        self.driver_path = 'E:/code/chromedriver'
        self._INPLAY_BASKETBALL_MS = re.compile(r'\|EV;AU=0;C1=1;C2=\d{6,8}.*?(?=\|EV;AU=0;)')
        self.NA = re.compile(r'(?<=NA=).*?(?=;)')  # name
        self.CC = re.compile(r'(?<=CC=).*?(?=;)')
        self.C2 = re.compile(r'(?<=C2=).*?(?=;)')
        self.ID = re.compile(r'(?<=ID=)\w*?(?=;)')
        self.r = redis.Redis(host='127.0.0.1', port=6379)
        self.driver = webdriver.Chrome(desired_capabilities=self.caps, executable_path=self.driver_path,
                                       chrome_options=self.chrome_options)
        self.driver.set_page_load_timeout(30)
        # self.driver.set_window_position(-1500, 1050)
        self.wait_60 = WebDriverWait(self.driver, 60)
        self.wait_10 = WebDriverWait(self.driver, 10)
        self.wait_5 = WebDriverWait(self.driver, 5)

    def web(self):
        while True:
            try:
                self.driver.get('https://www.635288.com/')
                break
            except:
                pass
        while True:
            try:
                self.wait_10.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="English"]'))).click()
                self.wait_10.until(EC.element_to_be_clickable((By.XPATH, '//div[@title="Live In-Play"]'))).click()
                break
            except:
                self.driver.refresh()
                print('重新加载页面')

    def overview(self):
        while True:
            try:
                self.wait_60.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="In-Play"]'))).click()
                self.wait_60.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Overview"]'))).click()
                break
            except:
                self.driver.refresh()
                print('重新加载页面')

    def game_update(self):
        while True:
            self.driver.refresh()
            while True:
                flag =False
                messages = self.driver.get_log('performance')
                for message in messages:
                    try:
                        message = json.loads(message['message'])['message']['params']['response']['payloadData']
                    except KeyError:
                        continue
                    if '\x14OVInPlay' in message[:10] :
                        games = self.parse_OVInPlay(message)
                        past = self.r.smembers('messages')
                        past_str = set([x.decode() for x in past])
                        for value in past:
                            self.r.srem('messages', value)
                        now = set()
                        for cell in games:
                            self.r.sadd('messages', cell['messages'])
                            self.r.sadd('games', cell['games'])
                            now.add(cell['messages'])
                        update = now - past_str
                        for cell in update:
                            self.r.sadd('update', cell)
                        for cell in self.r.smembers('update'):
                            self.r.srem('update', cell)
                        flag = True
                        break
                if flag:
                    break
            print('更新比赛嘻嘻！！！')
            self.driver.quit()
            time.sleep(random.randint(300, 400))

    def parse_OVInPlay(self, message):
        games = []
        basketball = self._INPLAY_BASKETBALL_MS.findall(message)
        for cell in basketball:
            dict = {}
            dict['messages'] = '15' + self.C2.findall(cell)[0] + '5M18_1_3' + '@' + self.ID.findall(cell)[0] + '@' + \
                               self.NA.findall(cell)[0]
            dict['games'] = self.NA.findall(cell)[0]
            games.append(dict)
        return games

    def login(self):
        while True:
            try:
                self.wait_60.until(EC.element_to_be_clickable(
                    (By.XPATH, '//input[@class = "hm-Login_InputField "]')))

                break
            except:
                continue
        elements = self.driver.find_elements_by_xpath('//input[@class = "hm-Login_InputField "]')
        account = elements[0]
        pw = elements[1]
        account.click()
        account.clear()
        account.send_keys('pxpwoa')
        while True:
            try:
                pw = self.driver.find_elements_by_xpath('//input[@class = "hm-Login_InputField "]')[1]
                pw.send_keys('nimabi')
                break
            except:
                pw = self.driver.find_elements_by_xpath('//input[@class = "hm-Login_InputField "]')[1]
                pw.click()
        pw = self.driver.find_elements_by_xpath('//input[@class = "hm-Login_InputField "]')[1]
        pw.clear()
        pw = self.driver.find_elements_by_xpath('//input[@class = "hm-Login_InputField "]')[1]
        pw.send_keys('nimabi3927493')
        pw = self.driver.find_element_by_xpath('//button[@class = "hm-Login_LoginBtn "]')
        pw.click()
        time.sleep(4)
        self.close_message()

        pass

    def login_cookies(self):
        self.driver.get('https://www.635288.com/')
        self.load_cookies()
        self.driver.refresh()
        while True:
            try:
                self.wait_10.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="wl-PushTargetedMessageOverlay_CloseButton "]'))).click()
                self.wait_60.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="In-Play"]'))).click()
                self.wait_60.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Overview"]'))).click()
                break
            except:
                self.driver.refresh()
                print('重新加载页面')
    def close_message(self):
        try:
            self.wait_10.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="wl-PushTargetedMessageOverlay_CloseButton "]'))).click()
        except:
            pass
    def bank(self):
        element = self.wait_60.until(EC.visibility_of_element_located((By.XPATH, '//div[@class = "hm-MembersInfoButton_BankInfo "]')))
        rmb = element.text.split(' ')[0]
        return rmb

    def basketball(self):
        self.overview()
        element = self.wait_10.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Basketball"]')))
        element.click()

    def my_bets(self):
        while True:
            try:
                self.wait_60.until(EC.visibility_of_element_located((By.XPATH, '//div[@class = "bw-BetslipHeader_Item "]'))).click() ## mybets
                self.wait_60.until(EC.visibility_of_element_located((By.XPATH, '//div[@class = "mbr-OpenBetItemsContainerRhs "]')))
                break
            except:
                self.driver.refresh()
        while True:
            try:
                self.wait_5.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class = "mbr-ShowMoreBetsButtonRhs_Label "]'))).click()
            except:
                break
        bets_cashOut = self.driver.find_elements_by_xpath('//div[@class = "mbr-OpenBetItemRhs "]')
        self.driver.find_elements_by_xpath('//div[text()="Live"]')[0].click()
        while True:
            try:
                self.wait_5.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class = "mbr-ShowMoreBetsButtonRhs_Label "]'))).click()
            except:
                break
        bets_live = self.driver.find_elements_by_xpath('//div[@class = "mbr-OpenBetItemRhs "]')

    def save_cookies(self):
        self.login()
        with open('cookies.pickle', 'wb') as filehandler:
            pickle.dump(self.driver.get_cookies(), filehandler)

    def load_cookies(self):
        with open('cookies.pickle', 'rb') as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def set_bets(self,team_home,uint,bet):
        team_home =  'Legia Warsaw'
        bet = 'U'
        element = self.wait_5.until(
            EC.visibility_of_element_located((By.XPATH, "//div/span[text()='" + team_home + "']")))
        parent_elem = element.find_element_by_xpath('..')
        parent_elem = parent_elem.find_element_by_xpath('..')
        parent_elem = parent_elem.find_element_by_xpath('..')
        parent_elem = parent_elem.find_element_by_xpath('..')
        parent_elem = parent_elem.find_element_by_xpath('..')
        bets =parent_elem.find_element_by_xpath(".//span[contains(text(), '" + bet + "')]").click()
        element.click()

    def quick_bet(self):
        self.overview()
        self.wait_10.until(EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class = "bw-BetslipHeader "]/div[text()="Bet Slip"]')))
        self.driver.switch_to.frame("bsFrame")
        self.wait_60.until(
            EC.visibility_of_element_located((By.XPATH, "//span[@class='qb-Btn_Switch-false']"))).click()
        self.driver.switch_to.default_content()
    def refresh(self):
        self.driver.refresh()
if __name__ =='__main__':
    page = inplay()
    page.web()
    page.login()
    bank = page.bank()
    # page.my_bets()
    page.basketball()
    page.quick_bet()
    page.refresh()
    pass