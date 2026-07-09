import requests
from bs4 import BeautifulSoup

def get_news_list():

    url = "https://www.offshore-energy.biz/marineenergy/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html5lib")
    news_list = []
    titles = soup.select("h3")

    for news in titles:
        a = news.find("a")
        if a:
            news_list.append({
                "title": a.get_text(strip=True),
                "url": a["href"]
            })
    return news_list

def get_article_page(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html5lib")

    return soup

def get_publish_date(article):
    
    date = article.find("div", class_="article-meta__info")
    text = " ".join(date.get_text().split())
    parts = text.split("by")

    publish_date = parts[0].rstrip(", ")
    author = parts[1].strip()
    return publish_date, author

def get_content(article):
    content = article.find("div", class_="wp-content")
    content = clean_content(content)

    paragraphs = content.find_all("p")

    texts = []

    for p in paragraphs:
        text = p.get_text(strip=True)

        if text:
            texts.append(text)

    return "\n\n".join(texts)

def clean_content(content):
    for script in content.find_all("script"):
        script.decompose()
    
    for sectcion in content.find_all("section"):
        sectcion.decompose()
    
    return content
news = get_news_list()
first_url = news[0]["url"]


## first article
article = get_article_page(first_url)

content = article.find("div", class_="wp-content")
content = get_content(article)

print(content)
