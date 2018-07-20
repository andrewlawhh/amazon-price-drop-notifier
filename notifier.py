import requests
import bs4 as bs
# import selenium

import smtplib
from email.message import EmailMessage
from credentials import *

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

'''
Scalability
    This approach introduces scalability issues because we are repetitively writing the same URL + price combination
    to the database for each user that wants to track it.
    
    For scalability and memory efficiency, make URL unique and in the email column have a list of emails the program 
    should notify when the price of the item updates.
'''

'''
Main function
'''
def update_and_notify() -> None:
    '''
    For each URL in database:
        get the price
        if it is different, update the dictionary
            if it is lower than it was before, email the user
    :return: None
    '''
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()

    url_price_email_list = read_database()

    for dict in url_price_email_list:
        url = dict['url']
        old_price = dict['price']
        email = dict['email']

        price_and_item = get_price_and_item(url)
        new_price = price_and_item[0]
        item_name = price_and_item[1]

        if old_price != new_price:
            update_table(url, new_price)
            if new_price < old_price:
                notify(url, item_name, new_price, email)

    conn.close()
    c.close()

def get_price_and_item(url : 'String url') -> 'double price, String item_name':
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
    price_tag = soup.find(id = 'priceblock_ourprice').text

    # Item titles are marked with id of #productTitle
    # Strip product title text of white space and line breaks
    item_name = strip(soup.find(id = 'productTitle').text)

    # Get the relevant information ($ amount) from the price tag
    price = price_tag[price_tag.index('$'):price_tag.index('</')]

    # Handle ranged vs flat

    # TODO - Change implementation so we can ALWAYS get flat
    if '-' in price:
        # Ranged price case : manipulate string to find low and high ends
        low_end = float(price[1:price.index(' ')])
        high_end = float(price[price.index('- $') + 3:])
        return item_name, low_end, high_end
    else:
        # Flat price case : Remove dollar sign and return the number as a float
        price = float(price[1:])
        return price, item_name

'''
Database handling
'''

def read_database() -> '{}[]' :
    '''
    Reads from a database and returns list of dictionaries]
    :return: list of dictionaries[ {url : exampleURL, price : examplePrice, email : exampleEmail} ]
    '''
    nonlocal c, conn
    conn.commit()
    pass

def update_table(url : 'amazon url', price : 'double price') -> None :
    '''
    Updates database with the new price where url column = url parameter
    :param url: String url
    :param price: float price
    :return: None
    '''
    nonlocal c, conn
    conn.commit()
    pass

def track_url(url : 'String url', email : 'String email') -> None:
    '''
    Adds a new row to the database, or if user is already tracking, show error message
    :param url: String url
    :return: None
    '''
    nonlocal c, conn
    conn.commit()
    pass

def unsubscribe(email : 'String email') -> None:
    '''
    Drops all rows where email column = email parameter
    :param email: String email
    :return: None
    '''
    nonlocal c, conn
    conn.commit()
    pass

'''
Notify functions
'''
def notify(url : 'String url', name : 'String name', price : 'double price', email : 'String email') -> None :
    '''
    Email EMAIL with message 'Item at URL just dropped to PRICE dollars at XX:XX time on XX-XX-XXXX day'
    :return: None
    '''
    # Format date and time for the email message
    date = datetime.datetime.now().isoformat()[:10]
    time = datetime.datetime.now().isoformat()[11:19]
    content = 'Item '  + name + ' at ' + url + ' just dropped to $' + str(price) + 'at ' + time + ' on ' + date

    # Initialize SMTP and login to Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(email_username, email_password)

    # Create email message
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = 'Amazon Price Drop'
    msg['From'] = 'AmazonPriceDropNotifier@gmail.com'
    msg['To'] = email

    # Send email and quit
    server.send_message(msg)
    server.quit()

# Returns version of string with spaces and line breaks removed
def strip(str : 'String str') -> 'String stripped_string':
    stripped = str
    for char in stripped:
        if char in '\n ':
            stripped = stripped.replace(char, '')
    return stripped

'''
Main
'''
def main():
    update_and_notify()

if __name__ == '__main__':
    main()
