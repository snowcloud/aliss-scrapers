# spider for old Grampian Care Data site
# Derek Hoy for ALISS.org
# 
# cd aliss
# scrapy crawl gcd --set FEED_URI=items.json --set FEED_FORMAT=json

import re
import urllib2

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from BeautifulSoup import BeautifulSoup

# http://soupselect.googlecode.com/svn/trunk/soupselect.py
# svn checkout http://soupselect.googlecode.com/svn/trunk/
# mv to libs, add libs to pythonpath
from soupselect import select as css

from aliss.items import GCDItem

class GCDSpider(BaseSpider):
    """
    This scrapes the old (live) GCD site, not the new development site.
    It should really read the URL for each entry on the page, then scrape the individual entry page for the full data.
    List pages don't show 'category' data we need for tags.
    
    for each page of 1658/25:
        for each item of 25:
            get URL
            scrape URL to item
        
    """
    name = "gcd"
    allowed_domains = ["grampiancaredata.gov.uk"]
    URL_TEMPLATE = "http://www.grampiancaredata.gov.uk/development/keyword-search/?tx_evgcdsearch_pi1%%5Breport%%5D=gcd_search&tx_evgcdsearch_pi1%%5Bstart%%5D=%d"
    max_result = 2 # 1658
    start_urls = [URL_TEMPLATE % n for n in xrange(1, max_result, 25)]

    def extract_span_heading(self, node, heading):
        """
        GCD pages have data as eg 
        <p><span class="bold">heading:</span>some text</p>
        
        can be p or div
        
        """
        result = None
        h = css(node, 'span.bold')
        if h and (str(h[0].contents[0].strip()) == heading):
            if len(node.contents) > 1:
                result = str(node.contents[1]).strip()
        return result
        
        
    def soup_parse(self, listitem):
        title = ident = web = short_address = area = phone = lat = lng = None
        tags = []

        t = css(listitem, 'h1 a')
        if t:
            title = t[0].contents[0]
            ident = t[0]['href']

        """
        this could look for span class=bold, extract heading, get content as next sibling
        
        """
        t = css(listitem, '.tel-fax .record-detail')
        if t:
            phone = t[0].contents[1].strip()

        t = css(listitem, '.web a[href^=http]')
        if t:
            web = t[0]['href']

        t = css(listitem, '.p-code .record-detail')
        if t:
            short_address = str(t[0].contents[1]).strip()

        t = css(listitem, '.p-code p')
        if t:    
            area = self.extract_span_heading(t[0], 'Area Covered:')

        item = {
            'title': title,
            # 'lat': lat,
            # 'lng': lng,
            'url': web,
            # 'phone': phone,
            'short_address': short_address,
            'area': area,
            # 'tags': tags,
            # 'origin': ident
        }
        return GCDItem(**item)

    def parse(self, response):
        html = response.body
        html = html.replace('<!- Google Analytics -->', '')
        html = re.sub('<script.*?>[\s\S]*?</.*?script>', '', html)
        soup = BeautifulSoup(html)
        items = []
        for listitem in css(soup, '.search-row-grey-wrapper'):
            items.append(self.soup_parse(listitem))
        for listitem in css(soup, '.search-row-white-wrapper'):
            items.append(self.soup_parse(listitem))
        return items
        
    
    # def parse_xpath(self, response):
    #     hxs = HtmlXPathSelector(response)
    #     items = []
    #     entries = hxs.select('//div[contains(@class, "search-row-grey-wrapper")]')
    #     for entry in entries:
    #         item = GCDItem()
    #         content = entry.select('.//div[contains(@class, "search-row-left-content")]')[0]
    #         item['title'] = ' '.join(content.select('.//h1/a/text()').extract())
    #         item['url'] = ' '.join(content.select('.//h1/a/@href').extract())
    #         item['description'] = ' '.join(content.select('.//p').extract())
    #         items.append(item)
    #         # print '---\n', item['title'], item['url'], item['description']
    #     entries = hxs.select('//div[contains(@class, "search-row-white-wrapper")]')
    #     for entry in entries:
    #         item = GCDItem()
    #         content = entry.select('.//div[contains(@class, "search-row-left-content")]')[0]
    #         item['title'] = ' '.join(content.select('.//h1/a/text()').extract())
    #         item['url'] = ' '.join(content.select('.//h1/a/@href').extract())
    #         item['description'] = ' '.join(content.select('.//p').extract())
    #         items.append(item)
    #         # print '---\n', item['title'], item['url'], item['description']
    #     return items
            
