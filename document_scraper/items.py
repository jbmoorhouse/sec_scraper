# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader.processors import TakeFirst, Identity


class CikItem(Item):
    cik = Field(output_processor = TakeFirst())
    report_date = Field(output_processor = TakeFirst())
    documents = Field(output_processor = TakeFirst())