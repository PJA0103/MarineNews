import sqlite3

def create_database():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            publish_date TEXT,
            highlight_en TEXT,
            highlight_zh TEXT,
            note TEXT,
            country TEXT,
            technology TEXT,
            topic TEXT,
            company TEXT,
            organization TEXT,
            project TEXT,
            site TEXT,
            sea_area TEXT,
            custom TEXT,
            url TEXT,
            author TEXT,
            is_read INTEGER DEFAULT 0
        )
    """)
    try:
        cursor.execute("""
            ALTER TABLE news
            ADD COLUMN is_read INTEGER DEFAULT 0
        """)
    except:
        pass
    connectDB.commit()

    print("Database initialized.")
    connectDB.close()
    
def insert_news(news):
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()
    
    cursor.execute("""
        INSERT INTO news (
            title,
            publish_date,
            highlight_en,
            highlight_zh,
            note,
            country,
            technology,
            topic,
            company,
            organization,
            project,
            site,
            sea_area,
            custom,
            url,
            author
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
    ))

    connectDB.commit()
    connectDB.close()
    
def news_exists(url):
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM news WHERE url = ?",
        (url,)
    )
    exists = cursor.fetchone()[0] > 0
    connectDB.close()
    
    return exists

def count_news():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("SELECT COUNT(*) FROM news")
    count = cursor.fetchone()[0]

    connectDB.close()

def find_duplicate_urls():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        SELECT url, COUNT(*)
        FROM news
        GROUP BY url
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    connectDB.close()

    return duplicates

def remove_duplicate_news():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        DELETE FROM news
        WHERE id NOT IN(
            SELECT MIN(id)
            FROM news
            GROUP BY url
        )
    """)
    connectDB.commit()
    connectDB.close()

def get_news_by_country(country):
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        SELECT
            title, publish_date, url
        FROM news
        WHERE country LIKE ?
        ORDER BY publish_date DESC
    """, (f"%{country}%",))

    result = cursor.fetchall()
    connectDB.close()

    return result

def build_or_condition(column, values, conditions, params):
    """
    Build OR conditions for a specific column.
    Example:
    country=["Japan","United Kingdom"]
    params:
    ["%Japan%", "%United Kingdom%"]
    """
    if not values:
        return

    if isinstance(values, str):
        values = [values]

    placeholders = []

    for value in values:
        placeholders.append(f"{column} LIKE ?")
        params.append(f"%{value}%")

    conditions.append("(" + " OR ".join(placeholders) + ")")

def search_news(
    keyword=None,
    country=None,
    technology=None,
    topic=None,
    company=None,
    organization=None,
    project=None,
    site=None,
    sea_area=None,
    custom=None,
    start_date=None,
    end_date=None,
    unread_only=False
    ):
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    sql = """
    SELECT
        title,
        publish_date,
        highlight_en,
        highlight_zh,
        note,
        country,
        technology,
        topic,
        company,
        organization,
        project,
        site,
        sea_area,
        custom,
        url,
        author
    FROM news
    """
    conditions = []
    params = []
    if unread_only:
        conditions.append("is_read = 0")

    # OR conditions
    build_or_condition("country", country, conditions, params)
    build_or_condition("technology", technology, conditions, params)
    build_or_condition("topic", topic, conditions, params)
    build_or_condition("company", company, conditions, params)
    build_or_condition("organization", organization, conditions, params)
    build_or_condition("project", project, conditions, params)
    build_or_condition("site", site, conditions, params)
    build_or_condition("sea_area", sea_area, conditions, params)
    build_or_condition("custom", custom, conditions, params)

    # Keyword search
    if keyword:
        conditions.append("""
        (
            title LIKE ?
            OR highlight_en LIKE ?
            OR highlight_zh LIKE ?
            OR note LIKE ?
        )
        """)

        params.extend([
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ])

    # Date range
    if start_date:
        conditions.append("publish_date >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("publish_date <= ?")
        params.append(end_date)

    if conditions:
        sql += "\nWHERE\n"
        sql += "\nAND\n".join(conditions)

    sql += "\nORDER BY publish_date DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    connectDB.close()

    return rows

def get_all_countries():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        SELECT country
        FROM news
    """)
    rows = cursor.fetchall()
    connectDB.close()

    countries = set()
    for (value,) in rows:
        if not value:
            continue
        for item in value.split(","):
            item = item.strip()
            if item:
                countries.add(item)

    return sorted(countries)

def get_all_technologies():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        SELECT technology
        FROM news
    """)
    rows = cursor.fetchall()
    connectDB.close()

    technologies = set()
    for (value,) in rows:
        if not value:
            continue
        for item in value.split(","):
            item = item.strip()
            if item:
                technologies.add(item)

    return sorted(technologies)

def get_all_topics():
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        SELECT topic
        FROM news
    """)
    rows = cursor.fetchall()
    connectDB.close()

    topics = set()
    for (value,) in rows:
        if not value:
            continue
        for item in value.split(","):
            item = item.strip()
            if item:
                topics.add(item)

    return sorted(topics)

def mark_as_read(url):
    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        UPDATE news
        SET is_read = 1
        WHERE url = ?
    """, (url,))

    connectDB.commit()
    connectDB.close()

def mark_all_as_read():

    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        UPDATE news
        SET is_read = 1
    """)

    connectDB.commit()
    connectDB.close()

def count_read_status():

    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("""
        SELECT is_read, COUNT(*)
        FROM news
        GROUP BY is_read
    """)

    rows = cursor.fetchall()

    connectDB.close()

    return rows

def export_excel(rows):
    wb = workbook()
    ws = wb.active
    ws.title = "Marine News"
    
    headers =[
        "Title",
        "Publish Date",
        "Highlight EN",
        "Highlight ZH",
        "Note",
        "Country",
        "Technology",
        "Topic",
        "Company",
        "Organization",
        "Project",
        "Site",
        "Sea Area",
        "Custom",
        "URL",
        "Author"        
    ]
    
    ws.append(headers)
    for row in rows:
        ws.append(row)
        
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output
    
