import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

class ESG_Rating_Scraper:
    def __init__(self):
        s = Service('C:/Users/leand/Downloads/chromedriver_win32/chromedriver.exe')
        options = Options()
        options.add_argument('log-level=3')
        options.add_argument('headless=True')
        self.driver = webdriver.Chrome(service=s, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_page(self, url):
        self.driver.get(url)

    def search_company(self, company_name, original_name=None):
        if not original_name:
            original_name = company_name

        legal_suffixes = [' inc', ' co', ' ltd', ' llc', ' corp', ' plc', ' ag', ' gmbh', ' nv', ' sa', ' srl', ' oyj', ' ab', ' as', ' a/s', ' s.a.', 'corporation']
        if '.com' in company_name:
            before_dotcom, after_dotcom = company_name.split('.com', 1)
            before_dotcom = before_dotcom.replace(',', '').replace('.', '').replace("'", '')
            company_name = before_dotcom + '.com' + after_dotcom
        else:
            company_name = company_name.replace(',', '').replace('.', '').replace("'", '')
        company_name_lower = company_name.lower()
        for suffix in legal_suffixes:
            if company_name_lower.endswith(suffix):
                company_name = company_name[:company_name_lower.rfind(suffix)]
                break
        search_input = self.driver.find_element(By.XPATH, '//*[@id="searchInput"]')
        for character in company_name:
            search_input.send_keys(character)
            # time.sleep(random.uniform(0.1, 0.15))
        self.driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(2.5)
        search_results = self.driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-results") and contains(@class, "shadow")]//a')
        max_similarity = 0
        best_match = None
        for result in search_results:
            result_name = result.find_element(By.TAG_NAME, 'span').text
            similarity = self._get_similarity(original_name, result_name)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = result
        if best_match and max_similarity >=0.5:
            self.driver.execute_script("arguments[0].click();", best_match)
        else:
            search_input.clear()
            if len(company_name.split()) > 1 or len(company_name.split('-')) > 1:
                trimmed_company_name = ' '.join(company_name.split()[:-1])
                if '-' in company_name:
                    trimmed_company_name = '-'.join(company_name.split('-')[:-1])
                self.search_company(trimmed_company_name, original_name=company_name)
            # time.sleep(2.5)

    def _get_similarity(self, str1, str2):
        vectorizer = TfidfVectorizer().fit_transform([str1, str2])
        vectors = vectorizer.toarray()
        return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    def extract_esg_rating(self, url):
        try:
            rating_element = self.driver.find_element(By.CLASS_NAME, 'risk-rating-score')
            return rating_element.text.strip()
        except NoSuchElementException:
            return None
        
    def extract_company_name(self):
        try:
            company_element = self.driver.find_element(By.XPATH, '//div[@class="row company-name"]/div/h2')
            return company_element.text.strip()
        except NoSuchElementException:
            return None

    def quit(self):
        self.driver.quit()

if __name__ == '__main__':
    companies_to_scrape = []
    companies_to_scrape.extend(['Alphabet', 'Apple'])
    failed_companies = []
    company_ratings = []
    scraper = ESG_Rating_Scraper()
    for company in companies_to_scrape:
        try:            
            scraper.get_page("https://www.sustainalytics.com/esg-ratings")
            scraper.search_company(company)
            rating = scraper.extract_esg_rating(scraper.driver.current_url)
            company_source = scraper.extract_company_name()
            print(f"The ESG rating for {company} is {rating}, found {company_source}")
            company_ratings.append((company, rating, company_source))
            
        except Exception as e:
            print(f"Failed to get the ESG rating for {company}")
            failed_companies.append(company)

    scraper.quit()
    if failed_companies:
        print(f"Failed to get the ESG rating for the following companies: {', '.join(failed_companies)}")
    
    print(company_ratings)
