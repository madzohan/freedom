from selenium.webdriver import Chrome,ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import PyChromeDevTools
from nba_playbyplay1 import nba
class bet365():
    def __init__(self):
        self.Date = datetime.datetime.today().strftime('%Y%m%d')
        self.driver_path = 'C:/Users/Administrator/Downloads/chromedriver'
        self.Options = ChromeOptions()
        self.url ="https://www.7788365365.com/?&cb=105812118651#/IP/"
    def navigate(self,index):
        driver_game = Chrome(chrome_options=self.Options, executable_path = self.driver_path)
        driver_game.get(self.url)
        driver_game.find_element_by_xpath('//div[@title="现场滚球盘"]').click()
        wait = WebDriverWait(driver_game, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH ,'//a[text()="滚球盘"]')))
        element.click()
        wait = WebDriverWait(driver_game, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH ,'//div[text()="盘口查看"]')))
        element.click()
        wait = WebDriverWait(driver_game, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH ,'//div[text()="篮球"]')))
        element.click()
        driver_game.find_elements_by_xpath('//div[contains(@class,"ipo-Fixture_ScoreDisplay ipo-ScoreDisplayPoints")]')[index]

    def ChromeDevToolsConnect(self):
        chrome = PyChromeDevTools.ChromeInterface()
        chrome.Network.enable()
        chrome.DOM.enable()
        chrome.Page.navigate(url = self.url)
        chrome.ws.settimeout(10)
        return chrome


    def gameRefresh(self):
        driver = Chrome(chrome_options=self.Options, executable_path=self.driver_path)
        driver.get(self.url)
        driver.find_element_by_xpath('//div[@title="现场滚球盘"]').click()
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH ,'//a[text()="滚球盘"]')))
        element.click()
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH ,'//div[text()="盘口查看"]')))
        element.click()
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH ,'//div[text()="篮球"]')))
        element.click()
        teams = driver.find_elements_by_xpath('//div[contains(@class,"ipo-Fixture_ScoreDisplay ipo-ScoreDisplayPoints")]')
        game =[]
        for index,team in enumerate(teams):
            self.navigate(index)
            chrome = ChromeDevToolsConnect
            game = nba(page.chrome)
            teamAway = team.text.split("\n")[0]
            teamHome = team.text.split("\n")[1]
            game.append(teamAway+'VS'+teamHome+Date)
        games = driver.find_elements_by_xpath('//div[contains(@class,"ipo-FixtureEventCountButton_EventCountWrapper")]')
        driver.refresh()
        p=0





