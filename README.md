# scraper
This scraper is set up for scraper everything loaded from 'https://www.zara.com/us/' it will first extract all the available category links that the 
main page has then goes to each of the category and treverse through each product from that category. 

When prompt Enter the link you wanna to scrap type https://www.zara.com/us/ and it will start scraping the needed data from zara.com

this will only extract limited products because we need to scroll down the web page to unlock more items, in the future if we want to scrape the 
whole website we would need implement the scrolling step.

as for update the database automatically overtime We can use df_to_sql(if_exist = 'replace') to keep the newest product information
