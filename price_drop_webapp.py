from flask import Flask, render_template, request
import sqlite3
from notifier import *
import os
import re
from typing import List

app = Flask(__name__, template_folder= os.path.join(os.getcwd(), 'templates/'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track_url', methods = ['POST', 'GET'])
def handle_track_url_form():
    error = None
    if request.method == 'POST':
        url = request.form['url']
        email = request.form['email']
        if valid_url(url) and valid_email(email):
            print('Form handling successful')
            track_url(url, email)
        else:
            error = 'Invalid URL or EMail'
    return render_template('index.html', error = error)

def valid_url(url : str) -> bool:
    print('Validating url ...')
    return 'amazon' in url

def valid_email(email : str) -> bool:
    print('Validating email ...')
    # @source : https://www.scottbrady91.com/Email-Verification/Python-Email-Verification-Script
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
    if match == None:
        print('Invalid email syntax')
        return False
    return True

def track_url(url : str, email : str) -> None:
    '''
    Adds a new row to the database, or if user is already tracking, show error message
    :param url: String
    :return: None
    '''
    print('Track URL form was submitted')
    subscribe_notify(url, get_name(url), email)
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    price = get_price(url)
    c.execute('INSERT INTO items (url, price, email) VALUES (?, ? ,?)', (url, price, email))
    conn.commit()
    conn.close()

@app.route('/unsubscribe', methods = ['POST', 'GET'])
def handle_unsubscribe_form():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        if valid_email(email):
            unsubscribe(email)
            unsubscribe_notify(email)
        else:
            error = 'Invalid email'
    return render_template('index.html', error = error)

def unsubscribe(email : str) -> None:
    '''
    Drops all rows where email column = email parameter
    :param email: String
    :return: None
    '''
    print('Unsubscribe form was submitted')
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE email = ?', (email, ))
    conn.commit()
    conn.close()

def get_urls(email : str) -> List[str]:
    '''
    Returns a list of URLs this email account is following
    :param email: String
    :return: String[]
    '''
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    c.execute('SELECT url FROM items WHERE email = ?', (email,))
    conn.close()
    return c.fetchall()

if __name__ == '__main__':
    app.run(debug = True)
