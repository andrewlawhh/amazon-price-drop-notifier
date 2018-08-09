import requests
import bs4 as bs

import smtplib
from email.message import EmailMessage
from credentials import *

import sqlite3

import datetime
import time

from typing import List

'''
Main function
'''
def update_and_notify() -> None :
    '''
    For each URL in database:
        get the price
        if it is different, update the dictionary
            if it is lower than it was before, email the user
    '''
    while True:
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

        # Run every four hours
        time.sleep(14400)

def get_price_and_item(url : str) -> (float, str) :
    # Scrapes and returns the price of a given amazon url
    # Set up web scraper
    page = requests.get(url)
    html = page.content
    soup = bs.BeautifulSoup(html, 'html.parser')

    # Price tags on amazon are marked with id of #priceblock_ourprice
    price_tag = str(soup.find(id = 'priceblock_ourprice'))

    # Item titles are marked with id of #productTitle
    # Strip product title text of white space and line breaks
    item_name = strip(soup.find(id = 'productTitle').text)

    # Get the relevant information ($ amount) from the price tag
    price = price_tag[price_tag.index('$'):price_tag.index('</')]

    # Handle ranged vs flat
    if '-' in price:
        # Ranged price case : manipulate string to find low and high ends
        low_end = float(price[1:price.index(' ')])
        high_end = float(price[price.index('- $') + 3:])
        return (low_end + high_end) // 2, item_name
    else:
        # Flat price case : Remove dollar sign and return the number as a float
        price = float(price[1:])
        return price, item_name

def get_price(url : str) -> float :
    return get_price_and_item(url)[0]

def get_name(url : str) -> str :
    return get_price_and_item(url)[1]

'''
Database handling
'''
def read_database() -> List[dict] :
    # Reads from a database and returns list of dictionaries
    database_list = []
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM items'):
        database_list.append({'url' : row[0], 'price' : row[1], 'email' : row[2]})
    conn.close()
    return database_list

def update_table(url : str, price : float) -> None :
    # Updates database with the new price where url column = url parameter
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    c.execute('UPDATE items SET price = ? WHERE url = ?', (price, url))
    conn.commit()
    conn.close()
    c.close()

'''
Notify functions
'''
def notify(url : str, name : str, price : float, recipient : str) -> None :
    # Email the recipient notifying him / her of a price drop
    # Format date and time for the email message
    date = datetime.datetime.now().isoformat()[:10]
    time = datetime.datetime.now().isoformat()[11:19]
    content = ' '.join(['Item', name, 'at', url, 'just dropped to $', str(price), 'at', time, 'on', date])
    send_email(content, recipient)

def subscribe_notify(url : str, name : str, recipient : str) -> None :
   # Email the person when he / she tracks a new item
    content = 'You have signed up to receive notifications for ' + name + ' at ' + url
    send_email(content, recipient)

def unsubscribe_notify(recipient : str) -> None :
    # Email the person who is unsubscribing
    content = 'Thank you for using the Amazon Price Drop Notifier Service. You have unsubscribed from the mailing list.'
    send_email(content, recipient)

def send_email(content : str, recipient : str) -> None :
    # Send email to recipient with body as content
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
    msg['To'] = recipient

    # Send email and quit
    server.send_message(msg)
    server.quit()

'''
Utility functions
'''
def strip(str : str) -> str :
    '''
    Returns a copy of the String argument with white space and line breaks removed
    :param str: String
    :return: String
    '''
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
