"""Curated list of real, public RSS feeds grouped by category.

Each entry: (source_name, feed_url, site_url, category_slug, region)

`region` is the ISO 3166-1 alpha-2 country code the source primarily covers
— used to power "nearby news" (see app/services/geolocation.py). None means
the source isn't tied to any single country.
"""

CATEGORIES = [
    {"name": "Top Stories", "slug": "general", "icon": "newspaper"},
    {"name": "World", "slug": "world", "icon": "globe"},
    {"name": "Technology", "slug": "technology", "icon": "cpu"},
    {"name": "Business", "slug": "business", "icon": "briefcase"},
    {"name": "Sports", "slug": "sports", "icon": "trophy"},
    {"name": "Entertainment", "slug": "entertainment", "icon": "film"},
    {"name": "Health", "slug": "health", "icon": "heart-pulse"},
    {"name": "Science", "slug": "science", "icon": "flask-conical"},
]

FEEDS = [
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "https://www.bbc.com/news", "general", "GB"),
    ("NPR News", "https://feeds.npr.org/1001/rss.xml", "https://www.npr.org", "general", "US"),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", "https://www.bbc.com/news/world", "world", "GB"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "https://www.aljazeera.com", "world", "QA"),
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", "https://www.bbc.com/news/technology", "technology", "GB"),
    ("TechCrunch", "https://techcrunch.com/feed/", "https://techcrunch.com", "technology", "US"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "https://www.theverge.com", "technology", "US"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "https://www.bbc.com/news/business", "business", "GB"),
    ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml", "https://www.bbc.com/sport", "sports", "GB"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "https://www.espn.com", "sports", "US"),
    ("BBC Entertainment", "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "https://www.bbc.com/news/entertainment_and_arts", "entertainment", "GB"),
    ("Variety", "https://variety.com/feed/", "https://variety.com", "entertainment", "US"),
    ("BBC Health", "http://feeds.bbci.co.uk/news/health/rss.xml", "https://www.bbc.com/news/health", "health", "GB"),
    ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "https://www.bbc.com/news/science_and_environment", "science", "GB"),
    ("NASA", "https://www.nasa.gov/feed/", "https://www.nasa.gov", "science", "US"),
    ("The Hindu", "https://www.thehindu.com/news/national/feeder/default.rss", "https://www.thehindu.com", "general", "IN"),
    ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "https://timesofindia.indiatimes.com", "general", "IN"),
    ("Hindustan Times", "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "https://www.hindustantimes.com", "general", "IN"),
]
