#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, MoveTargetOutOfBoundsException 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import re
import time
import json
import os


class EasyApplyLinkedin:

    def __init__(self, data):
        """Parameter initialization"""

        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Firefox(executable_path=data['driver_path'])
  
    def job_search(self):
        """This function goes to the 'Jobs' section a looks for all the jobs that matches the keywords and location"""

        # Jobs methods selected
        easy_apply = '?f_AL=true&f_WT=2&geoId=92000000'
  
        job_link = self.driver.get('https://www.linkedin.com/jobs/search/'+ easy_apply +'&keywords='+ self.keywords +'&location=' + self.location)
    
    def login_linkedin(self):
        
        login = self.driver.find_element(By.XPATH, "/html/body/div[1]/header/nav/div/a[2]")
        login.click()
        time.sleep(1)
        login_email = self.driver.find_element(By.XPATH, "//*[@id='username']")
        login_email.clear()
        login_email.send_keys(self.email)
        login_pass = self.driver.find_element(By.XPATH, "//*[@id='password']")
        login_pass.clear()
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.RETURN)
        
    def scroll_shim(self):
        
        lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
            lastCount = lenOfPage
            time.sleep(3)
            lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount == lenOfPage:
                match=True
    
    def find_offers(self):
        """This function finds all the offers through all the pages result of the search and filter"""

        time.sleep(5)
        # find the total amount of results (if the results are above 24-more than one page-, we will scroll trhough all available pages)
        total_results = self.driver.find_element(By.CLASS_NAME,"display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print("total result",total_results_int)
        
        time.sleep(5)
        # get results for the first page
        current_page = self.driver.current_url
        
        results = self.driver.find_elements(By.CLASS_NAME,"ember-view.jobs-search-results__list-item.occludable-update.p0.relative")
        
        # for each job add, submits application if no questions asked
        for result in results:
            
            self.scroll_shim()
            time.sleep(2)
            
            try:
                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                time.sleep(1)
                titles = result.find_elements(By.CLASS_NAME,'full-width.artdeco-entity-lockup__title.ember-view')
                for title in titles:
                    self.submit_apply(title)
                
            except (StaleElementReferenceException, MoveTargetOutOfBoundsException):
                pass
                     
        # if there is more than one page, find the pages and apply to the results of each page
        if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct url of each page based on the total amount of pages
            find_pages = self.driver.find_elements(By.CLASS_NAME,"artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view")
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element(By.XPATH,"//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=',1)[1])

            # go through all available pages and job offers and apply
            for page_number in range(25,total_jobs+25,25):
                self.driver.get(current_page+'&start='+str(page_number))
                time.sleep(5)
                results_ext = self.driver.find_elements(By.CLASS_NAME,"ember-view.jobs-search-results__list-item.occludable-update.p0.relative")
                
                for result_ext in results_ext: 
                    self.scroll_shim()
                    time.sleep(2)
                    
                    try:     
                        hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                        hover_ext.perform()
                        time.sleep(1)
                        titles_ext = result_ext.find_elements(By.CLASS_NAME,'full-width.artdeco-entity-lockup__title.ember-view')
                        for title_ext in titles_ext:
                            self.submit_apply(title_ext)
                        
                    except (StaleElementReferenceException,MoveTargetOutOfBoundsException):
                        pass
                    
        else:
            self.close_session()
            
    #case 1: Submit
    def quick_apply(self):
        # try to submit if submit application is available... 
        #quick_apply
        try:
            unfollow = self.driver.find_element(By.XPATH,"//input[@id='follow-company-checkbox']")
            if unfollow.is_selected():
                #uncheck
                self.driver.execute_script("arguments[0].click();",unfollow)
            time.sleep(1)
            submit = self.driver.find_element(By.XPATH,"//button[@aria-label='Submit application']")
            submit.click()
            time.sleep(1)
            print('Your application is successful...')
            
            try:
                done_button = self.driver.find_element(By.XPATH,"//button[@id]")
                done_button.send_keys(Keys.RETURN)
                time.sleep(1)
            
            except (NoSuchElementException, StaleElementReferenceException, MoveTargetOutOfBoundsException):
                discard_applied = self.driver.find_element(By.XPATH,"//button[@data-test-modal-close-btn]")
                discard_applied.send_keys(Keys.RETURN)
                time.sleep(1)
          
        except (NoSuchElementException, StaleElementReferenceException, MoveTargetOutOfBoundsException):
            pass
                   
        time.sleep(1)
    
    #case 2: Submit+Next
    def quick_apply_next(self):
        # try to submit if submit application is available... 
        #quick_apply_next
        try:        
            next_button = self.driver.find_element(By.XPATH,"//button[@aria-label='Continue to next step']")
            next_button.click()
            time.sleep(1)
            review_button = self.driver.find_element(By.XPATH,"//button[@aria-label='Review your application']")
            review_button.click()
            time.sleep(1)

            unfollow = self.driver.find_element(By.XPATH,"//input[@id='follow-company-checkbox']")
            if unfollow.is_selected():
                #uncheck
                self.driver.execute_script("arguments[0].click();",unfollow)

            submit_app = self.driver.find_element(By.XPATH,"//button[@aria-label='Submit application']")
            submit_app.click()
            time.sleep(1)
            print('Next option selected, your application is successful...')

            try:
                done_button_next = self.driver.find_element(By.XPATH,"//button[@id]")
                done_button_next.send_keys(Keys.RETURN)
                time.sleep(1)

            except (NoSuchElementException, StaleElementReferenceException, MoveTargetOutOfBoundsException):
                discard_applied_next = self.driver.find_element(By.XPATH,"//button[@data-test-modal-close-btn]")
                discard_applied_next.send_keys(Keys.RETURN)
                time.sleep(1)

        except (NoSuchElementException,StaleElementReferenceException, MoveTargetOutOfBoundsException):
            pass
    
    #case n: Close apply
    def discard_method(self):
        #Does not have quick application
        try:
            discard = self.driver.find_element(By.XPATH,"//button[@data-test-modal-close-btn]")
            discard.send_keys(Keys.RETURN)
            time.sleep(1)
            discard_confirm = self.driver.find_element(By.XPATH,"//button[@data-test-dialog-secondary-btn]")
            discard_confirm.send_keys(Keys.RETURN)
            time.sleep(1)
            print('Not direct application, going to next...')
        except NoSuchElementException:
            pass
        
    def submit_apply(self,job_add):
        """This function submits the application for the job add found"""

        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(2)
               
        # click on the easy apply button, skip if already applied to the position
        try:
            in_apply = self.driver.find_element(By.XPATH,"//button[@data-job-id]")
            in_apply.click()
        
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass
        time.sleep(1)
        
        #Case for applications
        self.quick_apply()
        time.sleep(1)
        self.quick_apply_next()
        time.sleep(1)
        self.discard_method()
        time.sleep(1)
            
    def close_session(self):
        """This function closes the actual session"""
        
        print('End of the session, see you later!')
        self.driver.close()

    def apply(self):
        """Apply to job offers"""

        self.driver.maximize_window()
        time.sleep(2)
        self.job_search()
        time.sleep(2)
        self.login_linkedin()   
        time.sleep(2)
        self.find_offers()
        time.sleep(2)
        self.close_session()


if __name__ == '__main__':

    os.chdir(r'C:\Linkedin_EasyApply_Job_Search_Bot')

    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()




