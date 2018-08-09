# Amazon Price Drop Notifier

This project is a web application that allows users to track Amazon URLs and receive an email when the price drops.
It uses Bootstrap to format the web page and the Flask web framework to run Python in the back end.


### Using the tool
The tool simply takes URL and email parameters through forms in the browser, which get sent to the script via HTTP to
Flask, which is listening on port 5000 by default. Data is then saved in a SQLite database. Every four hours, Python
checks Amazon using requests and beautifulSoup at the saved URLs in the database and emails users who are tracking an
item if the item's price has fallen.

### Functionality
- Tracking items
- Untracking items
- Unsubscribing from the service
- Seeing all items you are tracking
