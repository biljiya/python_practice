import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Target URL (POLITICS only)
url = 'https://english.onlinekhabar.com/category/political'
LIMIT = 10

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.text, features='html.parser')

# Find politics news cards
political_articles = soup.find_all('div', class_='ok-news-post ltr-post')[:LIMIT]

articles_url = []

for each_update in political_articles:
    content = each_update.find('div', class_='ok-post-contents')
    
    if content:
        a_tag = content.find('h2').find('a')
        if a_tag:
            articles_url.append(a_tag['href'])

articles_data = []

for each_article_url in articles_url:
    article_response = requests.get(each_article_url)
    article_soup = BeautifulSoup(article_response.text, features='html.parser')

    title = article_soup.find('div', class_='ok-post-header').find('h1').get_text(strip=True)

    posted_date = article_soup.find('span', class_='ok-post-date').get_text(strip=True)

    content_paragraphs = article_soup.find('div', class_='post-content-wrap').find_all('p')
    content = '\n'.join(p.get_text(strip=True) for p in content_paragraphs)

    articles_data.append({
        'title': title,
        'posted_date': posted_date,
        'content': content,
        'url': each_article_url,
        'scraped_at': datetime.now().isoformat()
    })


print(articles_data)

with open('political_articles.json', 'w') as f:
    json.dump(articles_data, f, indent=4)