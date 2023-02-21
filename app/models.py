from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class News(BaseModel):
    news_title: str
    image_url: Optional[str]
    publication_date: date


NewsResponse = List[News]
