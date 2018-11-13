from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.action_chains import ActionChains
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
        self.chrome_options.add_argument("--start-maximized")
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
        # self.driver.set_page_load_timeout(2)
        # self.driver.set_window_position(-1500, 1050)
        self.wait_60 = WebDriverWait(self.driver, 60)
        self.wait_30 = WebDriverWait(self.driver, 30)
        self.wait_20 = WebDriverWait(self.driver, 20)
        self.wait_15 = WebDriverWait(self.driver, 15)
        self.wait_10 = WebDriverWait(self.driver, 10)
        self.wait_5 = WebDriverWait(self.driver, 5)

    def web(self):
        while True:
            try:
                self.driver.get('https://www.wellbetbest.net')
                break
            except:
                pass

    def login(self):
        self.wait_60.until(EC.element_to_be_clickable(
            (By.XPATH, '//li[@class = "button-dropdown authenticate"]'))).click()
        account = self.wait_60.until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@class = "form-control ng-untouched ng-pristine ng-valid"]')))
        account.click()
        account.clear()
        account.send_keys('pxpwoa')
        pw = self.wait_60.until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@class = "form-control ng-untouched ng-pristine ng-valid"]')))
        pw.click()
        pw.clear()
        pw.send_keys('nimabi3927493')
        self.wait_60.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@class = "btn btn_red btn_200"]'))).click()
        time.sleep(1)
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
    def sport(self):
        while True:
            try:
                self.wait_60.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="体育"]'))).click()
                self.wait_60.until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, 'eng2')))
                element = self.wait_10.until(
                    EC.visibility_of_element_located((By.XPATH, '//div[@class = "sportMenu"]')))
                ActionChains(self.driver).move_to_element(element)
                break
            except:
                print('reload')
                self.refresh()

                # time.sleep(2)
                continue

    def bank(self):
        self.sport()
        element = self.wait_60.until(EC.visibility_of_element_located((By.XPATH, '//span[@class = "mg-l-4 ft-c-50 fts-14"]')))
        rmb = element.text.split(' ')[1]
        return rmb

    def basketball(self):
        while True:
            try:
                self.wait_30.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//div[@class = "dsp-tbcl pd-l-10 pd-t-10 pd-b-10 t-va-m t-a-c width-50p"]'))).click()
                break
            except:
                self.sport()
                continue
        try:
            # self.driver.find_element_by_xpath('//span[text() = "篮球"]').click()
            self.wait_5.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text() = "篮球"]'))).click()
        except:
            print('当前无篮球赛事！')

    def my_bets(self):
        self.wait_10.until(EC.visibility_of_element_located((By.XPATH, '//span[@class = "filters-lv1 pos-relative uppercase"]'))).click() ## mybets
        self.wait_60.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class = "dsp-tbcl pd-l-10 pd-t-10 pd-b-10 t-va-m t-a-c width-50p"]'))).click()
    def set_bets(self):
        self.basketball()
        team =  '密尔沃基雄鹿'
        bet = '小'
        index = 1 if bet =='小' else 2
        stake = 5

        elements = self.wait_5.until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[text()[contains(.,'" + team + "')]]")))
        if len(elements) > index:
            element=elements[index]
            parent_elem = element.find_element_by_xpath('..')
            parent_elem = parent_elem.find_element_by_xpath('..')
            wait = WebDriverWait(parent_elem,5)
            wait.until(  EC.element_to_be_clickable(
                    (By.XPATH, ".//td[@class='t-a-c rbr-c-6 col-ou']//span[@title= '" + bet + "']"))).click()
            self.set_stake(stake)
            self.confirm_bet()
            try:
                self.accept_adjustment()
                print('接受赔率调整')
            except:
                pass
            try:
                self.check_bet()
                print('投注成功！')
            except:
                print('投注失败！')
            self.return_inplay()
    def set_stake(self,stake):
        element_stake = self.wait_5.until(EC.element_to_be_clickable(
            (By.XPATH, ".//input[@class= 'js-stake width-100p hiddenInput ft-c-22']")))
        element_stake.click()
        element_stake.send_keys(stake)
    def accept_adjustment(self):
        self.wait_5.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@class= 'js-accept width-100p hiddenInput t-a-c ft-c-58 fontWeight-bold pointerbt uppercase']"))).click()

    def confirm_bet(self):
        self.wait_5.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@class= 'js-placebet width-100p t-a-c ft-c-51 fontWeight-bold pointerbt uppercase']"))).click()
    def check_bet(self):
        self.wait_5.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[@class= 'icon-CheckIcon fts-16 t-va-tbot mg-r-4 t-va-m']")))

    def return_inplay(self):
        self.wait_5.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@class= 'return lht-35 bg-c-18 pd-l-10 pd-r-10 clickable']"))).click()

    def refresh(self):
        self.driver.refresh()
    def quit(self):
        self.driver.quit()
if __name__ =='__main__':
    page = inplay()
    page.web()
    page.login()
    bank = page.bank()
    # page.my_bets()
    page.set_bets()

    pass