import scrapy

class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    max_items = 100

    def parse(self, response):
        if response.status != 200:
            self.logger.error(f"Erreur {response.status} - Impossible d'accéder à {response.url}")
            return

        scraped_count = self.crawler.stats.get_value("item_scraped_count", 0)
        if scraped_count >= self.max_items:
            self.logger.info(f"✅ Limite atteinte ({self.max_items} éléments), arrêt du scraping.")
            return

        for book in response.css("article.product_pod"):
            scraped_count = self.crawler.stats.get_value("item_scraped_count", 0)
            if scraped_count >= self.max_items:
                return

            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css("p.price_color::text").get(),
                "availability": "".join(book.css("p.instock.availability::text").getall()).strip(),
                "rating": book.css("p.star-rating::attr(class)").get().split()[-1],  # Extrait "Three", "Four", etc.
            }

        scraped_count = self.crawler.stats.get_value("item_scraped_count", 0)
        if scraped_count >= self.max_items:
            self.logger.info(f"Limite atteinte ({self.max_items} éléments), arrêt du scraping.")
            return

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
