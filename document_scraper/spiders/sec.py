import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from document_scraper.items import CikItem
from document_scraper.postprocess import MapComposeGen, get_ten_k
from scrapy.loader.processors import Compose, MapCompose
from datetime import datetime

class MySpider(CrawlSpider):
    name = 'demo'
    start_urls = ["https://www.sec.gov/divisions/corpfin/organization/cfia-123.htm"]

    custom_settings = {
        'DOWNLOAD_DELAY' : 0.25
    }

    def parse(self, response):

        for sel in response.xpath('(//*[@id="cos"]//tr)[position()>last()-10]'):#[position()>1]'):

            cik_number = sel.xpath("td[2]//text()").extract_first()

            yield response.follow(
                'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=10-K' \
                '&dateb=&owner=exclude&count=40'.format(cik_number),
                callback = self.index,
                meta = {'cik' : cik_number}
            )

        # alphanumeric_links = LinkExtractor(allow=r'/cfia-[a-z]+.htm')
        # for link in alphanumeric_links.extract_links(response):
        #     yield response.follow(
        #         link.url,
        #         callback=self.parse
        #   )

    def index(self, response):

        document_buttons = response.xpath(
            '//*[@id="documentsbutton"]/@href'
        )

        for url in document_buttons.extract():
            yield response.follow(
                url,
                callback=self.parse_page_two,
                meta={'cik' : response.meta['cik']}
            )

    def parse_page_two(self, response):

        filing_txt = response.xpath(
            '(//*[contains(@href, ".txt")])[last()]/@href'
        )

        document_info = response.xpath('(//*[@class="infoHead"]//text())').extract()

        if 'Period of Report' in document_info:
            idx = document_info.index('Period of Report')
            report_date = response.xpath('(//*[@class="info"]//text())[{}]'.format(idx + 1)).extract_first()

        for url in filing_txt.extract():
            yield response.follow(
                url,
                callback=self.parse_page_three,
                meta={'cik' : response.meta['cik'],
                      'report_date' : report_date}
            )

    def parse_page_three(self, response):

        loader = ItemLoader(item=CikItem(), response=response)

        loader.add_value(
            'cik',
            int(response.meta['cik']),
        )

        loader.add_value(
            'report_date',
            datetime.strptime(response.meta['report_date'], "%Y-%m-%d")
        )

        loader.add_xpath(
            'documents',
            "/html/body",
            MapComposeGen(get_ten_k)
        )

        return loader.load_item()

"""
2) Change back to all companies in (//*[@id="cos"]//tr)[position()>1]"""
