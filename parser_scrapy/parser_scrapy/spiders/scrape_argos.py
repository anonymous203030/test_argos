import json

import scrapy


class ScrapeArgosSpider(scrapy.Spider):
    name = "scrape_argos"
    allowed_domains = ["www.argos.co.uk"]
    start_urls = ["https://www.argos.co.uk"]

    def parse(self, response):

        # Parsing category list with class name
        cat_list = response.css("._39ydj a::attr(href)").extract()

        # Follow each category link
        for _ in cat_list:
            link = f"{self.start_urls[0]}{_}"
            yield response.follow(link, callback=self.parse_category)

    # Each category parser
    def parse_category(self, response):
        for link in response.css('.M052styles__Link-sc-1cubg5c-7.dtlHvb::attr(href)').extract():
            yield response.follow(link, callback=self.switch_page)

    def switch_page(self, response):
        # find the last page
        page = response.css('.Paginationstyles__PageLink-sc-1temk9l-1.ifyeGc.xs-hidden.sm-row::attr(href)').get()
        self.parse_product(response)

        p_spl = page.split('/')
        try:
            if p_spl[len(p_spl) - 2].find('page:') != -1:
                response.follow(f'https://www.argos.co.uk{page}')
            else:
                yield 'The data has been parsed.'
        except Exception as e:
            yield 'The data has been parsed.'

    def parse_product(self, response):
        product_info = {
            'Product Url': None,
            'Price': None,
            'Title/Name': None,
            'Color': None,
        }
        products = response.css(
            '.ProductCardstyles__Wrapper-h52kot-1.dWoMVd.StyledProductCard-sc-1o1topz-0.fOIrbR')

        for pr in products:
            product_info['Product Url'] = pr.css('.ProductCardstyles__Link-h52kot-13.cnmosm::attr(href)').get()
            product_info['Price'] = pr.css('.ProductCardstyles__PriceText-h52kot-16.Lynud::text').get()
            product_info['Title/Name'] = pr.css('.ProductCardstyles__Title-h52kot-12 PQnCV::text').get()

        with open('output.txt', 'w') as f:
            f.write(json.dumps(product_info))