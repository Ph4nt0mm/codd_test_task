from fastapi import FastAPI
from tortoise import Tortoise, connections

from app import models as app_models
from settings.config import TORTOISE_ORM
from src.parser import get_news_for_last_n_days

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await Tortoise.init(config=TORTOISE_ORM)


@app.on_event("shutdown")
async def shutdown_event():
    await connections.close_all()


@app.get(
    "/metro/news",
    response_model=app_models.NewsResponse,
    summary='Get news for last N days',
    description='Get all news parsed for last N days'
)
async def generate_oil_dataframe(days: int = 1):
    news_list = await get_news_for_last_n_days(days)
    return [
        app_models.News(
            news_title=news.title,
            image_url=news.image_url,
            publication_date=news.date_added_on_site.strftime("%Y-%m-%d")
        ) for news in news_list]
