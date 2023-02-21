import logging
from asyncio import SelectorEventLoop
from datetime import datetime, timedelta, date, timezone, time
from typing import List

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from starlette import status as response_status

from app.database import MetroNews


def get_soup_webpage() -> BeautifulSoup:
    url = "https://mosday.ru/news/tags.php?metro"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": "_ga=GA1.2.1338320064.1676455051; _gat_gtag_UA_49814013_1=1; _gid=GA1.2.319616539.1676630466; cookie_global_dttm=20230215125957; cookie_global_most=0; cookie_global_pcnt=14; cookie_global_usid=i0zaZK; _ym_isad=2; _ym_d=1676455052; _ym_uid=167645505263975919",
        "Upgrade-Insecure-Requests": "1",
        "Host": "mosday.ru",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
        "Connection": "keep-alive"
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code != response_status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=f'Some problems with requesting site')

    return BeautifulSoup(response.text, 'lxml')


def parse_news_page(loop: SelectorEventLoop):
    logging.info('Beginning parsing site')

    webpage = get_soup_webpage()

    # Извлечение таблиц, в которых записаны новости
    content_part_of_page = webpage.find('body').find_all('table', recursive=False)[1]
    part_of_tables = content_part_of_page.find('tr').find_all('td', recursive=False)[2].find('tr').find('center')
    news_tables = part_of_tables.find_all('table', recursive=False)

    # Получаем последние спаршенные новости, что бы не вставлять дубликаты в страницу
    last_added_news = loop.run_until_complete(get_news_for_last_n_days())
    last_added_news = last_added_news[0] if last_added_news else None

    new_news: List[MetroNews] = []
    for news_table in news_tables:
        for news_row in news_table.find_all('tr', recursive=False):
            # Получаем информацию об изображении
            news_columns = news_row.find_all('td', recursive=False)
            news_image_column = news_columns[0]
            image_link = news_image_column.find("img")

            if image_link is not None:
                image_link = f'https://mosday.ru/news/{image_link["src"]}'

            # Получаем информацию об изображении
            title_content = news_columns[1].contents[0]
            title_content_elements = title_content.contents

            # В таблице может пресутствовать строка "смотреть еще больше", отсекаем ее
            if len(title_content_elements) < 5:
                continue

            # Получаем информацию из заголовка
            publication_date = title_content_elements[0].text
            publication_time = title_content_elements[1].text.strip()
            publication_datetime = datetime.strptime(
                f'{publication_date} {publication_time} +0300', '%d.%m.%Y %H:%M %z'
            )
            publication_title = title_content.find('a')
            publication_title_text = publication_title.text
            publication_link = f'https://mosday.ru/news/{publication_title["href"]}'
            publication_number = publication_link[publication_link.find('?')+1:publication_link.find('&')]

            # Добавляем только свежие записи
            if last_added_news is not None:
                if last_added_news.date_added_on_site >= publication_datetime:
                    break

            new_news.append(MetroNews(
                id=publication_number,
                date_added_on_site=publication_datetime,
                title=publication_title_text,
                image_url=image_link
            ))

    # Сохраняем записи
    loop.run_until_complete(MetroNews.bulk_create(objects=new_news))
    logging.info(f'Have finished parsing site: have added {len(new_news)} tasks')


async def get_news_for_last_n_days(n_days: int = 1) -> List[MetroNews]:
    if n_days < 0:
        return []

    # Таблица возвращает в нулевой таймзоне, наткнулся на баг, что первые 3 часа нового дня записи не отображались
    moscow_timezone_delta = 3
    yesterday = datetime.combine(date.today(), time()) - timedelta(days=n_days, hours=moscow_timezone_delta)
    last_parsed_news = await MetroNews.filter(date_added_on_site__gte=yesterday).order_by('-date_added_on_site')

    # Добавляем 3 часа записям
    timezone_to_add = timezone(timedelta(hours=moscow_timezone_delta),  name="MSK")
    for news in last_parsed_news:
        news.date_added_on_site = news.date_added_on_site.astimezone(timezone_to_add)

    return last_parsed_news
