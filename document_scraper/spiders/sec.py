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

    with open(FILE_NAME, "r") as f:
        start_urls = f.read().splitlines()[:2]

    custom_settings = {
        'DOWNLOAD_DELAY' : 0.25
    }


    def parse(self, response):
        """
        The parse method extracts the filing document links for all Filing Dates, yielding all relavent request
        instances objects to follow. The request instances contain 10-K archive links which handled by the defined
        callback function.

        Parameters
        ----------
        response: scrapy.http.Response
            response (web page) from `start_urls` element


        Yields
        -------
        requests : generator
            requests contains each request instance to follow link url in document_button. The link url contains each
            10-K archive link indexed by Filing Date. Example request:
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
        The parse_page_two method follows the response object yielded in parse. The response objects are the requests
        for the 10-K document archive pages (e.g.
        https://www.sec.gov/Archives/edgar/data/1090872/000109087218000019/0001090872-18-000019-index.htm). The
        complete_submission_file are extracted and the request instances containing the submissions is returned

        Document 'Period of Report' information is passed to response.meta as 'report_date'.

        Parameters
        ----------
        response: scrapy.http.Response
            document archive indexed by date (e.g.
            https://www.sec.gov/Archives/edgar/data/1090872/000109087218000019/0001090872-18-000019-index.htm)

        Returns
        -------
        request : scrapy.http.Request
            request instance to follow complete_submission_file.txt link url

        """

        complete_submission_file = response.xpath(
            '(//*[contains(@href, ".txt")])[last()]/@href'
        )

        document_info = response.xpath('(//*[@class="infoHead"]//text())').extract()

        if 'Period of Report' in document_info:
            idx = document_info.index('Period of Report')

            # `idx + 1` since xpath is indexed from 1 unlike python which is indexed from 0
            report_date = response.xpath('(//*[@class="info"]//text())[{}]'.format(idx + 1)).extract_first()

        return response.follow(
            complete_submission_file.extract_first(),
            callback=self.parse_page_three,
            meta={'report_date' : report_date}#'cik' : response.meta['cik'],
        )


    def parse_page_three(self, response):
        """
        add_xpath method is applied to response instance (complete_submission_file). ItemLoader() is populated with
        documents, generated from response.xpath, along with cik and report_date, loaded from response.meta

        Parameters
        ----------
        response: scrapy.http.Response
            complete_submission_file

        Returns
        -------
        item: scrapy.loader.ItemLoader
        """

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
Change back to all companies in (//*[@id="cos"]//tr)[position()>1]"""
