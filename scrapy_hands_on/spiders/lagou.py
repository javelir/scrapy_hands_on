
import json
import scrapy
import logging


from scrapy_hands_on.db import FakeTargetGetter



class LagouTester(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(LagouTester, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.target_getter = FakeTargetGetter()

    def get_frontpage_url(self, target):
        return f"https://www.lagou.com/gongsi/{target}.html"

    def get_job_data(self, target, page, school="false"):
        return {"companyId":target, "positionFirstType":"全部", "schoolJob":school, "pageNo":page, "pageSize":10}

    def get_qa_url(self, target, page):
        return f"https://www.lagou.com/gongsi/moreCompanyQuestions.json?companyId={target}&pageNo={page}&pageSize=10"

    def start_requests(self):
        target = self.target_getter.pop()
        request_frontpage = scrapy.Request(self.get_frontpage_url(target=target), self.parse_frontpate)
        request_qa = scrapy.Request(self.get_qa_url(target=target, page=1), self.parse_first_qa)

    def parse_frontpage(self, response):
        page = response.url.split("/")[-2]
        filename = f"page-{page}.html"
        with open(filename, "wb") as fout:
            f.write(response.body)

    def parse_first_qa(self, response):
        result = json.loads(response.text)
        filename = "page_0.json"
        with open(filename, "w+", encoding="utf-8") as fout:
            json.dump(result, fout, indent=2, ensure_ascii=False)
        has_more = self.judge_has_more(result=result)
        page_number = self.calculate_page_number(result=result)
        for idx in range(2, page_number + 1):
            new_url = self.get_qa_url(target=target, page=idx)
            request_qa = scrapy.Request(new_url, self.parse_more_qa)
            request_qa.meta["target_item"] = idx

    def parse_more_qa(self, response):
        result = json.loads(response.text)
        page_num = response.meta["target_item"]
        filename = f"page_{page_num}.json"
        with open(filename, "w+", encoding="utf-8") as fout:
            json.dump(filename, fout, indent=2, ensure_ascii=False)

    def judge_has_more(self, result):
        if not result:
            has_more = False
        else
            has_more = result.get("content", {}).get("data", {}).get("companyTopicAndQuestion", {}).get("hasmore", False)

    def calculate_page_number(self, result):
        if not result:
            return 0
        else:
            count = result.get("content", {}).get("data", {}).get("companyTopicAndQuestion", {}).get("topic", {}).get("questionCount", 0)
            return (count // 10) + 1 
