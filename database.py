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
            author TEXT
        )
    """)

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
    
def count_news():

    connectDB = sqlite3.connect("MarineNews.db")
    cursor = connectDB.cursor()

    cursor.execute("SELECT COUNT(*) FROM news")
    count = cursor.fetchone()[0]

    connectDB.close()
    print(f"News in database: {count}")