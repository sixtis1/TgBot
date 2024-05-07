import feedparser

categories = {
    "В мире": "world/",
    'Политика': "politics/",
    "Проишествия": "incidents/",
    "Наука и техника": "tech/",
    "Военные новости": "army/",
    "Игры": "games/"
    }

def parse_news(rss: str):
    url = "https://news.rambler.ru/rss/"
    news_list = []
    feed = feedparser.parse(url + categories[rss])
    for entry in feed.entries:
        href = [enclosure.get('href', '') for enclosure in entry.enclosures]
        if href:
            href = href[0]
        news_item = {
                    "title": entry.title,
                    "description": entry.description,
                    "link": entry.link,
                    "href": href
                }
        news_list.append(news_item)
    print(news_list)
    return news_list


