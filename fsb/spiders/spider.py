import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FsbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FsbSpider(scrapy.Spider):
	name = 'fsb'
	start_urls = ['https://www.firstservicebank.com/news?page=1']

	def parse(self, response):
		post_links = response.xpath('//div[@class="col-md-4 col-sm-12 news-post"]/a[@class="btn btn-primary"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//ul[@class="pager"]/li/a[@rel="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		try:
			date = response.xpath('//h5[@class="postdate"]/text()').get()
			date = re.findall(r'\w+\s\d+\,\s\d+',date)
		except TypeError:
			date = response.xpath('//span[@class="dateline rs_skip"]/text()').get()
			date = re.findall(r'\d+\/\d+\/\d+', date)
		title = response.xpath('//div[@class="col-md-12 col-sm-12 news-post detail"]/h1/text() | //div[@class="col-md-7 col-sm-12 news-post detail"]/h1 | //span[@style="line-height: 1.1; font-weight: bold;"]/text()').get()
		if not title:
			title = response.xpath('//h1[@class="bulletin_subject"]/text()').get()
		content = response.xpath('//div[@class="post-body"]//text() | //table[@class="gd_combo_table"]/tbody//text()').getall()
		if not content:
			content = response.xpath('//div[@class="bulletin_body"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FsbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
