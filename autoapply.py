from colorama.ansi import clear_screen
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style
from time import sleep, time
from random import randint, choice, uniform
import json
import os
from pwinput import pwinput

init(convert=True)
init(autoreset=True)

bright = Style.BRIGHT
dim = Style.DIM
red = Fore.RED + dim
green = Fore.GREEN + dim
cyan = Fore.CYAN + dim
yellow = Fore.LIGHTYELLOW_EX + dim
blue = Fore.BLUE + dim
white = Fore.WHITE + dim
magenta = Fore.MAGENTA + dim

# Config
URL_ROOT = "https://www.linkedin.com/"
CONFIG_FILE = "Config.json"
LOGIN_MAX_RETRIES = 10


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

class AutoApplier:

    def __init__(self,
                 username,
                 password,
                 loc_list,
                 experience,
                 keywords,
                 is_silent
                 ):

        self.username = username
        self.password = password
        self.loc_list = loc_list
        self.experience = experience
        self.keywords = keywords
        self.is_silent = is_silent

    def create_session(self):
        options = Options()

        # Standard settings
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3");

        # Run chrome on the background
        if self.is_silent:
            options.headless = True
            mode_str = "Headless"
        else:
            mode_str = "Visible"

        # Avoid detection 1
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Create session
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # Avoid detection 2
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": "Mozilla/5.0 (X11; CrOS x86_64 13904.97.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.167 Safari/537.36"})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("\n{}[Created selenium session - {} mode]\n\n".format(green, mode_str))

        return self.driver

    def fill_field(self, object, text):
        sleep(uniform(0.1, 0.3))
        object.click()
        for char in text:
            object.send_keys(char)
            sleep(uniform(0.04, 0.13))
        sleep(uniform(0.1, 0.3))

    def do_login(self):

        driver = self.driver

        # Main page
        main_page = driver.get(URL_ROOT)
        go_to_login = driver.find_element_by_class_name("nav__button-secondary").click()

        # Login page
        usr_box = driver.find_element_by_name("session_key")
        self.fill_field(usr_box, self.username)

        pwd_box = driver.find_element_by_name("session_password")
        self.fill_field(pwd_box, self.password)

        submit_login = driver.find_element_by_class_name("login__form_action_container").click()

        # Captcha
        while True:
            try:
                checkpoint_element = driver.find_element_by_id("captchaInternalPath")
            except:
                break
            print("{}CHALLENGE REQUIRED".format(yellow))
            sleep(3)

        # Email verification
        while True:
            try:
                email_verify = driver.find_element_by_id("input__email_verification_pin")
            except:
                break
            print("{}EMAIL VERIFICATION REQUIRED".format(yellow))
            sleep(3)

        count = 0
        while True:
            try:
                message_list = driver.find_element_by_id("msg-overlay")
                break
            except Exception as error:
                if count >= LOGIN_MAX_RETRIES:
                    return False
                print("{}Waiting for feed to load ({}/{})".format(yellow))
                sleep(3)
                count += 1

        return True
    
    def get_location(self):
        driver = self.driver
        loc_list = self.loc_list
        
        driver.get(URL_ROOT + "jobs/")
        sleep(3)
        job_location_field = driver.find_elements_by_class_name("jobs-search-box__inner")[1]
        last_loc = driver.current_url
        added_count = 0
        
        for loc in loc_list:
            if loc_list[loc] == "":
                job_location_field.click()
                sleep(3.5)
                actions = ActionChains(driver)
                actions.send_keys(loc)
                actions.perform()
                print("Click on the location you wish to use for \'{}\' and press enter".format(loc))
                while True:
                    input()
                    if last_loc == driver.current_url:
                        print(red + "You must select a location first")
                        continue
                    else:
                        # pretty messy
                        try:
                            loc_list[loc] = driver.current_url
                            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                data["locations"][loc] = driver.current_url
                                f.close()
                                
                            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False)
                                f.close()
                            
                            print("{}Added {}".format(green, loc))
                            added_count += 1
                            break
                        except Exception as error:
                            print("{}Error adding {}".format(red, loc))
                            print(error)
                            
            else:
                added_count += 1
                
        if added_count == 0:
            raise ValueError('Geographical location setup failed')
        else:
            print("{}Geographical location setup finished".format(yellow))
            return loc_list
            
        
    def find_jobs(self, location):
        driver = self.driver
        experience = self.experience
        
        driver.get(self.loc_list[location])
        
        # Job position name
        job_name_field = driver.find_elements_by_class_name("jobs-search-box__text-input.jobs-search-box__keyboard-text-input")[0]
        self.fill_field(job_name_field, self.keywords)
        job_name_field.send_keys(Keys.ENTER)
        sleep(3)
        
        # Easy apply
        final_url = driver.current_url + "&f_AL=true"
        
        # Filter by experience
        final_url += "&f_E="
        for num, exp in enumerate(experience):
            if experience[exp]:
                final_url += str(num + 1) + ","
        
        # Send parameters
        driver.get(final_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results__list.list-style-none")))
            
        # Return job list
        return driver.find_element_by_class_name("jobs-search-results__list.list-style-none").find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")
        
            

    def start_apply(self):
        
        login_success = self.do_login()
        if login_success:
            print("\n{}Successfully logged in as {}".format(green, self.username))
        else:
            print("\n{}Couldn't log in as {}".format(red, self.username))
            raise ValueError('Error logging in')
        
        locations = self.get_location()
        job_count = 0

        for location in locations:
            print("\n\n{}- Loading jobs in {} -".format(yellow, location))
            job_list = self.find_jobs(location)
            sleep(4)
            # Apply for jobs
            for x in job_list:
                
                x.click()
                sleep(4)
                # Apply button
                try:
                    apply_button = driver.find_element_by_class_name("jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view")
                    apply_button.click()
                except:
                    print("Already applied")
                    continue
                try:
                    sleep(3)
                    # Next button (contact info)
                    next_button = driver.find_element_by_class_name("artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view")
                    next_button.click()
                    sleep(4)
                    # Next button (resume)
                    next_button.click()
                    sleep(4)
                    # Allowed to work here?
                    allowed_to_work = driver.find_element_by_class_name("fb-radio.display-flex").find_element_by_tag_name("label")
                    allowed_to_work.click()
                    sleep(4)
                    # Review button
                    next_button = driver.find_element_by_class_name("artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view")
                    next_button.click()
                    sleep(4)
                    # Send 
                    next_button = driver.find_element_by_class_name("artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view")
                    next_button.click()
                    sleep(5)
                
                except Exception as e:
                    print("Error applying - {}".format(e))
                    print(e)
                
                try:
                    WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CLASS_NAME, "artdeco-modal__dismiss.artdeco-button.artdeco-button--circle.artdeco-button--muted.artdeco-button--2.artdeco-button--tertiary.ember-view")))
                    dismiss_premium = driver.find_element_by_class_name("artdeco-modal__dismiss.artdeco-button.artdeco-button--circle.artdeco-button--muted.artdeco-button--2.artdeco-button--tertiary.ember-view")
                    dismiss_premium.click()
                    
                    WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CLASS_NAME, "artdeco-modal__confirm-dialog-btn.artdeco-button.artdeco-button--2.artdeco-button--secondary.ember-view")))
                    confirm_dismiss = driver.find_element_by_class_name("artdeco-modal__confirm-dialog-btn.artdeco-button.artdeco-button--2.artdeco-button--secondary.ember-view")
                    confirm_dismiss.click()
                except Exception as e:
                    continue
                
                job_count += 1
                print("{}Successfully applied to {} jobs".format(green, job_count))

                
            input()




