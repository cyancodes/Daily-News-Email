# Libraries

import requests
import bs4
import smtplib
import datetime
import os

def lambda_handler(event, context):
    # Setup Topic and URLs to scrape

    url_dict = {"Top Stories":"https://feeds.bbci.co.uk/news/rss.xml",
                "World":"http://feeds.bbci.co.uk/news/world/rss.xml",
            "UK":"http://feeds.bbci.co.uk/news/uk/rss.xml",
            "Business":"http://feeds.bbci.co.uk/news/business/rss.xml",
            "Politics":"http://feeds.bbci.co.uk/news/politics/rss.xml",
            "Technology":"https://feeds.bbci.co.uk/news/technology/rss.xml"}
    number_of_entries = 5
    email_string = ""

    # Import Emails and Password from environment variables
    sender_email = os.environ['email'] 
    receiver_email = os.environ['email'] # Sends an email to yourself
    password = os.environ['password'] 

    # Function to split the result of the web scrape
    def extrator(item):
        # Creates a list of header, body, long url, short url, time
        _, header, body, _, url, time, _ = item.split('\n')
        return header, body, url, time


    # Scraping The Headings

    for (heading,url) in url_dict.items():
        email_string = email_string+heading+' - '+'\n'
        web_page = requests.get(url)
        soup = bs4.BeautifulSoup(web_page.text,"xml")
        
        for item in soup.select('item')[:number_of_entries]:
            header,body,url,time = extrator(item.text)
            #print(f'\t{header}:\n\t{body}\n\t{url}\n\t{time}\n')
            email_string = email_string+f'\t{header}:\n\t{body}\n\t{url}\n\t{time}\n'+'\n'


    # Emailing The Headings

    # Setting Up Server
    smtp_object = smtplib.SMTP('smtp.gmail.com',587)
    smtp_object.ehlo()
    smtp_object.starttls()

    # Connecting To Account
    smtp_object.login(sender_email,password)

    # Preparing Email
    today = datetime.date.today().strftime("%d/%m/%Y") # Todays date
    subject = f'Daily News - {today}'
    message = email_string
    msg = "Subject: " + subject + '\n' + message

    # Sending Email
    smtp_object.sendmail(sender_email,receiver_email,msg.encode('utf-8'))
    smtp_object.quit()