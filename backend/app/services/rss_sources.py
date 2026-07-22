"""Curated list of real, public RSS feeds grouped by category.

Each entry: (source_name, feed_url, site_url, category_slug)
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
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "https://www.bbc.com/news", "general"),
    ("NPR News", "https://feeds.npr.org/1001/rss.xml", "https://www.npr.org", "general"),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", "https://www.bbc.com/news/world", "world"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "https://www.aljazeera.com", "world"),
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", "https://www.bbc.com/news/technology", "technology"),
    ("TechCrunch", "https://techcrunch.com/feed/", "https://techcrunch.com", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "https://www.theverge.com", "technology"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "https://www.bbc.com/news/business", "business"),
    ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml", "https://www.bbc.com/sport", "sports"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "https://www.espn.com", "sports"),
    ("BBC Entertainment", "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "https://www.bbc.com/news/entertainment_and_arts", "entertainment"),
    ("Variety", "https://variety.com/feed/", "https://variety.com", "entertainment"),
    ("BBC Health", "http://feeds.bbci.co.uk/news/health/rss.xml", "https://www.bbc.com/news/health", "health"),
    ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "https://www.bbc.com/news/science_and_environment", "science"),
    ("NASA", "https://www.nasa.gov/feed/", "https://www.nasa.gov", "science"),
]
