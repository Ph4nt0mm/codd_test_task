import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from starlette import status as response_status


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
