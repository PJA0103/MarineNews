from crawler import(
    get_news_list,
    get_article,
    generate_ai_analysis,
    parse_ai_response
)

from database import(
    create_database, 
    insert_news,
    news_exists
)

create_database()
page = 1

while True:

    print(f"\n===== Page {page} =====")
    news_list = get_news_list(page)

    if len(news_list) == 0:
        print("No news found.")
        break

    for item in news_list:
        if news_exists(item["url"]):
            print("Skip:", item["title"])
            continue

        news = get_article(item["url"])
        result = generate_ai_analysis(news["content"])
        (
            news["highlight_en"],
            news["highlight_zh"],
            news["note"],
            news["tags"]
        ) = parse_ai_response(result)
        insert_news(news)

        print("New:", news["title"])
    page += 1