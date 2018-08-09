from flask import Flask, render_template, request
import sqlite3
import notifier
import os
import re
from typing import List

app = Flask(__name__, template_folder= os.path.join(os.getcwd(), 'templates/'))

@app.route('/')
def index():
    return render_template('index.html')

'''
Track Amazon Item Functions
'''
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
            error = 'Invalid URL or email'
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
    notifier.subscribe_notify(url, notifier.get_name(url), email)
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    price = notifier.get_price(url)
    c.execute('INSERT INTO items (url, price, email) VALUES (?, ? ,?)', (url, price, email))
    conn.commit()
    conn.close()


'''
Unsubscribe from mailing list functions
'''
@app.route('/unsubscribe', methods = ['POST', 'GET'])
def handle_unsubscribe_form():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        if valid_email(email):
            unsubscribe(email)
            notifier.unsubscribe_notify(email)
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


'''
Get all URLs user is tracking functions
'''
@app.route('/user_items', methods = ['POST', 'GET'])
def handle_get_urls():
    pass

def get_urls(email : str) -> List[tuple]:
    '''
    Returns a list of URLs this email account is following
    :param email: String
    :return: Tuple[]
    The returned list contains tuples formatted like this -> (URL, Price)
    '''
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    c.execute('SELECT url, price FROM items WHERE email = ?', (email,))
    conn.close()
    return c.fetchall()

'''
Stop tracking an item functions
'''
@app.route('/untrack', methods = ['POST', 'GET'])
def handle_untrack_form():
    error = None
    if request.method == 'POST':
        url = request.form['url']
        email = request.form['email']
        if valid_url(url) and valid_email(email):
            print('Form handling successful')
            untrack(url, email)
        else:
            error = 'Invalid URL or email'
    return render_template('index.html', error = error)

def untrack(url : str, email : str) -> None:
    '''
    Untracks a URL for specified email
    :param email: str
    :param url: str
    :return: None
    '''
    conn = sqlite3.connect('tracked_items.db')
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE email = ? and url = ?', (email, url))
    conn.close()

if __name__ == '__main__':
    app.run(debug = True)
