MovieRater
==========


MovieRater is specifically designed for content from the media libraries of German public broadcasters and uses the RSS feed from [MediathekViewWeb](https://github.com/mediathekview/mediathekviewweb). It automatically collects and enriches movie and TV show data, stores everything in a local SQLite database, and provides a sortable web interface for browsing entries. The RSS Feed will periodically be checked for new entries.  
While made for this purpose, it can be adapted for other RSS feeds with minor modifications.
## Obtaining API Keys
To use MovieRater, you will need API keys for both The Movie Database (TMDb) and the Open Movie Database (OMDb).  
Both services provide free access for non-commercial purposes.  
Get your TMDb API key here: https://www.themoviedb.org/settings/api  
Get your OMDb API key here: https://www.omdbapi.com/apikey.aspx

## Environment Variables

| Variable          | Default                            | Description                                     |
|-------------------|------------------------------------|-------------------------------------------------|
| `TMDB_API_KEY`    | _required_                         | API key for The Movie Database                  |
| `OMDB_API_KEY`    | _required_                         | API key for the Open Movie Database             |
| `UPDATE_INTERVAL` | 24                                 | Update interval (hours between RSS feed checks) |
| `DB_PATH`         | `/data/movierater.db`              | Path to the SQLite database                     |
| `RSS_FEED_URL`    | `https://mediathekviewweb.de/feed` | URL of the RSS feed                             |
| `TMDB_API_URL`    | `https://api.themoviedb.org`       | Base URL for The Movie Database API             |
| `OMDB_API_URL`    | `http://www.omdbapi.com`           | Base URL for the Open Movie Database API        |
| `LANGUAGE`        | `de`                               | Language of the titles, used for TMDB queries   |

## Setup

1. Create a `.env` file in your project root with your API keys:
   ```yaml
   TMDB_API_KEY = "your_tmdb_api_key"
   OMDB_API_KEY = "your_omdb_api_key"
   ```

2. Use the following `docker-compose.yaml` example to run the container:

   ```yaml
    services:
      movierater:
        image: basilberg/movierater:latest
        container_name: movierater
        restart: unless-stopped
        volumes:
          - ./movierater.db:/data
        ports:
          - "5000:5000"
        environment:
          TMDB_API_KEY: ${TMDB_API_KEY}
          OMDB_API_KEY: ${OMDB_API_KEY}    
          #DB_PATH: "/data/movierater.db"
          #RSS_FEED_URL: "https://mediathekviewweb.de/feed"
          #TMDB_API_URL: "https://api.themoviedb.org"
          #OMDB_API_URL: "http://www.omdbapi.com"
          #LANGUAGE: "de"
          #UPDATE_INTERVAL: 24
   ```

3. Start the service:
   ```sh
   docker compose up -d
   ```

4. Access the web interface at [http://localhost:5000](http://localhost:5000)

