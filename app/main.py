import os
from apscheduler.schedulers.background import BackgroundScheduler
from app.update_db import main as update_db_main
from app.webserver import app

update_interval = int(os.environ.get("UPDATE_INTERVAL", 24)) * 3600

scheduler = BackgroundScheduler()
scheduler.add_job(update_db_main, 'interval', seconds=update_interval)
scheduler.start()

if __name__ == "__main__":
    update_db_main()
    app.run(host="0.0.0.0", port=5000)
