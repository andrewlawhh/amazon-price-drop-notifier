import requests
import bs4 as bs
# import selenium
import sys
import smtplib

# Dictionary mapping amazon URL to current lowest price
# Todo - Replace dictionary with SQL database
#
#        WARES
#  -- URL --- PRICE --
# |        |          |
# |        |          |
# |        |          |
# ---------------------
# Updated every X hours/days/whatever
url_to_price = {}

def get_price(url : 'an amazon url') -> 'double price':
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

    # Handle range vs flat
    if '-' in price:
        # Range case : manipulate string to find low and high ends
        low_end = float(price[1:price.index(' ')])
        high_end = float(price[price.index('- $') + 3:])
        return low_end, high_end
    else:
        # Flat price case : Remove dollar sign and return the number as a float
        price = float(price[1:])
        return price

def update_and_notify():
    '''
    For each URL in dictionary:
        get the price
        if it is different, update the dictionary
            if it is lower than it was before, email the user
    :return: None
    '''
    url_to_price = get_url_dict()

    for url in url_to_price:
        old_price = url_to_price[url]
        new_price = get_price(url)

        if old_price != new_price:
            update_table(url, new_price)
            if new_price < old_price:
                notify(url, new_price)


def get_url_dict():
    '''
    Reads from a database and returns mapping from URL to last saved price
    :return: dictionary {url -> price}
    '''
    pass

def update_table(url : 'amazon url', price : 'double price') -> None :
    '''
    Updates database with new mapping of URL -> price
    :param url: String url
    :param price: float price
    :return: None
    '''
    pass

def notify(url : 'amazon url', price : 'double price') -> None :
    '''
    Email with message 'Item at URL just dropped to PRICE dollars'
    :return: None
    '''
    pass

def main():
    pass

if __name__ == '__main__':
    main()

