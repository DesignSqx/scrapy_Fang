# -*- coding: utf-8 -*-
import scrapy
from dashuju.items import nhItem, zfItem, spItem
import re


class FangSpider(scrapy.Spider):
    name = 'fang'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.html']

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get().strip()
            if "其它" in province_text:
                break
            if province_text:
                province = province_text
            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                url_mode = city_url.split("//")
                # url后面分割
                url_hou = url_mode[1].split(".")
                city_s = url_hou[0]
                if 'bj' in city_s:
                    nh_url = 'https://newhouse.fang.com/house/s/'
                    zf_url = 'https://zu.fang.com'
                    sp_url = 'https://shop.fang.com'
                else:
                    nh_url = url_mode[0] + '//' + city_s + '.newhouse.' + \
                             url_hou[1] + '.' + url_hou[2]
                    zf_url = url_mode[0] + '//' + city_s + '.zu.' + \
                             url_hou[1] + '.' + url_hou[2]
                    sp_url = url_mode[0] + '//' + city_s + '.shop.' + \
                             url_hou[1] + '.' + url_hou[2]
                # yield scrapy.Request(url=nh_url, callback=self.parse_nh,
                #                      meta={"info": (province, city)})
                # yield scrapy.Request(url=zf_url, callback=self.parse_zf,
                #                      meta={"info": (province, city)}, dont_filter=True)
                yield scrapy.Request(url=sp_url, callback=self.parse_sp,
                                     meta={"info": (province, city)}, dont_filter=True)



    def parse_nh(self, response):
        item = nhItem()
        province, city = response.meta.get('info')
        item['province'] = province
        item['city'] = city
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            # 房子名字
            name = str(li.xpath(".//div[@class='nlcd_name']/a/text()").get()).strip()
            item['name'] = name

            # 详情url
            url = response.urljoin(li.xpath(".//div[@class='nlcd_name']/a/@href").get())
            item['ori_url'] = url

            # 评论数
            comment_1 = li.xpath(".//span[@class='value_num']/text()").get()
            if comment_1:
                comment = str(comment_1).split('(')[1].split('条')[0]
            else:
                comment = comment_1
            item['comment'] = comment

            # 规格
            specs_list = li.xpath(".//div[contains(@class,'house_type')]//text()").getall()
            specs_list1 = list(map(lambda x: re.sub(r"\s", "", x), specs_list))
            specs = "|".join(list(filter(lambda x: x.endswith("居"), specs_list1)))
            item['specs'] = specs

            # 面积
            area = None
            if specs_list1:
                area = specs_list1[-1].replace('－', '')
            item['area'] = area

            # 地址
            address = li.xpath(".//div[@class='address']/a/@title").get()
            item['address'] = address

            # 是否在售
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            item['sale'] = sale

            # 价格
            price = ''.join(li.xpath(".//div[@class='nhouse_price']//text()").getall()).strip()
            item['price'] = price

            yield item

        # 下一页
        all_url = response.xpath("//div[@class='page']//li[@class='fr']")
        last_url = all_url.xpath("./a[position()=last()]/@href").get()
        this_url = response.request.url
        lens = len(this_url.split('b9'))
        if last_url and lens <= 1:
            a = last_url.split('b9')
            last_num = int(a[1].split('/')[0])
            if all_url and last_num >= 2:
                for i in range(2, last_num + 1):
                    i = str(i)
                    url = a[0] + 'b9' + i + '/'
                    yield scrapy.Request(url=response.urljoin(url), callback=self.parse_nh,
                                         meta={"info": (province, city)})

        # next_url_text = response.xpath \
        #     ("//div[@class='page']//li[@class='fr']/a[position()=last()-1]/text()").get()
        # next_url = response.xpath \
        #     ("//div[@class='page']//li[@class='fr']/a[position()=last()-1]/@href").get()
        #
        # if next_url:
        #     if '下一页' in next_url_text:
        #         yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_nh,
        #                              meta={"info": (province, city)})
        #     else:
        #         all_url = response.xpath("//div[@class='page']//li[@class='fr']")
        #         urls = all_url.xpath("./a[not(contains(@class,'f16'))]/@href").getall()
        #         for url in urls:
        #             yield scrapy.Request(url=response.urljoin(url), callback=self.parse_nh,
        #                                  meta={"info": (province, city)})

    def parse_sp(self, response):
        item = spItem()
        province, city = response.meta.get('info')
        item['province'] = province
        item['city'] = city
        dls = response.xpath("//div[contains(@class,'shop_list')]/dl")
        for dl in dls:
            name = dl.xpath(".//h4/a[1]/@title").get()
            item['name'] = name

            big_address = dl.xpath(".//p[contains(@class,'add_shop')]/a[1]/@title").get()
            item['big_address'] = big_address

            address = dl.xpath(".//p[contains(@class,'add_shop')]/span/text()").get()
            item['address'] = address

            all_text = ','.join(dl.xpath(".//p[@class='tel_shop']/text()").getall()).strip()\
                .replace('\n', '').replace('\t', '')
            single_text = all_text.split(',')
            if len(single_text) >= 3:
                if len(single_text[2].split(':')) > 1:
                    area = single_text[2].split(':')[1]
                    floor = single_text[1].split('：')[1]
                else:
                    area = single_text[2].split(':')[0]
                    floor = single_text[1].split('：')[0]
            else:
                area = None
                floor = None
            item['floor'] = floor
            item['area'] = area

            price = ''.join(dl.xpath(".//dd[@class='price_right']/span[1]//text()").getall())\
                .replace('\n', '').replace('\t', '')
            item['price'] = price

            yield item

        parrern = re.compile("(house/i3).*(末页)")
        urls = parrern.search(response.text)
        if urls:
            last_num = int(urls.group().split("/")[1].split("i3")[1])
            print(last_num)
            for i in range(2, last_num + 1):
                i = str(i)
                url = "/shou/house/i3" + i + '/'
                yield scrapy.Request(url=response.urljoin(url), callback=self.parse_sp,
                                     meta={"info": (province, city)}, dont_filter=False)

    def parse_zf(self, response):
        item = zfItem()
        province, city = response.meta.get('info')
        item['province'] = province
        item['city'] = city
        dls = response.xpath("//div[@class='houseList']/dl")
        for dl in dls:
            # 租房名字
            name = dl.xpath(".//dd[@class='info rel']/p[@class='title']/a/@title").get()
            item['name'] = name

            # 详情url
            ori_url = response.urljoin(dl.xpath(".//dd[@class='info rel']/p[1]/a/@href").get())
            item['ori_url'] = ori_url

            # env情况
            env = dl.xpath(".//dd[@class='info rel']/p[2]/text()").getall()

            # 合租情况
            rental = None
            if len(env) >= 1:
                rental = env[0].strip()
            item['rental'] = rental

            # 几户
            households = None
            if len(env) >= 2:
                households = env[1].strip()
            item['households'] = households

            # 面积
            area = None
            if len(env) >= 3:
                area = env[2].strip()
            item['area'] = area

            # 朝向
            toward = None
            if len(env) >= 4:
                toward = env[3].strip()
            item['toward'] = toward

            # 地址
            # address = str(''.join(dl.xpath(".//dd[@class='info rel']/p//text()").getall()).strip().replace('\n', '').replace(' ', ''))
            address = ''.join(dl.xpath(".//dd[@class='info rel']/p[3]//text()").getall())
            item['address'] = address

            # 价格
            price = ''.join(dl.xpath(".//div[@class='moreInfo']/p//text()").getall())
            item['price'] = price

            yield item
            # 下一页
        last_url = response.xpath("//div[@class='fanye']/a[position()=last()]/@href").get()
        all_a = response.xpath("//div[@class='fanye']/a")
        this_url = response.request.url
        lens = len(this_url.split('i3'))
        if last_url and lens <= 1:
            a = last_url.split('i3')
            a_len = len(a)
            if a_len >= 2:
                last_num = int(a[1].split('/')[0])
                if all_a and last_num >= 4:
                    for i in range(2, last_num + 1):
                        i = str(i)
                        url = a[0] + 'i3' + i + '/'
                        yield scrapy.Request(url=response.urljoin(url), callback=self.parse_zf,
                                             meta={"info": (province, city)})
