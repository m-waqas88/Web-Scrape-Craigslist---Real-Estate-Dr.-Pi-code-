import scrapy
import os
from .. items import ScrapePropertiesItem


class PropertiesSpider(scrapy.Spider):
    name = 'properties'
    start_urls = ['https://newyork.craigslist.org/d/real-estate/search/rea/']

    try:
        os.remove('results.csv')
    except OSError:
        pass

    def parse(self, response):

        all_adds = response.xpath('//li[@class="result-row"]')

        for ads in all_adds:

            title = ads.xpath('div/h3/a/text()').get()
            date_posted = ads.xpath('div/time/text()').get()
            price = ads.xpath('div/span/span[@class="result-price"]/text()').get()
            hood = ads.xpath('div/span/span[@class="result-hood"]/text()').get()
            details_link = ads.xpath('div/h3/a/@href').get()
            current_url = response.url

            # url = response.xpath('//li[@class="result-row"]/a/@href').get()
            request = scrapy.Request(url=details_link, callback=self.parse_details, cb_kwargs={
                'price': price,
                'date_posted': date_posted,
                'title': title,
                'hood': hood,
                'details_link': details_link,
                'current_url': current_url
            })

            yield request

        next_button = response.xpath('//a[@class="button next"]/@href').get()

        if next_button is not None:
            yield response.follow(next_button, callback=self.parse)

    def parse_details(self, response, price, date_posted, title, hood, details_link, current_url):

        item = ScrapePropertiesItem()

        lon = response.xpath('//meta[@name="geo.position"]/@content').get().split(';')[0]
        lat = response.xpath('//meta[@name="geo.position"]/@content').get().split(';')[1]

        item['price'] = price
        item['date_posted'] = date_posted
        item['title'] = title
        item['hood'] = hood
        item['details_link'] = details_link
        item['current_url'] = current_url
        item['lon'] = lon
        item['lat'] = lat

        yield item
