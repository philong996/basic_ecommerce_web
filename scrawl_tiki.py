from concurrent.futures import ThreadPoolExecutor
import psycopg2
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


class Product:
    def __init__(self, productid, images, fprice, category, subcategory, category_id, titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink):
        self.productid  = productid
        self.images = images
        self.fprice = fprice
        self.category = category
        self.subcategory = subcategory
        self.category_id = category_id
        self.titles = titles
        self.seller = seller
        self.rprice = rprice
        self.discount = discount
        self.ratings = ratings
        self.num_reviews = num_reviews
        self.tikinow = tikinow
        self.productlink = productlink
    def insert_product(self):
        tablename = 'products'
        query = f"""INSERT INTO {tablename}(productid ,images, fprice, category, subcategory, category_id , titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink)
                    VALUES('{self.productid}', '{self.images}','{self.fprice}', '{self.category}', '{self.subcategory}','{self.category_id}' ,'{self.titles}','{self.seller}','{self.rprice}','{self.discount}','{self.ratings}','{self.num_reviews}','{self.tikinow}','{self.productlink}');"""
        cur.execute(query)
        conn.commit()
    def __repr__(self):
        return f'Category: {self.category}, \n Name: {self.titles}, Price: {self.fprice}'

def load_website(url):
    try:
        response = requests.get(url)
        return BeautifulSoup(response.text, "html.parser")
    except Exception as err:
        print(f'ERROR: {err}')

def scrape_and_insert(cat_link,articles,k):
    #Works for scraping beautiful soup product item from tiki product page
    try:
        #scrape and assign to variables
        images = articles[k].img['src']
        productid = articles[k]['data-id']
        fprice = int(articles[k].find_all("span",{"class":"final-price"})[0].text.strip().split()[0].strip('đ').replace('.',''))
        rprice = [0 if articles[k].find_all("span",{"class":"price-regular"})[0].text == '' else int(articles[k].find_all("span",{"class":"price-regular"})[0].text.strip('đ').replace('.',''))][0]
        discount = [0 if len(articles[k].find_all("span",{"class":"final-price"})[0].text.strip().split()) == 1 else int(articles[k].find_all("span",{"class":"final-price"})[0].text.strip().split()[1].split('%')[0])][0]
        seller = articles[k]['data-brand'].replace('\'','').replace('"','')
        titles = articles[k].a['title'].strip().replace('\'','').replace('"','')
        subcategory = articles[k]['data-category'].strip().split('/')[-1]
        category = articles[k]['data-category'].strip().split('/')[0]
        if articles[k].find_all('p',{"class":'review'}) == [] or articles[k].find_all('p',{"class":'review'})[0].text == 'Chưa có nhận xét':
            num_reviews = 0
        else:
            num_reviews = int(articles[k].find_all('p',{"class":'review'})[0].text.strip('\(\)').split()[0])

        ratings = [int(articles[k].find_all('span',{"class":'rating-content'})[0].find('span')['style'].split(':')[1].split('%')[0]) if articles[k].find_all('span',{"class":'rating-content'}) != [] else 0][0]
        tikinow = [0 if articles[k].find_all('i',{"class":"tikicon icon-tikinow-20"}) == [] else 1][0]
        productlink = articles[k].a['href']
        category_id = cat_link[0]
        return (productid, images, fprice, category, subcategory, category_id, titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink)
        
    except Exception as err:
        print(err, k)

def get_products(cat_link):
    t1 = time.perf_counter()
    count = 0
    soup = load_website(cat_link[1])
    links = soup.find('a',{"class":'next'})
    if links == None:
        articles = soup.find_all('div', {"class":'product-item'})
        for k in range(len(articles)):
            productid, images, fprice, category, subcategory, category_id, titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink = scrape_and_insert(cat_link,articles, k)
            product = Product( productid, images, fprice, category, subcategory, category_id, titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink)

            #print(product)
            count += 1
            product.insert_product()
    else:
        links = soup.find('a',{"class":'next'})
        while links != None:
            articles = soup.find_all('div', {"class":"product-item"})
            soup = load_website(('https://tiki.vn' + links['href']))
            for k in range(len(articles)):
                productid, images, fprice, category, subcategory, category_id, titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink = scrape_and_insert(cat_link,articles, k)
                product = Product( productid, images, fprice, category, subcategory, category_id, titles, seller, rprice, discount, ratings, num_reviews, tikinow, productlink)
                product.insert_product()
                #print(product)
                count += 1
            links = soup.find('a',{"class":'next'})
    t2 = time.perf_counter()
    duration = f'Duration Process: {t2 - t1}'

    print(cat_link[1], count , duration)


query = '''SELECT p.id, p.url FROM categories as p
    LEFT JOIN categories as c ON c.parent_id = p.id
    WHERE c.id IS NULL;
'''

conn = psycopg2.connect(user="philong",
                        password="",
                        database="tiki")
conn.autocommit = True
cur = conn.cursor()

cur.execute(query)
urls = cur.fetchall()


start = time.perf_counter()
with ThreadPoolExecutor() as executor:
    executor.map(get_products, urls)

end = time.perf_counter()
print(f'Time for Process: {end - start}')
