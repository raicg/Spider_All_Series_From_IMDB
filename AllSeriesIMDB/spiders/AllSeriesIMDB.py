# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from ..items import *
from ..items import SerieItem
from scrapy import Spider


class AllSeriesIMDBSpider(Spider):
    name = 'AllSeriesIMDB'
    start_urls = ['https://www.imdb.com/search/title?title_type=tv_series&release_date=1980-01-01,2020-03-01&count=250']
    stop = 0

    def parse(self, response):
        body = response.xpath("//div[contains(@class, 'lister-list')]")
        dataColumns = body.xpath(".//div[contains(@class, 'lister-item-content')]")

        for column in dataColumns:
        
            headerColumn = column.xpath(".//h3[@class='lister-item-header']")
            
            popularity = ""
            popularityDirty = headerColumn.xpath(".//span[contains(@class, 'lister-item-index')]//text()").extract_first()
            popularityDirty = popularityDirty.split(".")
            popularityDirty = popularityDirty[0].split(",")
            for i in range(0, len(popularityDirty) ):
              popularity = popularity + popularityDirty[i]

            link = headerColumn.xpath("./a")

            title = link.xpath("./text()").extract_first()
            href = link.xpath("./@href").extract_first()

            yield response.follow(
                    href,
                    callback=self.parse_serie,
                    meta={'title': title, 'popularity': popularity}
            )

        nextPageDiv = response.xpath("//div[@class='desc']")
        nextPage = nextPageDiv.xpath(".//a[contains(@class, 'next-page')]//@href").extract_first()
        if nextPage is not None:
            
            yield response.follow(
                    nextPage,
                    callback=self.parse
            )     

    def parse_serie(self, response):

        divGenre = response.xpath("//div[@class='title_wrapper']")

        genre = divGenre.xpath(".//a[contains(@href, 'genres=')]//text()").extract()

        divImage = response.xpath("//div[contains(@class, 'poster')]")      

        image = divImage.xpath(".//img//@src").extract_first()

        divYearLastSeason = response.xpath("//div[@class='seasons-and-year-nav']")

        yearLastSeason = divYearLastSeason.xpath(".//a[contains(@href, 'year=')]//text()").extract()

        company = response.xpath("//a[contains(@href, '/company/')]//text()").extract()

        if 'See more' in company:
            company.pop()

        loader = ItemLoader(item=SerieItem(), response=response)
        loader.add_value('popularity', response.meta.get('popularity'))
        loader.add_value('title', response.meta.get('title'))

        if yearLastSeason != []:
            if '… See all' in yearLastSeason[0]:
                loader.add_value('yearLastSeason', yearLastSeason[1])
            else:
                loader.add_value('yearLastSeason', yearLastSeason[0])

        else:
            loader.add_value('yearLastSeason', yearLastSeason)

        
        loader.add_value('genre', genre)
        loader.add_value('image', image)
        loader.add_value('company', company)

        return loader.load_item()
