import os

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_article(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    article = BeautifulSoup(response.text, "html5lib")
    
    meta = article.find("div", class_="article-meta__info")
    meta_text = " ".join(meta.get_text().split())
    parts = meta_text.split("by")
 
    news = {}
    news["title"] = article.title.get_text(strip=True).replace(" - Offshore Energy","")
    news["url"] = url
    news["publish_date"] = parts[0].strip().rstrip(",")
    news["author"] = parts[1].strip()
    news["content"] = get_content(article)
    news["highlight_en"] = ""
    news["highlight_zh"] = ""
    news["note"] = ""
    news["hashtags"] = []
    
    return news

def get_news_list():

    url = "https://www.offshore-energy.biz/marineenergy/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html5lib")
    news_list = []
    titles = soup.select("h3")

    for title in titles:
        a = title.find("a")
        if a:
            news = {}
            news["title"] = a.get_text(strip = True)
            news["url"] = a["href"]
            news_list.append(news)
            
    return news_list

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

def generate_ai_analysis(content):

    while True:
        try:
                    
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=f"""
                You are a marine energy analyst.

                Read the following marine energy news and return the result in EXACTLY the following format.

                [HIGHLIGHTS_EN]
                - Bullet 1
                - Bullet 2
                - Bullet 3
                - Bullet 4
                - Bullet 5

                [HIGHLIGHTS_ZH]
                - Bullet 1
                - Bullet 2
                - Bullet 3
                - Bullet 4
                - Bullet 5

                [NOTE]
                - Observation 1
                - Observation 2
                - Observation 3

                [HASHTAGS]
                #Tag1
                #Tag2
                #Tag3
                #Tag4
                #Tag5

                Requirements:

                For HIGHLIGHTS_EN:
                - Keep 3–5 bullet points.
                - Use concise engineering language.
                - Keep only factual information from the article.

                For HIGHLIGHTS_ZH:
                - Use Traditional Chinese.
                - Faithfully reflect the English highlights.
                - Use standard engineering terminology commonly used in Taiwan.
                - Do not add information not mentioned in the article.

                For NOTE:
                Provide 2–4 objective observations that may be relevant to Taiwan's marine energy development.

                Requirements:
                - Base every observation ONLY on information explicitly stated in the article.
                - Do NOT recommend what Taiwan should do.
                - Do NOT assume Taiwan is involved in the project.
                - Do NOT speculate about future cooperation or policy.
                - Do not infer implications beyond the facts reported in the article.
                - Highlight why the reported technology, project, testing approach, deployment location, or development stage could be relevant for Taiwan.
                - Use Traditional Chinese.
                - Keep each observation to one sentence.
                - If there is no obvious relevance to Taiwan, return exactly:
                無

                For HASHTAGS:
                - Return 5–8 hashtags.
                - Use English only.
                - One hashtag per line.
                - No spaces.
                - Use PascalCase (example: #WaveEnergy).
                - Include technology, company, country/region, project, TRL, or other important concepts when appropriate.

                Return ONLY these four sections.
                Do not output any additional text.

                Article:
                {content}
                """
            )
            time.sleep(5)
            
            return response.text.strip()    
        except Exception as e:
            print("AI API error")
            print(e)
            print("retry after 40 sec.")
            time.sleep(40)

def parse_ai_response(text):
    parts = text.split("[HIGHLIGHTS_ZH]")

    highlights_en = parts[0].replace("[HIGHLIGHTS_EN]", "").strip()
    parts = parts[1].split("[NOTE]")
    highlights_zh = parts[0].strip()
    parts = parts[1].split("[HASHTAGS]")
    note = parts[0].strip()
    hashtags = parse_hashtags(parts[1])
    
    return highlights_en, highlights_zh, note, hashtags

def parse_hashtags(text):
    hashtags = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            hashtags.append(line)
    hashtags = list(dict.fromkeys(hashtags))
            
    return hashtags
    
news_list = get_news_list()
all_news = []
for item in news_list:
    news = get_article(item["url"])
    result = generate_ai_analysis(news["content"])
    (
        news["highlight_en"],
        news["highlight_zh"],
        news["note"],
        news["hashtags"]
    ) = parse_ai_response(result)
    
    all_news.append(news)


wb = Workbook()
ws = wb.active
ws.title = "Marine News"

headers = [
    "title",
    "publish_date",
    "highlight_en",
    "highlight_zh",
    "note",
    "hashtags",
    "url",
    "author"
]
ws.append(headers)

for news in all_news:
    ws.append([
        news["title"],
        news["publish_date"],
        news["highlight_en"],
        news["highlight_zh"],
        news["note"],
        ", ".join(news["hashtags"]),
        news["url"],
        news["author"]
    ])

wb.save("MarineNews.xlsx")
print(f"完成，共輸出 {len(all_news)} 篇文章")