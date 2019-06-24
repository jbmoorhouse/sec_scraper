# sec_scraper

## What is it?

**sec_scraper** is a scraping tool, leveraging the [**Scrapy project**](https://github.com/scrapy) framework. It's aimed at crawling the [**Securities and Exchange Commission** (SEC)](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm), extracting 10-K (annual) financial documents for each company in the SEC's [**company directory**](https://www.sec.gov/divisions/corpfin/organization/cfia-123.htm). It is anticipated that these documents will be later used for sentiment analysis as part of alpha research using [Quantopian](https://www.quantopian.com/).

## Requirements

* Python 3.4+
* Scrapy 1.6

### Prerequisites 

The program was developed on Windows 10, utilising the Windows [Anaconda distribution](https://www.anaconda.com/distribution/). In order to install scrapy using the Windows anaconda, execute the following command using `conda`. Please refer to the [Scrapy installation guide](http://doc.scrapy.org/en/latest/intro/install.html) for further details

```
conda install -c conda-forge scrapy
```

