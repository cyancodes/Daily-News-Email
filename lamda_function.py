# Libraries

import requests
import bs4
import smtplib
import datetime
import os

def lambda_handler(event, context):
    # Set number of entries to include of each topic
    number_of_entries = 5

    # Import Emails and Password from environment variables
    sender_email = os.environ['email'] 
    receiver_email = os.environ['email'] # Sends an email to yourself
    password = os.environ['password'] 

    # Function to split the result of the web scrape
    def extractor(item):
        # Creates a list of header, body, long url, short url, time
        cleaned_list = [entry for entry in item.split('\n') if entry != '']
        header, body, url, time = cleaned_list[0], cleaned_list[1], cleaned_list[3], cleaned_list[4]
        return header, body, url, time


    # Function for Scraping The Headings

    def scraper(heading,url):
        current_list = [heading+' -\n\n'] # The first entry of the list is the heading with a space
        web_page = requests.get(url) # grabs web page
        soup = bs4.BeautifulSoup(web_page.text,"xml") # creates the soup
        
        for item in soup.select('item'): # runs this code for each item found
            # This try and except test makes the code more reliable, in case there are any news articles formatted in a way that the code is not expecting
            try: 
                header,body,url,time = extractor(item.text)
                current_list.append(f'{header}:\n{body}\n{url}\n{time}\n'+'\n')
            except:
                continue    
        return current_list

    # Scraping and creating a list for each topic
    
    top_stories = scraper("Top Stories","https://feeds.bbci.co.uk/news/rss.xml")
    world = scraper("World","http://feeds.bbci.co.uk/news/world/rss.xml")
    uk = scraper("UK","http://feeds.bbci.co.uk/news/uk/rss.xml")
    business = scraper("Business","http://feeds.bbci.co.uk/news/business/rss.xml")
    politics = scraper("Politics","http://feeds.bbci.co.uk/news/politics/rss.xml")
    technology = scraper("Technology","https://feeds.bbci.co.uk/news/technology/rss.xml")
    master_list = [top_stories,world,uk,business,politics,technology]

    # Creates a unique list of news stories to include in the email

    email_list = []
    for category in master_list:
        index = 0
        for entry in category:
            if index < number_of_entries + 1: # The index hasn't yet reached the number of entries + 1 for the heading
                found = any(entry[:10] == news_item[:10] for news_item in email_list) # Searches the current entry to see if it is found in the current email_list
                if not found:
                    email_list.append(entry)
                    index += 1
            else:
                break

    email_string = ''.join(email_list) # converts the email list into a single string ready to email

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