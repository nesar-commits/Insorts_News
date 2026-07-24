"""Curated list of real, public RSS feeds grouped by category.

Each entry: (source_name, feed_url, site_url, category_slug, region, language, city)

`region` is the ISO 3166-1 alpha-2 country code the source primarily covers,
`language` the ISO 639-1 code of the language it's actually published in,
`city` the specific city it's local to (None for national/international
sources) — together they power "nearby news" (see geolocation.py) with a
city > region+language > region > general fallback chain.

Only 12 of India's 22 official languages are covered below (Hindi, Bengali,
Tamil, Telugu, Marathi, Gujarati, Punjabi, Urdu, Nepali, Kannada, Malayalam,
Odia) — every URL was manually verified to be a live, real feed actually
published in that language. The other 10 (Assamese, Bodo, Dogri, Kashmiri,
Konkani, Maithili, Manipuri, Sanskrit, Santali, Sindhi) simply don't have a
findable public RSS feed with real content in that language; nothing here
fakes one. Note BBC Nepali's editorial focus is Nepal, not India, so its
India-specific coverage is thinner than the other 11.

City coverage is similarly a curated, verified subset (10 cities) — not
literally every city in the world, since no comprehensive source for that
exists. Every feed here was checked for real, on-topic local content before
being added (e.g. a "Hyderabad" candidate that turned out to be generic
national news was rejected).
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
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "https://www.bbc.com/news", "general", "GB", "en", None),
    ("NPR News", "https://feeds.npr.org/1001/rss.xml", "https://www.npr.org", "general", "US", "en", None),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", "https://www.bbc.com/news/world", "world", "GB", "en", None),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "https://www.aljazeera.com", "world", "QA", "en", None),
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", "https://www.bbc.com/news/technology", "technology", "GB", "en", None),
    ("TechCrunch", "https://techcrunch.com/feed/", "https://techcrunch.com", "technology", "US", "en", None),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "https://www.theverge.com", "technology", "US", "en", None),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "https://www.bbc.com/news/business", "business", "GB", "en", None),
    ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml", "https://www.bbc.com/sport", "sports", "GB", "en", None),
    ("ESPN", "https://www.espn.com/espn/rss/news", "https://www.espn.com", "sports", "US", "en", None),
    ("BBC Entertainment", "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "https://www.bbc.com/news/entertainment_and_arts", "entertainment", "GB", "en", None),
    ("Variety", "https://variety.com/feed/", "https://variety.com", "entertainment", "US", "en", None),
    ("BBC Health", "http://feeds.bbci.co.uk/news/health/rss.xml", "https://www.bbc.com/news/health", "health", "GB", "en", None),
    ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "https://www.bbc.com/news/science_and_environment", "science", "GB", "en", None),
    ("NASA", "https://www.nasa.gov/feed/", "https://www.nasa.gov", "science", "US", "en", None),
    ("The Hindu", "https://www.thehindu.com/news/national/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", None),
    ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "https://timesofindia.indiatimes.com", "general", "IN", "en", None),
    ("Hindustan Times", "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "https://www.hindustantimes.com", "general", "IN", "en", None),
    ("BBC Hindi", "https://www.bbc.com/hindi/index.xml", "https://www.bbc.com/hindi", "general", "IN", "hi", None),
    ("BBC Bengali", "https://www.bbc.com/bengali/index.xml", "https://www.bbc.com/bengali", "general", "IN", "bn", None),
    ("BBC Tamil", "https://www.bbc.com/tamil/index.xml", "https://www.bbc.com/tamil", "general", "IN", "ta", None),
    ("BBC Telugu", "https://feeds.bbci.co.uk/telugu/rss.xml", "https://www.bbc.com/telugu", "general", "IN", "te", None),
    ("BBC Marathi", "https://feeds.bbci.co.uk/marathi/rss.xml", "https://www.bbc.com/marathi", "general", "IN", "mr", None),
    ("BBC Gujarati", "https://feeds.bbci.co.uk/gujarati/rss.xml", "https://www.bbc.com/gujarati", "general", "IN", "gu", None),
    ("BBC Punjabi", "https://feeds.bbci.co.uk/punjabi/rss.xml", "https://www.bbc.com/punjabi", "general", "IN", "pa", None),
    ("BBC Urdu", "https://www.bbc.com/urdu/index.xml", "https://www.bbc.com/urdu", "general", "IN", "ur", None),
    ("BBC Nepali", "https://www.bbc.com/nepali/index.xml", "https://www.bbc.com/nepali", "general", "IN", "ne", None),
    ("Oneindia Kannada", "https://kannada.oneindia.com/rss/kannada-news-fb.xml", "https://kannada.oneindia.com", "general", "IN", "kn", None),
    ("Oneindia Malayalam", "https://malayalam.oneindia.com/rss/malayalam-news-fb.xml", "https://malayalam.oneindia.com", "general", "IN", "ml", None),
    ("OTV Odia", "https://odishatv.in/feed", "https://odishatv.in", "general", "IN", "or", None),
    # City-local sources — highest-priority match tier, above region/language.
    ("The Hindu Bengaluru", "https://www.thehindu.com/news/cities/bangalore/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", "Bengaluru"),
    ("The Hindu Hyderabad", "https://www.thehindu.com/news/cities/hyderabad/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", "Hyderabad"),
    ("Siasat Daily", "https://www.siasat.com/feed/", "https://www.siasat.com", "general", "IN", "en", "Hyderabad"),
    ("The Hindu Delhi", "https://www.thehindu.com/news/cities/delhi/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", "Delhi"),
    ("The Hindu Mumbai", "https://www.thehindu.com/news/cities/mumbai/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", "Mumbai"),
    ("The Hindu Chennai", "https://www.thehindu.com/news/cities/chennai/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", "Chennai"),
    ("The Hindu Kolkata", "https://www.thehindu.com/news/cities/kolkata/feeder/default.rss", "https://www.thehindu.com", "general", "IN", "en", "Kolkata"),
    ("New York Post Metro", "https://nypost.com/metro/feed/", "https://nypost.com", "general", "US", "en", "New York"),
    ("The Moscow Times", "https://www.themoscowtimes.com/rss/news", "https://www.themoscowtimes.com", "general", "RU", "en", "Moscow"),
    ("Block Club Chicago", "https://blockclubchicago.org/feed/", "https://blockclubchicago.org", "general", "US", "en", "Chicago"),
    ("BBC London", "https://feeds.bbci.co.uk/news/england/london/rss.xml", "https://www.bbc.com/news/england/london", "general", "GB", "en", "London"),
]
