import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose

from document_scraper.items import CikItem
from document_scraper.postprocess import MapComposeGen, get_ten_k

from datetime import datetime

import os



class MySpider(CrawlSpider):
    name = 'sec'

    DIR_NAME = os.getcwd()
    FILE_NAME = "cik.txt"

    if FILE_NAME in os.listdir(DIR_NAME):
        file_path = os.path.join(DIR_NAME, FILE_NAME)

    with open(FILE_NAME, "r") as f:
        start_urls = f.read().splitlines()[:2]

    custom_settings = {
        'DOWNLOAD_DELAY' : 0.25
    }

    #start_urls = ["https://www.sec.gov/divisions/corpfin/organization/cfia-123.htm"]

    # def parse(self, response):
    #
    #     for sel in response.xpath('(//*[@id="cos"]//tr)[last()]'):#[position()>last()-10]'):
    #
    #         cik_number = sel.xpath("td[2]//text()").extract_first()
    #
    #         yield response.follow(
    #             'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=10-K' \
    #             '&dateb=&owner=exclude&count=40'.format(cik_number),
    #             callback = self.index,
    #             meta = {'cik' : cik_number}
    #         )

        # alphanumeric_links = LinkExtractor(allow=r'/cfia-[a-z]+.htm')
        # for link in alphanumeric_links.extract_links(response):
        #     yield response.follow(
        #         link.url,
        #         callback=self.parse
        #   )

    def parse(self, response):
        """
        The parse method extracts the filing document links for all Filing Dates, yielding all
        relavent request instances objects to follow. The request instances contain 10-K archive links
        which handled by the defined callback function.

        Parameters
        ----------
        response: scrapy.http.Response object
            response (web page) from `start_urls` element

        Yields
        -------
        requests : generator
            requests contains each request instance to follow a specific link url. The link url contains
            each 10-K archive link indexed by Filing Date. Example request:
            https://www.sec.gov/Archives/edgar/data/1733998/000173399819000004/0001733998-19-000004-index.htm
        """

        document_buttons = response.xpath(
            '//*[@id="documentsbutton"]/@href'
        )

        for url in document_buttons.extract():
            yield response.follow(
                url,
                callback=self.parse_page_two#,
                #meta={'cik' : response.meta['cik']}
            )

    def parse_page_two(self, response):
        """
        The parse_page_two method follows the response object yielded in parse. The response objects
        are the requests for the 10-K document archive pages.
        """



        filing_txt = response.xpath(
            '(//*[contains(@href, ".txt")])[last()]/@href'
        )

        document_info = response.xpath('(//*[@class="infoHead"]//text())').extract()

        if 'Period of Report' in document_info:
            idx = document_info.index('Period of Report')
            report_date = response.xpath('(//*[@class="info"]//text())[{}]'.format(idx + 1)).extract_first()

        return response.follow(
            filing_txt.extract_first(),
            callback=self.parse_page_three,
            meta={'report_date' : report_date}#'cik' : response.meta['cik'],
        )

    def parse_page_three(self, response):

        loader = ItemLoader(item=CikItem(), response=response)

        # loader.add_value(
        #     'cik',
        #     int(response.meta['cik']),
        # )

        loader.add_value(
            'report_date',
            datetime.strptime(response.meta['report_date'], "%Y-%m-%d")
        )

        loader.add_xpath(
            'documents',
            "/html/body",
            MapCompose(get_ten_k)
        )

        return loader.load_item()

"""
2) Change back to all companies in (//*[@id="cos"]//tr)[position()>1]"""
