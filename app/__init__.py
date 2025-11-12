import os

DB_PATH = os.environ.get("DB_PATH", "/data/movierater.db")
RSS_FEED_URL = os.environ.get("RSS_FEED_URL", "https://mediathekviewweb.de/feed")
TMDB_API_URL = os.environ.get("TMDB_API_URL", "https://api.themoviedb.org")
OMDB_API_URL = os.environ.get("OMDB_API_URL", "http://www.omdbapi.com")
LANGUAGE = os.environ.get("LANGUAGE", "de")

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")
