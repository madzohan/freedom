from selenium.webdriver import Chrome,ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import datetime
logging.
import requests
Date = datetime.datetime.today().strftime('%Y%m%d')
driver_path = 'C:/Users/Administrator/Downloads/chromedriver'
options = ChromeOptions()
# options.add_argument('--headless')
driver = Chrome(chrome_options=options, executable_path = driver_path,port =9220)

driver.debugger_address
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
for team in teams:
    teamAway = team.text.split("\n")[0]
    teamHome = team.text.split("\n")[1]
    game.append([teamAway,teamHome])
games = driver.find_elements_by_xpath('//div[contains(@class,"ipo-FixtureEventCountButton_EventCountWrapper")]')
driver.refresh()
p=0
