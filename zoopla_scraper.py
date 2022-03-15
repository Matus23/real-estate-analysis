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


def parse_flat_sale_listings(listings, flats):

    for listing in listings:
        price_with_description = listing.find(attrs={'data-testid': 'listing-price'})

        if (len(price_with_description) != 2):
            continue
        
        price_description = price_with_description.contents[0].text
        price = price_with_description.contents[1].text
        price = process_price(price)

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


def get_sale_listings_from_url(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    # dependent on the page layout
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


def process_price(price):
    return float(price.strip()[1:].split(',')[0] + price.strip()[1:].split(',')[1])


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
    
    


def insert_flat_sale_listings_into_db(flats, mydb):
    cursor = mydb.cursor()
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



def main():
    flats = []
    num_pages=31
    for i in range(1, num_pages+1):
        URL = f'https://www.zoopla.co.uk/for-sale/property/glasgow/?beds_min=1&page_size=25&q=Glasgow&radius=5&results_sort=newest_listings&search_source=refine&pn={i}'
        listings = get_sale_listings_from_url(URL)
        flats = parse_flat_sale_listings(listings, flats)
        print(f'Page {i} processed')

    print(f'Length of flats: {len(flats)}')
    mydb = make_db_connection()
    insert_flat_sale_listings_into_db(flats, mydb)

main()