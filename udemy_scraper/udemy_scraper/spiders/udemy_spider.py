import scrapy
import json

class UdemySpider(scrapy.Spider):
    name = "udemy"
    allowed_domains = ["www.udemy.com"]
    start_urls = [
        "https://www.udemy.com/api-2.0/courses/?page=1&page_size=10&language=fr&ordering=relevance"
    ]

    def parse(self, response):
        data = json.loads(response.text)
        courses = data.get("results", [])

        for course in courses:
            yield {
                "Titre": course.get("title", "N/A"),
                "Prix": course.get("price", "N/A"),
                "URL": f"https://www.udemy.com/course/{course.get('url', '')}",
                "Catégorie": course.get("visible_instructors", [{}])[0].get("job_title", "N/A")
            }

        # Pagination : récupérer la page suivante
        next_page = data.get("next")
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
