import requests
import feedparser
import sqlite3
import logging
import datetime
from urllib.parse import quote
from app import DB_PATH, RSS_FEED_URL, TMDB_API_URL, OMDB_API_URL, LANGUAGE, TMDB_API_KEY, OMDB_API_KEY




logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        description TEXT,
        pubdate TEXT,
        link TEXT,
        creator TEXT,
        duration INTEGER,
        tmdb_id INTEGER,
        popularity REAL,
        vote_average REAL,
        vote_count INTEGER,
        imdb_id TEXT,
        imdb_rating REAL,
        rotten_tomatoes TEXT,
        metacritic TEXT,
        awards TEXT,
        boxoffice TEXT,
        media_type TEXT,
        type TEXT,
        downloaded BOOLEAN,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()


def parse_rss():
    feed = feedparser.parse(RSS_FEED_URL)
    items = []
    for entry in feed.entries:
        duration = int(entry.get('duration', 0))
        duration_min = duration // 60
        if duration_min >= 90:
            media_type = 'movie'
            title = entry.get('title', '')
        elif 20 <= duration_min < 90:
            media_type = 'tv'
            title = entry.get('title', '')
        else:
            continue
        items.append({
            'title': title,
            'category': entry.get('category', ''),
            'description': entry.get('description', ''),
            'pubdate': entry.get('published', ''),
            'link': entry.get('link', ''),
            'creator': entry.get('creator', ''),
            'duration': duration_min,
            'media_type': media_type
        })
    return items


def entry_exists(title, link):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM media WHERE title = ? OR link = ? LIMIT 1", (title, link))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def get_tmdb_data(title, category, media_type):
    def query_tmdb(query, mtype):
        url = f"{TMDB_API_URL}/3/search/{mtype}?query={quote(query)}&include_adult=false&language={LANGUAGE}&page=1"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_KEY}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for result in data.get('results', []):
                return {
                    'tmdb_id': result.get('id'),
                    'popularity': result.get('popularity'),
                    'vote_average': result.get('vote_average'),
                    'vote_count': result.get('vote_count'),
                    'media_type': result.get('media_type') if result.get('media_type') else mtype,
                    'tmdb_title': result.get('title') or result.get('name')
                }
        logger.warning(f"No TMDB data found for query '{query}' and type '{mtype}'")
        return None

    query = title if media_type == 'movie' else category
    result = query_tmdb(query, media_type)
    if result:
        return result
    alt_type = 'tv' if media_type == 'movie' else 'movie'
    alt_query = category if alt_type == 'tv' else title
    logger.info(f"Trying alternative TMDB search: Query '{alt_query}', Type '{alt_type}'")
    alt_result = query_tmdb(alt_query, alt_type)
    if alt_result:
        alt_result['media_type'] = alt_type
        return alt_result
    return None


def get_tmdb_external_ids(tmdb_id, media_type):
    if not tmdb_id:
        logger.warning(f"No tmdb_id provided for type '{media_type}'")
        return None
    url = f"{TMDB_API_URL}/3/{media_type}/{tmdb_id}/external_ids"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.warning(f"Error fetching external IDs for tmdb_id {tmdb_id} ({media_type})")
        return None
    imdb_id = response.json().get('imdb_id')
    if not imdb_id:
        alt_media_type = 'tv' if media_type == 'movie' else 'movie'
        alt_url = f"{TMDB_API_URL}/3/{alt_media_type}/{tmdb_id}/external_ids"
        alt_response = requests.get(alt_url, headers=headers)
        if response.status_code != 200:
            logger.warning(f"Error fetching external IDs for tmdb_id {tmdb_id} ({alt_media_type})")
            return None
        imdb_id = alt_response.json().get('imdb_id')
        if not imdb_id:
            logger.warning(f"No IMDb ID found for tmdb_id {tmdb_id} in both types")
            return None

    return imdb_id


def get_omdb_data(imdb_id):
    if not imdb_id:
        return {}
    url = f"{OMDB_API_URL}/?apikey={OMDB_API_KEY}&i={imdb_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return {}
    data = response.json()
    ratings = {r['Source']: r['Value'] for r in data.get('Ratings', [])}
    return {
        'imdb_rating': data.get('imdbRating'),
        'rotten_tomatoes': ratings.get('Rotten Tomatoes'),
        'metacritic': ratings.get('Metacritic'),
        'awards': data.get('Awards'),
        'boxoffice': data.get('BoxOffice'),
        'type': data.get('Type')
    }


def save_to_db(item):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO media (
        title, category, description, pubdate, link, creator, duration, tmdb_id, popularity, vote_average, vote_count, media_type, imdb_id, imdb_rating, rotten_tomatoes, metacritic, awards, boxoffice, type, downloaded, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (
                  item.get('title'),
                  item.get('category'),
                  item.get('description'),
                  item.get('pubdate'),
                  item.get('link'),
                  item.get('creator'),
                  item.get('duration'),
                  item.get('tmdb_id'),
                  item.get('popularity'),
                  item.get('vote_average'),
                  item.get('vote_count'),
                  item.get('media_type'),
                  item.get('imdb_id'),
                  item.get('imdb_rating'),
                  item.get('rotten_tomatoes'),
                  item.get('metacritic'),
                  item.get('awards'),
                  item.get('boxoffice'),
                  item.get('type'),
                  False,
                  datetime.datetime.now().isoformat()
              )
              )
    conn.commit()
    conn.close()


def main():
    init_db()
    items = parse_rss()
    logger.info(f"Found entries: {len(items)}")
    for item in items:
        if entry_exists(item['title'], item['link']):
            logger.info(f"Already exists: {item['title']}")
            continue
        tmdb = get_tmdb_data(item['title'], item['category'], item['media_type'])
        if tmdb:
            item.update(tmdb)
            imdb_id = get_tmdb_external_ids(item.get('tmdb_id'), item['media_type'])
            item['imdb_id'] = imdb_id
            omdb = get_omdb_data(imdb_id)
            item.update(omdb)
        else:
            item['tmdb_id'] = None
            item['popularity'] = None
            item['vote_average'] = None
            item['vote_count'] = None
            item['media_type'] = item['media_type']
            item['imdb_id'] = None
            item['imdb_rating'] = None
            item['rotten_tomatoes'] = None
            item['metacritic'] = None
            item['awards'] = None
            item['boxoffice'] = None
            item['type'] = None
        save_to_db(item)
        logger.info(f"Saved: {item['title']}")
