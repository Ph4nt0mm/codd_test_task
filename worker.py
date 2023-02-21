import asyncio
import logging

from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from tortoise import Tortoise, connections

from settings.config import TORTOISE_ORM
from settings.config import settings
from src.parser import parse_news_page

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    jobstores = {
        'default': SQLAlchemyJobStore(
            url=f'postgresql://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DATABASE}')
    }
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    scheduler = BlockingScheduler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Tortoise.init(config=TORTOISE_ORM))
    scheduler.add_job(parse_news_page, 'interval', seconds=100, args=[loop])
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit) as e:
        pass
    finally:
        scheduler.shutdown()
        loop.run_until_complete(connections.close_all())
