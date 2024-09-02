from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import time
import random
import traceback

class LinkedInProfileScraper:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment this line to run in headless mode
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.profiles = []

    def login(self, username, password):
        self.driver.get("https://www.linkedin.com/login")
        self.safe_find_element(By.ID, "username").send_keys(username)
        self.safe_find_element(By.ID, "password").send_keys(password)
        self.safe_find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(random.uniform(3, 5))  # Wait for login to complete

    def search_for_ceo(self):
        try:
            search_input = self.safe_find_element(By.CLASS_NAME, "search-global-typeahead__input")
            if search_input:
                search_input.clear()
                search_input.send_keys("CEO")
                search_input.send_keys(Keys.RETURN)
                print("Entered 'CEO' in the search box and submitted.")
                time.sleep(random.uniform(3, 5))  # Wait for search results to load
            else:
                print("Search input not found.")
        except Exception as e:
            print(f"An error occurred while searching for CEO: {e}")

    def click_people_filter(self):
        try:
            people_filter = self.safe_find_element(By.XPATH, "//button[contains(@class, 'search-reusables__filter-pill-button') and contains(., 'People')]")
            if people_filter:
                people_filter.click()
                print("Clicked on the 'People' filter.")
                time.sleep(random.uniform(2, 4))  # Wait for filter to apply
            else:
                print("People filter not found.")
        except Exception as e:
            print(f"An error occurred while clicking the People filter: {e}")

    def visit_profiles(self):
        try:
            profile_links = self.safe_find_elements(By.XPATH, "//ul[@class='reusable-search__entity-result-list list-style-none']//a[contains(@class, 'app-aware-link')]")
            visited_count = 0

            for i in range(len(profile_links)):
                try:
                    profile_links = self.safe_find_elements(By.XPATH, "//ul[@class='reusable-search__entity-result-list list-style-none']//a[contains(@class, 'app-aware-link')]")
                    link = profile_links[i]
                    profile_url = link.get_attribute('href')
                    self.driver.execute_script("arguments[0].click();", link)
                    visited_count += 1
                    print(f"Visited profile: {visited_count}")
                    
                    profile_data = self.scrape_profile(profile_url)
                    if profile_data:
                        self.profiles.append(profile_data)
                        self.save_to_json()  # Save after each successful scrape
                    
                    time.sleep(random.uniform(2, 4))  # Wait for the profile page to load
                    self.driver.back()  # Go back to the search results page
                    time.sleep(random.uniform(2, 4))  # Wait for the page to load
                except StaleElementReferenceException:
                    print("Encountered stale element, retrying...")
                    continue
                except Exception as e:
                    print(f"Error visiting profile: {e}")
                    traceback.print_exc()

            print(f"Total profiles visited: {visited_count}")
        except Exception as e:
            print(f"An error occurred while visiting profiles: {e}")
            traceback.print_exc()

    def safe_find_element(self, by, value):
        try:
            return self.wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            print(f"Element not found: {value}")
            return None

    def safe_find_elements(self, by, value):
        try:
            return self.wait.until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            print(f"Elements not found: {value}")
            return []

    def scrape_profile(self, profile_url):
        item = {}
        item['url'] = profile_url

        # Name
        name_element = self.safe_find_element(By.XPATH, "//h1[@class='text-heading-xlarge inline t-24 v-align-middle break-words']")
        if name_element:
            item['name'] = name_element.text.strip()

        # Description
        description_element = self.safe_find_element(By.XPATH, "//div[@class='text-body-medium break-words']")
        if description_element:
            item['description'] = description_element.text.strip()

        # Check if "CEO" is in the description
        if "CEO" not in item.get('description', ''):
            return None

        # Location
        location_element = self.safe_find_element(By.XPATH, "//span[@class='text-body-small inline t-black--light break-words']")
        if location_element:
            item['location'] = location_element.text.strip()

        # About
        about_element = self.safe_find_element(By.XPATH, "//div[@class='display-flex ph5 pv3']//span[@aria-hidden='true']")
        if about_element:
            item['about'] = about_element.text.strip()
        else:
            item['about'] = ""
        
        # Experience
        item['experience'] = self.scrape_experience()

        # Education
        item['education'] = self.scrape_education()

        # Profile Picture
        item['has_profile_picture'] = self.has_profile_picture()

        # Number of Connections
        item['number_connections'] = self.get_number_connections()

        # Number of Recommendations
        item['number_recommendations'] = self.get_number_recommendations()

        # Interests
        item['interests'] = self.get_interests()

        # Latest 3 Posts
        item['latest_posts'] = self.scrape_latest_posts()

        return item

    def scrape_latest_posts(self):
        posts = []
        try:
            # Scroll to ensure posts are loaded
            self.scroll_page()

            # Click on the "Posts" tab under the Activity section
            activity_tab = self.safe_find_element(By.XPATH, "//a[contains(@href, '/recent-activity')]")
            if activity_tab:
                self.driver.execute_script("arguments[0].click();", activity_tab)
                time.sleep(random.uniform(2, 4))  # Wait for the posts tab to load

            # Find post elements
            post_elements = self.safe_find_elements(By.XPATH, "//div[contains(@class, 'occludable-update')]")

            for i in range(min(3, len(post_elements))):  # Get up to 3 posts
                post = {}
                post_date_element = post_elements[i].find_element(By.XPATH, ".//span[contains(@class, 'visually-hidden')]")
                if post_date_element:
                    post['date'] = post_date_element.text.strip()
                posts.append(post)

            if not posts:
                print("No post data found. HTML structure might have changed.")
        except Exception as e:
            print(f"Error scraping latest posts: {e}")
            traceback.print_exc()

        return posts

    def get_interests(self):
        interests = []
        try:
            # Scroll to load all content
            self.scroll_page()

            # Open the Interests section if available
            interests_section = self.safe_find_element(By.XPATH, "//a[@data-control-name='interests']")
            if interests_section:
                self.driver.execute_script("arguments[0].click();", interests_section)
                time.sleep(random.uniform(2, 4))  # Wait for the interests section to load

            # Find interest elements
            interest_elements = self.safe_find_elements(By.XPATH, "//ul[contains(@class, 'pv-interests-list')]//span[contains(@class, 'entity-result__title-text')]")

            if interest_elements:
                interests = [interest.text.strip() for interest in interest_elements]

            if not interests:
                print("No interests data found. HTML structure might have changed.")
        except Exception as e:
            print(f"Error scraping interests: {e}")
            traceback.print_exc()

        return interests

    def scrape_experience(self):
        experience_list = []
        try:
            self.scroll_page()
            xpaths = [
                "//section[.//div[contains(@class, 'pvs-header__title-container')]/h2[contains(text(), 'Experience')]]",
                "//section[.//span[contains(text(), 'Experience')]]",
                "//div[contains(@class, 'experience-section')]"
            ]

            experience_section = None
            for xpath in xpaths:
                experience_section = self.safe_find_element(By.XPATH, xpath)
                if experience_section:
                    break

            if experience_section:
                html = experience_section.get_attribute('outerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                experience_items = soup.find_all('li', class_='artdeco-list__item')
                
                for item in experience_items:
                    experience = {}
                    
                    # Job Title
                    title_elem = item.find('span', class_='mr1 t-bold')
                    if title_elem:
                        experience['job_title'] = title_elem.get_text(strip=True)
                    
                    # Company Name
                    company_elem = item.find('span', class_='t-14 t-normal')
                    if company_elem:
                        experience['company_name'] = company_elem.get_text(strip=True)
                    
                    # Date Range and Duration
                    date_elem = item.find_all('span', class_='t-14 t-normal t-black--light')
                    if len(date_elem) >= 2:
                        experience['date_range'] = date_elem[0].get_text(strip=True)
                        experience['duration'] = date_elem[1].get_text(strip=True)
                    
                    if experience:
                        experience_list.append(experience)
            
            if not experience_list:
                print("No experience data found. HTML structure might have changed.")
        except Exception as e:
            print(f"Error scraping experience: {e}")
            traceback.print_exc()
        
        return experience_list
    
    def scrape_education(self):
        education_list = []
        try:
            self.scroll_page()
            xpaths = [
                "//section[.//div[contains(@class, 'pvs-header__title-container')]/h2[contains(text(), 'Education')]]",
                "//section[.//span[contains(text(), 'Education')]]",
                "//div[contains(@class, 'education-section')]"
            ]

            education_section = None
            for xpath in xpaths:
                education_section = self.safe_find_element(By.XPATH, xpath)
                if education_section:
                    break

            if education_section:
                html = education_section.get_attribute('outerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                education_items = soup.find_all('li', class_='artdeco-list__item')
                
                for item in education_items:
                    education = {}
                    
                    # School Name
                    school_elem = item.find('span', class_='mr1 t-bold')
                    if school_elem:
                        education['university_name'] = school_elem.get_text(strip=True)
                    
                    # Degree and Field of Study
                    degree_elem = item.find('span', class_='t-14 t-normal')
                    if degree_elem:
                        degree_text = degree_elem.get_text(strip=True)
                        degree_parts = degree_text.split(',')
                        education['degree'] = degree_parts[0].strip() if len(degree_parts) > 0 else None
                        education['major'] = degree_parts[1].strip() if len(degree_parts) > 1 else None
                    
                    # Date Range
                    date_elem = item.find('span', class_='t-14 t-normal t-black--light')
                    if date_elem:
                        date_range = date_elem.get_text(strip=True).split(' - ')
                        education['start_date'] = date_range[0] if len(date_range) > 0 else None
                        education['end_date'] = date_range[1] if len(date_range) > 1 else None
                    
                    if education:
                        education_list.append(education)
            
            if not education_list:
                print("No education data found. HTML structure might have changed.")
        except Exception as e:
            print(f"Error scraping education: {e}")
            traceback.print_exc()
        
        return education_list

    def has_profile_picture(self):
        try:
            picture = self.safe_find_element(By.XPATH, '//div[contains(@class, "pv-top-card-profile-picture__container")]//img')
            return True if picture else False
        except Exception:
            return False

    def get_number_connections(self):
        try:
            connections = self.safe_find_element(By.XPATH, '//li[@class="text-body-small t-black--light inline-block"]//span')
            if connections:
                return connections.text.strip().split()[0]
            return None
        except Exception:
            return None

    def get_number_recommendations(self):
        try:
            recommendations = self.safe_find_element(By.XPATH, '//section[contains(@class, "recommendations")]//span[@class="t-bold"]')
            if recommendations:
                return recommendations.text.strip()
            return None
        except Exception:
            return None

    def get_interests(self):
        interests = []
        try:
            interests_section = self.safe_find_element(By.XPATH, '//section[.//span[contains(text(), "Interests")]]')
            if interests_section:
                interest_elements = interests_section.find_elements(By.XPATH, './/span[@class="mn-connection-card__name t-16 t-black t-bold"]')
                interests = [interest.text.strip() for interest in interest_elements]
        except Exception as e:
            print(f"Error scraping interests: {e}")
        return interests

    def scroll_page(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def save_to_json(self, filename='linkedin_profiles.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = LinkedInProfileScraper()
    
    # Replace with your LinkedIn credentials
    username = ""
    password = ""
    
    try:
        scraper.login(username, password)
        time.sleep(random.uniform(2, 4))  # Wait for the page to load after login
        scraper.search_for_ceo()
        scraper.click_people_filter()
        scraper.visit_profiles()
    except KeyboardInterrupt:
        print("Script interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
    finally:
        scraper.close()
