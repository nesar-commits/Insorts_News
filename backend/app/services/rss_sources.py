"""Curated list of real, public RSS feeds grouped by category.

Each entry: (source_name, feed_url, site_url, category_slug, region, language)

`region` is the ISO 3166-1 alpha-2 country code the source primarily covers,
`language` the ISO 639-1 code of the language it's actually published in —
together they power "nearby news" (see app/services/geolocation.py) and its
language-preference refinement. None means not tied to one.

Only 12 of India's 22 official languages are covered below (Hindi, Bengali,
Tamil, Telugu, Marathi, Gujarati, Punjabi, Urdu, Nepali, Kannada, Malayalam,
Odia) — every URL was manually verified to be a live, real feed actually
published in that language. The other 10 (Assamese, Bodo, Dogri, Kashmiri,
Konkani, Maithili, Manipuri, Sanskrit, Santali, Sindhi) simply don't have a
findable public RSS feed with real content in that language; nothing here
fakes one. Note BBC Nepali's editorial focus is Nepal, not India, so its
India-specific coverage is thinner than the other 11.
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
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "https://www.bbc.com/news", "general", "GB", "en"),
    ("NPR News", "https://feeds.npr.org/1001/rss.xml", "https://www.npr.org", "general", "US", "en"),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", "https://www.bbc.com/news/world", "world", "GB", "en"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "https://www.aljazeera.com", "world", "QA", "en"),
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", "https://www.bbc.com/news/technology", "technology", "GB", "en"),
    ("TechCrunch", "https://techcrunch.com/feed/", "https://techcrunch.com", "technology", "US", "en"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "https://www.theverge.com", "technology", "US", "en"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "https://www.bbc.com/news/business", "business", "GB", "en"),
    ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml", "https://www.bbc.com/sport", "sports", "GB", "en"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "https://www.espn.com", "sports", "US", "en"),
    ("BBC Entertainment", "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "https://www.bbc.com/news/entertainment_and_arts", "entertainment", "GB", "en"),
    ("Variety", "https://variety.com/feed/", "https://variety.com", "entertainment", "US", "en"),
    ("BBC Health", "http://feeds.bbci.co.uk/news/health/rss.xml", "https://www.bbc.com/news/health", "health", "GB", "en"),
    ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "https://www.bbc.com/news/science_and_environment", "science", "GB", "en"),
    ("NASA", "https://www.nasa.gov/feed/", "https://www.nasa.gov", "science", "US", "en"),
    ("The Hindu", "https://www.thehindu.com/news/national/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en"),
    ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "https://timesofindia.indiatimes.com", "general", "IN", "en"),
    ("Hindustan Times", "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "https://www.hindustantimes.com", "general", "IN", "en"),
    ("BBC Hindi", "https://www.bbc.com/hindi/index.xml", "https://www.bbc.com/hindi", "general", "IN", "hi"),
    ("BBC Bengali", "https://www.bbc.com/bengali/index.xml", "https://www.bbc.com/bengali", "general", "IN", "bn"),
    ("BBC Tamil", "https://www.bbc.com/tamil/index.xml", "https://www.bbc.com/tamil", "general", "IN", "ta"),
    ("BBC Telugu", "https://feeds.bbci.co.uk/telugu/rss.xml", "https://www.bbc.com/telugu", "general", "IN", "te"),
    ("BBC Marathi", "https://feeds.bbci.co.uk/marathi/rss.xml", "https://www.bbc.com/marathi", "general", "IN", "mr"),
    ("BBC Gujarati", "https://feeds.bbci.co.uk/gujarati/rss.xml", "https://www.bbc.com/gujarati", "general", "IN", "gu"),
    ("BBC Punjabi", "https://feeds.bbci.co.uk/punjabi/rss.xml", "https://www.bbc.com/punjabi", "general", "IN", "pa"),
    ("BBC Urdu", "https://www.bbc.com/urdu/index.xml", "https://www.bbc.com/urdu", "general", "IN", "ur"),
    ("BBC Nepali", "https://www.bbc.com/nepali/index.xml", "https://www.bbc.com/nepali", "general", "IN", "ne"),
    ("Oneindia Kannada", "https://kannada.oneindia.com/rss/kannada-news-fb.xml", "https://kannada.oneindia.com", "general", "IN", "kn"),
    ("Oneindia Malayalam", "https://malayalam.oneindia.com/rss/malayalam-news-fb.xml", "https://malayalam.oneindia.com", "general", "IN", "ml"),
    ("OTV Odia", "https://odishatv.in/feed", "https://odishatv.in", "general", "IN", "or"),
]
