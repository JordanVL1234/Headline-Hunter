import openai
import os
import json
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def load_data():
    try:
        with open('data.json') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data

def scrape_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headline = soup.find('h1', class_='headline__text').get_text().strip()
    author_name = soup.find('span', class_='byline__name')
    author_name = author_name.get_text().strip() if author_name else None
    content = '\n'.join([p.get_text().strip() for p in soup.find_all('p', class_='paragraph inline-placeholder')])
    summary = summarize(content)
    article_data = {'url': url, 'headline': headline, 'author': author_name, 'content': content, 'summary': summary}
    return article_data

def summarize(text):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=f'Please summarize the following text:\n\n{text}',
        temperature=0.7,
        max_tokens=200
    )
    summary = response.choices[0].text.strip()
    return summary

def main():
    url = 'https://www.cnn.com/business/tech'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    valid_links = [link.get('href') for link in soup.find_all('a') if link.get('href', '').startswith('/') and 'tech' in link.get('href', '') and '/videos/' not in link.get('href', '')]
    if valid_links:
        data = load_data()
        id_num = data[-1]['id_num'] + 1 if data else 1
        random_link = random.choice(valid_links)
        article_data = scrape_article(f'https://www.cnn.com{random_link}')
        article_data['id_num'] = id_num
        data.append(article_data)
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == '__main__':
    main()