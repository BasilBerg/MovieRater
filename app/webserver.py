from flask import Flask, render_template_string, request
import sqlite3
from datetime import datetime
from app import DB_PATH

app = Flask(__name__)

SORTABLE_COLUMNS = [
    "creator", "title", "category", "duration", "vote_average",
    "imdb_id", "imdb_rating", "rotten_tomatoes", "metacritic",
    "media_type", "downloaded", "created_at"
]



@app.route("/")
def index():
    sort = request.args.get("sort", "imdb_rating")
    order = request.args.get("order", "desc")
    if sort not in SORTABLE_COLUMNS:
        sort = "imdb_rating"
    if order not in ("asc", "desc"):
        order = "desc"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = f"""
        SELECT
            creator, title, link, category, duration, vote_average,
            imdb_id, imdb_rating, rotten_tomatoes, metacritic,
            media_type, downloaded, created_at
        FROM media
        ORDER BY
            CASE WHEN {sort} IS NULL OR {sort} = 'N/A' THEN 1 ELSE 0 END,
            {sort} {'ASC' if order == 'asc' else 'DESC'}
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    formatted_rows = []
    for row in rows:
        row_dict = dict(row)
        created_at = row_dict.get('created_at')
        if created_at:
            try:
                dt = datetime.fromisoformat(str(created_at))
                row_dict['created_at'] = dt.date().isoformat()
            except Exception:
                row_dict['created_at'] = str(created_at)[:10]
        formatted_rows.append(row_dict)

    def next_order(col):
        if col == sort:
            return "desc" if order == "asc" else "asc"
        return "asc"

    html = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>MovieRater</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #fafafa; }
            h1 { text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f0f0f0; position: sticky; top: 0; cursor: pointer; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .true { color: green; font-weight: bold; }
            .false { color: red; }
        </style>
    </head>
    <body>
        <h1>MovieRater</h1>
        <table>
            <thead>
                <tr>
                    {% for col in columns %}
                    <th>
                        <a href="/?sort={{ col }}&order={{ next_order(col) }}">
                            {{ col.replace('_', ' ').title() }}
                            {% if sort == col %}
                                {% if order == 'asc' %}▲{% else %}▼{% endif %}
                            {% endif %}
                        </a>
                    </th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr>
                    <td>{{ row['creator'] or '' }}</td>
                    <td><a href="{{ row['link'] }}" target="_blank">{{ row['title'] or '' }}</a></td>
                    <td>{{ row['category'] or '' }}</td>
                    <td>{{ row['duration'] or '' }}</td>
                    <td>{{ row['vote_average'] or '' }}</td>
                    <td>
                        {% if row['imdb_id'] %}
                            <a href="https://www.imdb.com/title/{{ row['imdb_id'] }}" target="_blank">
                                {{ row['imdb_id'] }}
                            </a>
                        {% else %}
                            –   
                        {% endif %}
        
                    </td>
                    <td>{{ row['imdb_rating'] if row['imdb_rating'] not in (None, 'N/A') else '' }}</td>
                    <td>{{ row['rotten_tomatoes'] or '' }}</td>
                    <td>{{ row['metacritic'] or '' }}</td>
                    <td>{{ row['media_type'] or '' }}</td>
                    <td class="{{ 'true' if row['downloaded'] else 'false' }}">
                        {{ '✔️' if row['downloaded'] else '❌' }}
                    </td>
                    <td>{{ row['created_at'] or '' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(
        html,
        rows=formatted_rows,
        columns=SORTABLE_COLUMNS,
        sort=sort,
        order=order,
        next_order=next_order
    )

