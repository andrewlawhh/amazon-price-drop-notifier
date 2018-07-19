import requests
import bs4 as bs
# import selenium

import smtplib
import sqlite3
import datetime

# Database mapping amazon URL to current lowest price
#
#         TRACKED ITEMS
#
# --- URL --- PRICE -- ---EMAIL---
# |        |          |          |
# |        |          |          |
# |        |          |          |
# ---------------------------------
# Updated every X hours/days/whatever

def update_and_notify():
    '''
    For each URL in database:
        get the price
        if it is different, update the dictionary
            if it is lower than it was before, email the user
    :return: None
    '''
    url_price_email_list = read_database()

    for dict in url_price_email_list:
        url = dict['url']
        old_price = dict['price']
        email = dict['email']

        new_price = get_price(url)

        if old_price != new_price:
            update_table(url, new_price)
            if new_price < old_price:
                notify(url, new_price, email)


def get_price(url : 'String url') -> 'double price':
    '''
    Scrapes and returns the price of a given amazon url
    :param url: String
    :return: Float
    '''
    # Set up web scraper
    page = requests.get(url)
    html = page.content
    soup = bs.BeautifulSoup(html, 'html.parser')

    # Price tags on amazon are marked with id of #priceblock_ourprice
    price_tag = str(soup.find(id = 'priceblock_ourprice'))

    # Get the relevant information ($ amount) from the price tag
    price = price_tag[price_tag.index('$'):price_tag.index('</')]

    # Handle ranged vs flat
    if '-' in price:
        # Ranged price case : manipulate string to find low and high ends
        low_end = float(price[1:price.index(' ')])
        high_end = float(price[price.index('- $') + 3:])
        return low_end, high_end
    else:
        # Flat price case : Remove dollar sign and return the number as a float
        price = float(price[1:])
        return price

def read_database():
    '''
    Reads from a database and returns list of dictionaries]
    :return: list of dictionaries[ {url : exampleURL, price : examplePrice, email : exampleEmail} ]
    '''
    pass

def update_table(url : 'amazon url', price : 'double price') -> None :
    '''
    Updates database with the new price where url column = url parameter
    :param url: String url
    :param price: float price
    :return: None
    '''
    pass

def notify(url : 'String url', price : 'double price', email : 'String email') -> None :
    '''
    Email EMAIL with message 'Item at URL just dropped to PRICE dollars at XX:XX time on XX-XX-XXXX day'
    :return: None
    '''
    server = smtplib.SMTP('smtp.gmail.com', 587)

def track_url(url : 'String url', email : 'String email'):
    '''
    Adds a new row to the database, or if user is already tracking, show error message
    :param url: String url
    :return: None
    '''
    pass

def unsubscribe(email : 'String email'):
    '''
    Drops all rows where email column = email parameter
    :param email: String email
    :return: None
    '''

def main():
    update_and_notify()

if __name__ == '__main__':
    main()
