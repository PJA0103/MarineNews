import os

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from datetime import datetime

import time
from dotenv import load_dotenv
from google import genai

from database import create_database, insert_news, count_news, news_exists, find_duplicate_urls, remove_duplicate_news, get_news_by_country

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
    news["publish_date"] = format_date(parts[0].strip().rstrip(","))
    news["author"] = parts[1].strip()
    news["content"] = get_content(article)
    news["highlight_en"] = ""
    news["highlight_zh"] = ""
    news["note"] = ""
    news["tags"] = {
    "Country": [],
    "Technology": [],
    "Topic": [],
    "Company": [],
    "Organization": [],
    "Project": [],
    "Site": [],
    "SeaArea": [],
    "Custom": []
    }
    
    return news

def format_date(date_text):
    date_text = date_text.replace(", posted", "")
    date_text = date_text.strip().rstrip(",")

    dt = datetime.strptime(date_text, "%B %d, %Y")
    return dt.strftime("%Y-%m-%d")

def get_news_list(page=1):

    if page == 1:
        url = "https://www.offshore-energy.biz/markets/marine-energy/"
    else:
        url = f"https://www.offshore-energy.biz/markets/marine-energy/page/{page}/"
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

                Analyze the following marine energy news and return the result in EXACTLY the following format.

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

                [TAGS]
                Country:
                - Tag
                Technology:
                - Tag
                Topic:
                - Tag
                Company:
                - Tag
                Organization:
                - Tag
                Project:
                - Tag
                Site:
                - Tag
                SeaArea:
                - Tag
                Custom:
                - Tag

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

                For TAGS:

                Extract structured tags using the following categories.

                Country:
                - Extract ONLY countries where at least one of the following is true:

                1. The project is physically located there.
                2. The company is headquartered there.
                3. A government, university, or organization from that country is a direct participant.
                4. The article explicitly states that work is being carried out there.

                - Do NOT include countries mentioned only:
                - as market opportunities,
                - as future deployment locations,
                - as background information,
                - as examples,
                - in global comparisons,
                - in report statistics,
                - in maps or figures.

                - Use standardized English country names.
                - Never infer countries from seas, oceans, currents, organizations, or company names.
                Examples:
                Dutch company → Netherlands
                British company → United Kingdom
                US company → United States of America
                
                Kuroshio Current → NOT Japan
                North Sea → NOT United Kingdom
                Global market → None

                Technology:
                - Select ONLY from:
                Wave Energy
                Tidal Steam
                Tidal Range
                Ocean Current
                OTEC
                Salinity Gradient

                Topic:
                - Select ONLY from:
                Policy
                Regulation
                Funding
                Investment
                Testing
                Prototype
                Operation
                Commercialization
                Research
                Collaboration
                Manufacturing
                Grid Connection
                Environmental Assessment
                Permitting

                Company:
                - Extract official full company names.

                Organization:
                - Extract official full organization names.

                Project:
                - Extract the official full project or product name.
                - Do not shorten names.
                - Extract only the official name of an engineering project, demonstration project, commercial project, product, prototype, or funded programme.
                - Do NOT output report titles, article titles, conference names, slogans, or publication titles.
                - If none exists, return:
                None

                Site:
                - Extract official testing site or demonstration site names.

                SeaArea:
                - Extract official names of oceans, seas, currents or marine regions.

                Custom:
                - Extract important technical terms that do not belong to the above categories.
                - Examples:
                TRL6
                OpenFAST
                Power Take Off
                Dynamic Cable
                EMEC

                General rules:
                - Use English only.
                - One tag per line.
                - Do not invent information.
                - If a category has no tags, leave it empty.


                Return ONLY these four sections.
                Do not output any additional text.

                Article:
                {content}
                """
            )
            time.sleep(5)
            
            return response.text.strip()    
        except Exception as e:
            time.sleep(40)

def parse_ai_response(text):
    parts = text.split("[HIGHLIGHTS_ZH]")

    highlights_en = parts[0].replace("[HIGHLIGHTS_EN]", "").strip()
    parts = parts[1].split("[NOTE]")
    highlights_zh = parts[0].strip()
    parts = parts[1].split("[TAGS]")
    note = parts[0].strip()
    tags = parse_tag_categories(parts[1])
    
    return highlights_en, highlights_zh, note, tags

def parse_tag_categories(text):

    categories = {
        "Country": [],
        "Technology": [],
        "Topic": [],
        "Company": [],
        "Organization": [],
        "Project": [],
        "Site": [],
        "SeaArea": [],
        "Custom": []
    }
    current = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(":"):
            name = line[:-1]
            if name in categories:
                current = name
            continue
        if line.startswith("-") and current:
            categories[current].append(line[1:].strip())

    return categories

if __name__ == "__main__":
    create_database() 
    remove_duplicate_news()   
    news_list = get_news_list()

    all_news = []

    existing_count = 0
    MAX_EXISTING = 3

    for item in news_list:
        if news_exists(item["url"]):
            existing_count += 1

            if existing_count >= MAX_EXISTING:
                print(f"{MAX_EXISTING} consecutive existing news found. Stop crawling.")
                break

            continue
        existing_count = 0
        news = get_article(item["url"])
        result = generate_ai_analysis(news["content"])
        (
            news["highlight_en"],
            news["highlight_zh"],
            news["note"],
            news["tags"]
        ) = parse_ai_response(result)

        all_news.append(news)
        insert_news(news)
        print("New:", news["title"])

    wb = Workbook()
    ws = wb.active
    ws.title = "Marine News"

    headers = [
        "title",
        "publish_date",
        "highlight_en",
        "highlight_zh",
        "note",
        "country",
        "technology",
        "topic",
        "company",
        "organization",
        "project",
        "site",
        "sea_area",
        "custom",
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
            ", ".join(news["tags"]["Country"]),
            ", ".join(news["tags"]["Technology"]),
            ", ".join(news["tags"]["Topic"]),
            ", ".join(news["tags"]["Company"]),
            ", ".join(news["tags"]["Organization"]),
            ", ".join(news["tags"]["Project"]),
            ", ".join(news["tags"]["Site"]),
            ", ".join(news["tags"]["SeaArea"]),
            ", ".join(news["tags"]["Custom"]),
            news["url"],
            news["author"]
        ])

    wb.save("MarineNews.xlsx")
    print("Excel exported.")
    print(f"New articles: {len(all_news)}")

