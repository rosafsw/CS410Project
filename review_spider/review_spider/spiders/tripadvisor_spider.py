import scrapy
from review_spider.items import ReviewSpiderItem
"""
This is the spider to crawl the chicago hotel reviews from the tripadvisor.
use the command line to excute: scrapy crawl tripadvisor -o hotel_reviews.csv -s CLOSESPIDER_PAGECOUNT=1500
"""


class TripadvisorSpider(scrapy.Spider):

    name = "tripadvisor"
    start_urls = [
        "https://www.tripadvisor.com/Hotels-g35805-Chicago_Illinois-Hotels.html"
    ]

    def parse_review(self, response):
        item = ReviewSpiderItem()
        item['url'] = response
        item['review'] = response.xpath('//div[@class="entry"]/p/text()').extract()
        item['hotel_name'] = response.xpath('//div[@class="ui_column wrap_column meta-block-header"]/span/text()').extract()
        return item

    def parse_hotel(self, response):
        for href in response.xpath('//div[@class="quote"]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_review)

        next_page = response.xpath('//div[@class="unified pagination"]/span/a/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_hotel)

    def parse(self, response):
        for href in response.xpath('//div[@class="listing_title"]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)

        next_page = response.xpath('//div[@class="unified pagination standard_pagination"]/span/a/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)
