import scrapy


# TODO: Clear output file, do not append
class MtggoldfishSpider(scrapy.Spider):
    name = "mtggoldfish"
    base_url = "https://mtggoldfish.com"
    # TODO: dynamic format?
    format = "modern"
    ignored_cards = {"plains", "island", "swamp", "mountain", "forest"}

    def __init__(self, *args, **kwargs):
        # TODO: Dynamic date
        url = "{base_url}/tournament_searches/create?tournament_search[format]={format}&tournament_search[date_range]=12/01/2021+-+01/31/2022&commit=Search".format(
            base_url=self.base_url,
            format=self.format,
        )
        self.start_urls = [url]
        super(MtggoldfishSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # Tournaments
        self.logger.info("Parsing tourney list")
        tourney_urls = response.css("table.table-striped tr td a::attr(href)").getall()
        for relative_url in tourney_urls:
            absolute_url = "{base_url}/{relative_url}".format(
                base_url=self.base_url, relative_url=relative_url
            )
            yield scrapy.Request(absolute_url, callback=self.parse_tourney)

        # Pagination
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            self.logger.info("Yield new page")
            yield scrapy.Request("{base_url}{next_page}".format(base_url=self.base_url, next_page=next_page))

    def parse_tourney(self, response):
        self.logger.info("Parsing tourney")
        decklist_pages = response.css(
            '.table-tournament a[href^="/deck"]::attr(href)'
        ).getall()
        deck_ids = [url.split("/")[2] for url in decklist_pages]
        for id in deck_ids:
            decklist_url = "{base_url}/deck/download/{id}".format(
                base_url=self.base_url, id=id
            )
            yield scrapy.Request(decklist_url, callback=self.parse_decklist)

    def parse_decklist(self, response):
        self.logger.info("Parsing decklist")
        cardlist = response.text.splitlines()
        cards = {}

        for card_data in cardlist:
            boom = card_data.split(" ")
            if len(boom) < 2:
                continue
            num = int(boom[0])
            card_name = " ".join(boom[1:])

            if card_name.lower() in self.ignored_cards:
                continue

            if card_name in cards:
                cards[card_name] += num
            else:
                cards[card_name] = num

        yield cards
