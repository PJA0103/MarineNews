# 海洋能國際新聞知識庫

## 專案介紹
海洋能國際新聞知識庫 是一套利用 **Python 爬蟲、AI 自動摘要與 SQLite 資料庫** 建立的海洋能新聞管理系統。
系統可自動蒐集 Offshore Energy 網站的海洋能新聞，透過 AI 產生中英文摘要、延伸思考（Note）及分類資訊，並建立本地端知識庫，方便後續搜尋、管理與分析。

---

## 功能特色
- 自動爬取最新海洋能新聞
- AI 產生中英文摘要
- AI 產生延伸思考（Note）
- 自動分類新聞
  - 國家（Country）
  - 技術（Technology）
  - 類別（Category）
  - 公司（Company）
  - 組織（Organization）
  - 專案（Project）
  - 地點（Site）
  - 海域（Sea Area）
- SQLite 本地端資料庫
- Streamlit 視覺化查詢介面
- 多條件搜尋
- 已讀／未讀管理
- 一鍵啟動程式
- 匯出目前查詢結果(Excel)

---

## 系統流程

```
Offshore Energy
        │
        ▼
   Python 爬蟲
        │
        ▼
AI 摘要與分類
        │
        ▼
 SQLite 資料庫
        │
        ▼
 Streamlit 查詢介面
```

---

## 專案架構

```
MarineNews/
│
├── crawler.py          # 每日新聞更新
├── backfill.py         # 歷史新聞回填
├── database.py         # SQLite 操作
├── app.py              # Streamlit 網頁介面
├── startup.bat         # 一鍵啟動
├── MarineNews.db       # 新聞資料庫
└── README.md
```

---

## 使用技術

- Python
- BeautifulSoup
- Requests
- SQLite
- Streamlit
- OpenAI API

---

## 使用方式

### 1. 更新最新新聞

```bash
python crawler.py
```

---

### 2. 回填歷史新聞

```bash
python backfill.py
```

---

### 3. 開啟查詢系統

```bash
streamlit run app.py
```

或直接執行

```
startup.bat
```

即可完成新聞更新並開啟系統。

---

## 查詢功能

系統支援以下查詢條件：

- 關鍵字
- 國家
- 技術
- 類別
- 公司
- 組織
- 專案
- 地點
- 海域
- 日期區間

可同時搭配多個條件，快速縮小搜尋範圍，提高查詢效率。

---

## 支援技術分類

目前系統支援以下海洋能技術：

- Wave Energy
- Tidal Stream
- Tidal Range
- Ocean Current
- OTEC

---

## 離線知識庫

所有新聞內容、AI 摘要、分類資訊及 Note 都會儲存在本地端 SQLite 資料庫。

- 不需網路即可查詢已蒐集的新聞。
- 即使原始新聞網站暫時無法存取，仍可正常搜尋與閱讀歷史資料。

僅有更新新聞時需要網路連線。

---

## 作者

PJA
