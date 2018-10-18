
import json
import scrapy
import logging


from scrapy_hands_on.db import FakeTargetGetter
from scrapy_hands_on.utils import HEADERS



class LagouTester(scrapy.Spider):
    name = "lagou"

    def __init__(self, *args, **kwargs):
        super(LagouTester, self).__init__(*args, **kwargs)
        self.target_getter = FakeTargetGetter()
    #@property
    #def logger(self):
    #    return logging.getLogger(__name__)

    def get_frontpage_url(self, target):
        return f"https://www.lagou.com/gongsi/{target}.html"

    def get_job_data(self, target, page, school="false"):
        return {"companyId":target, "positionFirstType":"全部", "schoolJob":school, "pageNo":page, "pageSize":10}

    def get_qa_url(self, target, page):
        return f"https://www.lagou.com/gongsi/moreCompanyQuestions.json?companyId={target}&pageNo={page}&pageSize=10"

    def start_requests(self):
        target = self.target_getter.pop()
        #request_frontpage = scrapy.Request(self.get_frontpage_url(target=target), self.parse_frontpage, headers=HEADERS)
        #request_frontpage["target_corp"] = target
        #yield request_frontpage
        request_qa = scrapy.Request(self.get_qa_url(target=target, page=1), self.parse_first_qa, headers=HEADERS)
        request_qa.meta["target_corp"] = target
        yield request_qa

    def parse_frontpage(self, response):
        page = response.url.split("/")[-2]
        filename = f"./data/page_{page}.html"
        with open(filename, "wb") as fout:
            fout.write(response.body)

    def parse_first_qa(self, response):
        target_corp = response.meta["target_corp"]
        result = json.loads(response.text)
        filename = "./data/page_1.json"
        with open(filename, "w+", encoding="utf-8") as fout:
            json.dump(result, fout, indent=2, ensure_ascii=False)
        has_more = self.judge_has_more(result=result)
        page_number = self.calculate_page_number(result=result)
        for idx in range(2, page_number + 1):
            new_url = self.get_qa_url(target=target_corp, page=idx)
            request_qa = scrapy.Request(new_url, self.parse_more_qa, headers=HEADERS)
            request_qa.meta["target_item"] = idx
            yield request_qa

    def parse_more_qa(self, response):
        result = json.loads(response.text)
        page_num = response.meta["target_item"]
        filename = f"./data/page_{page_num}.json"
        with open(filename, "w+", encoding="utf-8") as fout:
            json.dump(result, fout, indent=2, ensure_ascii=False)

    def judge_has_more(self, result):
        if not result:
            has_more = False
        else:
            has_more = result.get("content", {}).get("data", {}).get("companyTopicAndQuestion", {}).get("hasmore", False)

    def calculate_page_number(self, result):
        if not result:
            return 0
        else:
            count_str = result.get("content", {}).get("data", {}).get("companyTopicAndQuestion", {}).get("topic", {}).get("questionCount", 0)
            return (int(count_str) // 10) + 1 
