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

news = get_news_list()
print(f"找到 {len(news)} 篇新聞")

for item in news[:5]:
    print(item)