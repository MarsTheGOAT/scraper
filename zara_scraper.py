from bs4 import BeautifulSoup as bs
import requests
import numpy as np 
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from datetime import date
from urllib.parse import urlparse
from sqlalchemy import create_engine
import io

def extract_source(url):
     agent = {"User-Agent":"Mozilla/5.0"}
     source=requests.get(url, headers=agent).text
     return source


def extract_category_link(url):
    # extract different category links from the main websites
    source = extract_source(url)
    soup = bs(source,'lxml')
    links = soup.findAll('a', {'class':'layout-categories-category__link'})
    urls = []
    for i in links:
        try:
            urls.append(i['href'])
        except:
            pass
    return urls

def category_scrape(url):
    # scrape every product from a single category
    errors = []
    source = extract_source(url)
    soup = bs(source,'lxml')
    links = soup.findAll('a', {'class':'product-link'})
    urls = list(set([i['href'] for i in links]))
    temp = urlparse(url)
    brand = temp.netloc
    path = temp.path[7:-5].split('-')
    low_level = ' '.join(path[1:])
    gender = path[0]
    second_hand = False
    category = []
    print(urls)
    for url in urls:
        product_url = url
        try:
            product = [brand,product_url,low_level,gender,second_hand] + scrape(url)
            category.append(product)
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst) 
            errors.append(url)
            pass
    columns = ['brand_name','product_url','low_level', 'gender','secondhand','display_name','product_material','color', 'size', 'price', 'image_links','description','scrapped_date']
    dataset = pd.DataFrame(category, columns=columns)
    return dataset,errors
 
def scrape(url):
    #scrape the desired information for a single product
    driver = webdriver.Chrome('/Users/marsdai/Downloads/chromedriver')
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-detail-extra-detail")))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "media-image__image")))
    except TimeoutException:
        print('Page timed out after 10 secs.')
        return []
        driver.quit()
    soup = bs(driver.page_source, 'html.parser')
    driver.quit()
    display_name = soup.find('h1').text
    product_material = soup.findAll('span','structured-component-text')
    product_material = [i.text for i in product_material]
    product_material = '\n'.join(product_material)
    color = soup.findAll('span','product-detail-color-selector__color-area')
    color = [col.text for col in color]
    if not color:
        color = soup.find('p','product-detail-selected-color').text
    price = soup.find('span','price-current__amount').text
    image = list(soup.findAll('img',{'class':'media-image__image media__wrapper--media'}))
    image_links = list(set([i['src']for i in image if display_name in i['alt']]))
    size = soup.findAll('div',{'class':'product-detail-size-info__size'})
    size = [i.text for i in size]
    description = soup.find('p').text
    today = date.today()
    scrapped_date = today.strftime("%d/%m/%Y")
    return [display_name,product_material,color,size,price,image_links,description,scrapped_date]

if __name__ == '__main__':
    url = input('Enter the link you wanna to scrap')
    for i in extract_category_link(url):
        df, errors = category_scrape(i)
    #exporting 
        engine = create_engine('postgresql://marsdai:password@localhost:5432/marsdai')
        conn = engine.connect()
        df.to_sql('zara', con=conn, if_exists='append', index=False)
        conn.close()