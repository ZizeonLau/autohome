#import urllib2
import urllib.request
import re
import importlib
#import imp
import json
import sys
import regex
import urllib.parse as urlparse
from scrapy import Selector
from scrapy.spiders import CrawlSpider

from scrapy.http import Request


class Car(CrawlSpider):
    name = "car"
    allowed_domains = ["autohome.com.cn"]
    start_urls = 'https://www.autohome.com.cn/grade/carhtml/{headChar}.html'


    def start_requests(self):
        for i in range(ord('A'), ord('Z') + 1):
            url = self.start_urls.format(headChar=chr(i))
            yield Request(url=url, callback=self.parse)
            # response.meta.get

    def parse(self, response):
        if response:
            sel = Selector(response)
            branchBox = sel.xpath('//dl')
            # print(branchBox)
            # print(branchList)
            #caridList = []
            for branch in branchBox:
                carInfoBase = {}
                #carInfoBase['branchName'] = branch.xpath('./dt/div/a/text()').extract_first() or 'Null'
                branchName = branch.xpath('./dt/div/a/text()').extract_first() or 'Null'
                subBranchList = branch.xpath('./dd/div[@class="h3-tit"]')
                carSeriesSetList = branch.xpath('./dd/ul[@class="rank-list-ul"]')
                # print(len(subBranchList), len(carSeriesSetList))
                # print(subBranchList)
                for index, subBranchName in enumerate(subBranchList):
                    carInfoBase[subBranchName.xpath('./text()').extract_first()] = []
                    #print(carInfoBase)
                    for carSeries in carSeriesSetList[index].xpath('./li'):
                        Name = carSeries.xpath('./h4/a/text()').extract_first()
                        if Name:
                            scarid = carSeries.xpath('./@id').extract_first()
                            carid = regex.sub('[s]', '',scarid)
                            html = "https://car.autohome.com.cn/config/series/"
                            carid = carid + ".html"
                            carhtml = html + carid
                            #carSeriesInfo = {'carSeriesName': carSeries.xpath('./h4/a/text()').extract_first(),
                            #                    'carSeriesPrice': carSeries.xpath('./div/a[@class="red"]/text()').extract_first(),
                            #                    'carSeriesURL': carhtml}
                            #carInfoBase[subBranchName.xpath('./text()').extract_first()].append(carSeriesInfo)
                            #caridList.append(carSeriesInfo)
                            if carhtml:
                                yield Request(url=carhtml, callback=self.parse_toconfigure, meta={'branchName':branchName,'carseries':Name})
                        #yield(carInfoBase)
                #yield(carInfoBase)
            #print(caridList)

    def parse_toconfigure(self, response):
        if response:
            carSeries = response.meta
            specIDr = r'var specIDs =(\[.*\])'
            specIDb = regex.search(specIDr, response.body_as_unicode())
            specidc = json.loads(specIDb.group(1))
            configr = r'var config = ({.*})'
            configb = regex.search(configr, response.body_as_unicode())
            configc = json.loads(configb.group(1))
            optionr = r'var option = ({.*})'
            optionb = regex.search(optionr, response.body_as_unicode())
            optionc = json.loads(optionb.group(1))
            colorr = r'var color = ({.*})'
            colorb = regex.search(colorr, response.body_as_unicode())
            colorc = json.loads(colorb.group(1))
            innercolorr = r'var innerColor =({.*})'
            innercolorb = regex.search(innercolorr, response.body_as_unicode())
            innercolorc = json.loads(innercolorb.group(1))
            configBaseList = configc.get('result').get('paramtypeitems')
            optionBaseList = optionc.get('result').get('configtypeitems')
            colorBaseList = colorc.get('result').get('specitems')
            innercolorBaseList = innercolorc.get('result').get('specitems')
            carList=[]

            class car(object):
                外观颜色 = []
                内饰颜色 = []

            for idc in specidc:
                car_item = car()
                car_item.carSeriesName = carSeries.get('carseries')
                car_item.branchName = carSeries.get('branchName')
                setattr(car_item,'specid',idc)
                carList.append(car_item)

            def get_value(paramdict, specid):
                for item in paramdict.get('valueitems'):
                    if item.get('specid') == specid:
                        htmlvalue = item.get('value')
                        textvalue = regex.sub('<[^>]+>', '', htmlvalue)
                        textvalue = textvalue.replace("&nbsp;", "")
                        htmlname = paramdict.get('name')
                        textname = regex.sub('<[^>]+>', '', htmlname)
                        return textname, textvalue
                return None, None

            for car in carList:
                for configBase in configBaseList:
                    for config in configBase.get('paramitems'):
                        name, value = get_value(config, car.specid)
                        if name and value:
                            setattr(car, name, value)
                for optionBase in optionBaseList:
                    for option in optionBase.get('configitems'):
                        name, value = get_value(option, car.specid)
                        if name and value:
                            setattr(car, name, value)
                for colorBase in colorBaseList:
                    if car.specid == colorBase.get('specid'):
                        setattr(car, '外观颜色', [])
                        for color in colorBase.get('coloritems'):
                            car.外观颜色.append(color.get('name'))
                for innercolorBase in innercolorBaseList:
                    if car.specid == innercolorBase.get('specid'):
                        setattr(car, '内饰颜色', [])
                        for innercolor in innercolorBase.get('coloritems'):
                            car.内饰颜色.append(innercolor.get('name'))

            for cardict in carList:
                if cardict.外观颜色:
                    pass
                else:
                    setattr(cardict, '外观颜色', '暂无')
                if cardict.内饰颜色:
                    pass
                else:
                    setattr(cardict, '内饰颜色', '暂无')
                yield(cardict.__dict__)