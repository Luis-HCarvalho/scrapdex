import pandas as pd
import scrapy
from scrapdex.enums.data_type import DType

class Scrapdex(scrapy.Spider):
    name = "scrapdex"
    domain = "https://pokemondb.net"
    start_urls = ["https://pokemondb.net/pokedex/all"]
    pokemon_page = ""
    json = { }

    def __init__(self, index=None, *args, **kwargs):
        self.index = int(index)

    def parse(self, response):
        pokemons = response.css('#pokedex > tbody > tr')
        # length = len(pokemons)
        length = self.index + 1
        if self.index < length:
            for pokemon in pokemons[self.index:self.index + 1]:
                self.index += 1
                link = pokemon.css("td.cell-name > a::attr(href)").extract_first()
                self.pokemon_page = self.domain + link
                yield scrapy.Request(self.pokemon_page, callback=self.parse_pokemon, meta={ "len": length})
        else:
            self.index = None
            return None

    def parse_pokemon(self, response):
        number = response.css("table.vitals-table > tbody > tr:nth-child(1) > td > strong::text").get()
        item =  {
            "number": number,
            "page_url": self.pokemon_page,
            'pokemon_name': response.css('main#main > h1::text').get(),
            'evolution_chart': self._evolution_chart(response, number),
            'height': response.css('.vitals-table > tbody > tr:nth-child(4) > td::text').get().split("(")[0].replace("\u00a0", " "),
            'weight': response.css('.vitals-table > tbody > tr:nth-child(5) > td::text').get().split("(")[0].replace("\u00a0", " "),
            "type": response.css('.vitals-table > tbody > tr:nth-child(2) > td > a.type-icon::text').extract(),
            "dtype": DType.POKEMON,
            "index_len": (self.index, response.meta["len"])
        }
        
        moves = response.css("#tab-moves-21.active tbody tr")
        for m in moves[:1]:
            tmp = {}
            tmp["number"] = item["number"]
            tmp["name"] = m.css("td.cell-name > a.ent-name::text").get()
            link = f"{self.domain}{m.css("td.cell-name > a.ent-name::attr(href)").get()}"
            tmp["url"] = link
            yield scrapy.Request(link, callback=self.mv_description, meta=tmp)

        yield item
        
    def mv_description(self, res):
        yield {
            # "pokemon_number": res.meta["number"],
            "dtype": DType.MOVE,
            "name": res.meta["name"],
            "url": res.meta["url"],
            "description": res.css("div.grid-row > div.span-md-8 > p::text").get()
        }

    def _evolution_chart(self, response, pokemon_number):
        # path = "#main  div.infocard-list-evo div.infocard span.infocard-lg-data"
        evolists = response.css("#main  > div.infocard-list-evo")
        print()
        print()
        print(dir(evolists))
        print()
        print(evolists.extract())
        e = "#main  div.infocard-list-evo"

        list_evo = "div.infocard-list-evo"
        evo_split = "span.infocard-evo-split"
        p1 = "#main  div.infocard-list-evo > div.infocard"
        p2 = "#main  div.infocard-list-evo > span.infocard-evo-split"
        p3 = "#main  div.infocard-list-evo" # get how many

        initial = f"#main > {list_evo} > div.infocard:first-child"

        evo_lists = len(response.css("#main  div.infocard-list-evo").getall())
        evo_splits = len(response.css("#main div.infocard-list-evo span.infocard-evo-split").getall())
        path_all = "#main div.infocard-list-evo div.infocard span.infocard-lg-data"

        chain = []
        next_evos = []

        if  evo_splits > 0:
            numbers = response.css(f"{path_all} small:first-child::text").getall()
            names = response.css(f"{path_all} a.ent-name::text").getall()
            urls = response.css(f"{path_all} a.ent-name::attr(href)").getall()


        else:
            numbers = response.css(f"{path_all} small:first-child::text").getall()
            names = response.css(f"{path_all} a.ent-name::text").getall()
            urls = response.css(f"{path_all} a.ent-name::attr(href)").getall()

            i = 0
            for j, n in enumerate(numbers):
                if n[1:] == pokemon_number:
                    i = j + 1
                    break

            if i < len(numbers):
                for j in range(i, len(numbers)):
                    next_evos.append({
                        "number": numbers[j],
                        "name": names[j],
                        "url": f"{self.domain}{urls[j]}"
                    })
        
        return next_evos