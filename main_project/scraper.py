import requests 
from bs4 import BeautifulSoup
import re
from time import sleep
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


from data_saver import load_data

# main Scraper to scrape data 
class Scraper:

    def __init__(self):
        self.scraped_data = []

    
    def get_page(self, url, headers, queries, pages):

        for query in queries:

            for page in range(1, pages + 1):

                page_url = f"{url}{query}&page={page}"
                print(f"\n{'-' * 50}\nSCRAPING DATA FOR {query}\n{'-' * 50}\n")

                webpage = requests.get(page_url, headers=headers)

                self.get_product(webpage, headers)

            sleep(random.uniform(1, 3)) 

            load_data(self.scraped_data, query)
            self.scraped_data.clear()



    def get_product(self, webpage, headers):
            try:
                webpage.raise_for_status() 
                soup = BeautifulSoup(webpage.content, "html.parser")
                links = soup.find_all("a", attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
                
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(self.fetch_product_details, link.get('href'), headers) for link in links]
                    for future in futures:
                        future.result()

            except requests.HTTPError as e:
                print("Failed to fetch webpage:", e)



    def fetch_product_details(self, href, headers):
        product_list = f"https://amazon.com{href}" if href.startswith('/') else href       
        product_webpage = requests.get(product_list, headers=headers)
        self.get_product_details(product_webpage)



    def get_product_details(self, product_webpage):
        
        if product_webpage.status_code == 200:

            new_soup = BeautifulSoup(product_webpage.content, "html.parser")

            image_url = new_soup.find('img', attrs={'id': 'landingImage'})
            img_src = image_url.get('src') if image_url else None
            title = new_soup.find('span', attrs={'id': "productTitle"})
            price = new_soup.find('span', attrs={'class': "a-price-whole"})
            reviews = new_soup.find('span', attrs={'id': "acrCustomerReviewText"})
            ratings = new_soup.find('span', attrs={'class': "a-icon-alt"})

            title_text = title.text.strip() if title else "N/A"
            price_text = (("$" + price.text.strip()[:-1]) if (price and price.text.strip().endswith('.')) else (price.text.strip() if price else "N/A"))
            reviews_text = (re.sub('[a-zA-Z]', '', reviews.text.strip()) if reviews else "N/A")
            ratings_text = ratings.text.strip() if ratings else "N/A"


            if "N/A" not in (title_text, price_text, reviews_text, ratings_text):
                scrape_date = datetime.now().strftime("%Y-%m-%d")
                scrape_timestamp = datetime.now().strftime("%I:%M %p")

                product_data = {
                    "Image URL": img_src,
                    "Title": title_text,
                    "Price": price_text,
                    "Total Reviews": reviews_text,
                    "Rating": ratings_text,
                    "Date": scrape_timestamp,
                    "Time": scrape_date,
                }
                print(product_data)

                self.scraped_data.append(product_data)     
            else:
                pass
        else:
            print("Failed to fetch product:", product_webpage)


        