if __name__ == '__main__':
    cls()

    if not os.path.exists(CONFIG_FILE):
        # Credentials
        print("{}\n\n*** CREDENTIALS ***".format(cyan))
        conf_username = input("> Linkedin email/phone: ")
        conf_password = pwinput(prompt='> Linkedin password: ', mask='*')
        
        # Geolocations
        print("{}\n*** GEOLOCATION ***".format(cyan))
        conf_locations = {}
        while True:
            loc = input("> Add geographical location? (y/N): ").lower()
            if loc == "n" or loc == "no" or loc == "":
                if len(conf_locations) == 0:
                    print(red + "At least 1 location must be added!")
                    continue
                else:
                    break
            else:
                loc = input(" - ")
                if loc != "":
                    conf_locations[loc] = ""
                    
        # Experience
        print("{}\n*** EXPERIENCE ***".format(cyan))
        conf_experience = {
            "Internship": False,
            "Entry level": False,
            "Associate": False,
            "Mid-Senior level": False,
            "Director": False,
            "Executive": False
        }
        
        while True:
            print("Select one or more experience levels (1-6) or type \'quit\':")
            for num, exp_lvl in enumerate(conf_experience):
                if conf_experience[exp_lvl]:
                    color = green
                else:
                    color = red
                    
                print("{}{}. {}".format(color, num+1, exp_lvl))
            
            exp_lvl = input("\n> ")
            if exp_lvl == "quit":
                break
            elif exp_lvl == "":
                print(red + "Cannot leave field blank")
                continue
            else:
                try:
                    exp_lvl = int(exp_lvl)
                except:
                    print(red + "You must introduce a number!")
                    continue
                if exp_lvl < 1 or exp_lvl > 6:
                    print(red + "Invalid number")
                    continue
                
                
                conf_experience[list(conf_experience)[exp_lvl - 1]] = not conf_experience[list(conf_experience)[exp_lvl - 1]]
                
        conf_keywords = input("> Name of the job: ")
                
        # Save to file
        to_save = {
            "username": conf_username,
            "password": conf_password,
            "locations": conf_locations,
            "keywords": conf_keywords,
            "experience": conf_experience
        }

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(to_save, f, ensure_ascii=False)
    else:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            conf_username = data["username"]
            conf_password = data["password"]
            conf_locations = data["locations"]
            conf_keywords = data["keywords"]
            conf_experience = data["experience"]
    sleep(2)
    
    

    
    cls()
    print("{}\n\nLinkedin bot loaded! Running...\n".format(cyan))
    autoapply = AutoApplier(conf_username, conf_password, conf_locations, conf_experience, conf_keywords, False)
    driver = autoapply.create_session()
    result = autoapply.start_apply()