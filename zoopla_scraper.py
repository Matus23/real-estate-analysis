import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from db import make_db_connection
import re 

class Flat:
    def __init__(self, listing_id, price, address, zip_code, num_bedrooms, num_bathrooms, num_liv_rooms, 
                 description, price_description, listing_link,  listed_on='', listed_by='', sq_ft=0):
        self.listing_id = listing_id
        self.price = price
        self.address = address
        self.zip_code = zip_code
        self.num_bedrooms = num_bedrooms
        self.num_bathrooms = num_bathrooms
        self.num_liv_rooms = num_liv_rooms
        self.description = description
        self.price_description = price_description
        self.listing_link = listing_link
        self.listed_on = listed_on
        self.listed_by = listed_by
        self.sq_ft = sq_ft

    def to_list(self):
        return [self.listing_id, self.price, self.address, self.zip_code, 
            self.num_bedrooms, self.num_bathrooms, self.num_liv_rooms,
            self.description, self.price_description, self.listing_link,
            self.listed_on, self.listed_by, self.sq_ft]

    def to_tuple(self):
        return (self.listing_id, self.price, self.address, self.zip_code, 
            self.num_bedrooms, self.num_bathrooms, self.num_liv_rooms,
            self.description, self.price_description, self.listing_link,
            self.listed_on, self.listed_by, self.sq_ft)


def parse_flat_listings(listings, flats, category):
    for listing in listings:
        price_with_description = listing.find(attrs={'data-testid': 'listing-price'})

        if (len(price_with_description) != 2):
            continue
        
        if category == 'sale':
            price_description = price_with_description.contents[0].text
            price = price_with_description.contents[1].text
            price = process_sale_price(price)
        elif category == 'rental':
            price_description = ''
            price = process_rental_price(price_with_description)

        listing_id = process_id(listing.parent['id'])
        description = listing.find(attrs={'data-testid': 'listing-title'}).text

        address = listing.find(attrs={'data-testid': 'listing-description'}).text
        zip_code = get_zip_code(address)

        listed_on = listing.find(attrs={'data-testid':'date-published'})
        listed_on = process_date(listed_on)

        listing_link = listing.find(attrs={'data-testid': 'listing-details-link'})['href']

        num_bedrooms = 0
        num_bathrooms = 0
        num_living_rooms = 0
        if listing.find(attrs={'data-testid': 'bed'}) is not None:
            num_bedrooms = listing.find(attrs={'data-testid': 'bed'}).parent.parent.contents[1].text
        if listing.find(attrs={'data-testid': 'bath'}) is not None:
            num_bathrooms = listing.find(attrs={'data-testid': 'bath'}).parent.parent.contents[1].text
        if listing.find(attrs={'data-testid': 'chair'}) is not None:
            num_living_rooms = listing.find(attrs={'data-testid': 'chair'}).parent.parent.contents[1].text

        flat = Flat(listing_id, price, address, zip_code, num_bedrooms, 
                    num_bathrooms, num_living_rooms, description, 
                    price_description, listing_link, listed_on=listed_on)
        flats.append(flat)
    
    return flats


def get_listings_from_db(mydb, category):
    cursor = mydb.cursor()
    if category == 'sale':
        cursor.execute("SELECT listing_id FROM ZooplaSales")
    elif category == 'rental':
        cursor.execute("SELECT listing_id FROM ZooplaRentals")
    db_listing_ids = cursor.fetchall()

    return db_listing_ids


def filter_listings(new_flats, mydb, category):
    old_listing_ids = get_listings_from_db(mydb, category)
    old_listing_ids = [listing_id[0] for listing_id in old_listing_ids]
    new_flats = [flat for flat in new_flats if int(flat.listing_id) not in old_listing_ids]
    return new_flats


def get_sale_listings_from_url(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    listings = soup.find_all(attrs={'data-testid': 'search-result'})    
    return listings


def preprocess_price_string(price):
    """
    Transforms price from string format into float
    Args:
        price: String
        example: '$85,000'
    Returns:
        price: Float
        example: 85000.0
    """
    split_price = price.strip()[1:].split(',')
    return float(split_price[0] + split_price[1])

def process_sale_price(price):
    return float(price.strip()[1:].split(',')[0] + price.strip()[1:].split(',')[1])

def process_rental_price(price_with_description):
    price = price_with_description.p.text.split(' ')[0][1:]
    if ',' in price:
        price = price.split(',')[0] + price.split(',')[1]
    
    return float(price)

def get_zip_code(full_address):
    res = re.search('G\d(.*)$', full_address)

    # regular expression failed, split the string
    if res is None:
        split_address = full_address.split(',')

        if len(split_address) < 3:
            # zip code present but at a sooner index
            return split_address[1].strip().split(' ')[1]

        zip_code_with_city = split_address[2].strip().split(' ')

        if len(zip_code_with_city) < 2:
            # missing zipcode
            return ''

        return split_address[2].strip().split(' ')[1]

    return res.group()

def insert_flat_listings_into_db(flats, mydb, category):
    cursor = mydb.cursor()
    if category == 'rental':
        sql_query = "INSERT INTO ZooplaRentals VALUES (%s, %s, %s, %s, %s, %s, \
                                                    %s, %s, %s, %s, %s, %s, %s)"
    elif category == 'sale':
        sql_query = "INSERT INTO ZooplaSales VALUES (%s, %s, %s, %s, %s, %s, \
                                                    %s, %s, %s, %s, %s, %s, %s)"
    flats_records = [flat.to_tuple() for flat in flats]
    cursor.executemany(sql_query, flats_records)
    mydb.commit()

def process_date(date):
    date_list = date.text.split(' ')[2:]
    date = ' '.join(map(str, date_list))
    return date

def process_id(listing_id):
    return listing_id[8:]

def get_url(category, page):
    if category == 'sale':
        return f'https://www.zoopla.co.uk/for-sale/property/glasgow/?beds_min=1&page_size=25&q=Glasgow&radius=0&results_sort=newest_listings&search_source=refine&pn={page}'
    elif category == 'rental':
        return f'https://www.zoopla.co.uk/to-rent/property/glasgow/?beds_min=1&price_frequency=per_month&q=Glasgow&results_sort=newest_listings&search_source=to-rent&pn={page}'

def get_num_pages():
    num_pages = input("Enter number of pages to scrape: ")
    return int(num_pages)

def get_category():
    category = input("Enter category ('sale' or 'rental'): ")
    return category

def main():
    flats = []
    num_pages=get_num_pages()
    category = get_category()
    mydb = make_db_connection()

    for page_num in range(1, num_pages+1):
        URL = get_url(category, page_num)
        listings = get_sale_listings_from_url(URL)
        flats = parse_flat_listings(listings, flats, category)    
        print(f'Page {page_num} processed')

    new_flats = filter_listings(flats, mydb, category)

    print(f'Length of flats: {len(flats)}')
    print(f'Length of new flats: {len(new_flats)}')   

    insert_flat_listings_into_db(new_flats, mydb, category)

if __name__ == "__main__":
    main()