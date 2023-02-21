from tortoise import fields
from tortoise.models import Model


class MetroNews(Model):
    id = fields.IntField(pk=True)
    date_added_on_site = fields.DatetimeField()
    date_downloaded = fields.DatetimeField(auto_now_add=True)
    title = fields.CharField(max_length=1024)
    image_url = fields.CharField(max_length=128, null=True)

    class Meta:
        table = 'metro_news'
