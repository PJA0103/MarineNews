from crawler import(
    get_news_list,
    get_article,
    generate_ai_analysis,
    parse_ai_response
)

from database import(
    create_database, 
    insert_news,
    news_exists,
    news_needs_update,
    update_news
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
        needs_update = news_exists(item["url"]) and news_needs_update(item["url"])
        if news_exists(item["url"]) and not needs_update:
            print("Skip:", item["title"])
            continue
        try:
            news = get_article(item["url"])

            if needs_update:
                update_news(news)
                print("Updated:", news["title"])
                continue

            result = generate_ai_analysis(news["content"])
            (
                news["highlight_en"],
                news["highlight_zh"],
                news["note"],
                news["tags"]
            ) = parse_ai_response(result)

            insert_news(news)
            print("New:", news["title"])
        except Exception as e:
            print(f"Error: {item['title']}")
            print(f"URL:{item['url']}")
            print(e)
            continue
    page += 1