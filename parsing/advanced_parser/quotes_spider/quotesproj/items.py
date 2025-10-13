import scrapy

class QuoteItem(scrapy.Item):
    url = scrapy.Field()                 # task requirements
    parsed_at = scrapy.Field()           # parsing time
    text = scrapy.Field()                # quote text
    author = scrapy.Field()              # author name
    tags = scrapy.Field()                # tags list
    author_url = scrapy.Field()          # autor link
    author_born_date = scrapy.Field()
    author_born_location = scrapy.Field()
    author_description = scrapy.Field()