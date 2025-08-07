
import json
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence


url = "https://search.earth911.com/?what=Electronics&where=10001&max_distance=100"

google_api_key = 'AIzaSyCikK_F5VuQd-fGEnhheQkpVtSd-msiRbI'


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=google_api_key,
    temperature=0.0,
    max_tokens=5000
)

prompt_template = PromptTemplate.from_template("""
Extract distinct recycling facilities from the raw HTML. Return only a valid JSON array with entries containing:
- business_name: Official facility name
- last_update_date: Last updated date (e.g., "2023-11-04" from <time> tags or text like "Last updated: ..."), use "Unknown" if unavailable
- street_address: Full physical street address
- materials_category: List of categories from ["Electronics", "Batteries", "Paint & Chemicals", "Medical Sharps", "Textiles/Clothing", "Other Important Materials"], inferred from materials accepted
- materials_accepted: List of specific materials (e.g., ["Computers", "Smartphones", "Lithium-ion Batteries"])
Ensure unique facilities by business_name and street_address. Return only a JSON array in square brackets [], with no markdown, comments, or extra text.
Raw HTML (each facility is a <li class="result-item">):
{scraped_html}
""")

chain = prompt_template | llm

def setup_driver():
    cache_path = os.path.expanduser("~/.wdm")
    if os.path.exists(cache_path):
        import shutil
        shutil.rmtree(cache_path)
    
    driver_path = ChromeDriverManager().install()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(service=Service(driver_path), options=chrome_options)

def scrape_earth911():
    driver = setup_driver()
    try:
        driver.get(url)
        time.sleep(5)
        scraped_html = driver.page_source
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(scraped_html)
        soup = BeautifulSoup(scraped_html, 'html.parser')
        results = soup.select('ul.result-list > li.result-item')
        return '\n'.join([str(result) for result in results[:5]])
    finally:
        driver.quit()

def process_with_llm(scraped_html):
    time.sleep(5)
    result = chain.invoke({"scraped_html": scraped_html})
    facilities = json.loads(result.content)
    if not isinstance(facilities, list):
        print("Error: LLM response is not a valid JSON array")

    if "rate limit" in result.content.lower():
        print("Error: Gemini API rate limit exceeded. Wait 60 seconds or until 12:30 PM IST next day.")

    return facilities

def main():
    scraped_html = scrape_earth911()
    facilities = process_with_llm(scraped_html)
    if not facilities:
        print("Error: No facilities extracted")

    with open('recycling_facilities.json', 'w') as f:
        json.dump(facilities, f, indent=2)
    print(json.dumps(facilities, indent=2))

if __name__ == "__main__":
    main()