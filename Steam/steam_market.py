import requests
import bs4
import time, datetime
import json
import re


class SteamMarket:
    def __init__(self):
        self.START_ITEM_INDEX = 0
        self.COUNT = 20
        self.CURRENCY_RUB = None
        self.html_site = None
        self.get_currency_rub()
        self.event()
        # self.get_top_list()

    def get_currency_rub(self):
        """функция находит курс рубля для доллара в стим"""
        url = requests.get('https://api.steam-currency.ru/currency')
        url = url.json()
        self.CURRENCY_RUB = float(url['data'][0]['close_price'])

    def get_site(self):
        try:
            steam_market = requests.get(
                f'https://steamcommunity.com/market/search/render/?query=&start={self.START_ITEM_INDEX}&count={self.COUNT}&search_descriptions=0&sort_column=popular&sort_dir=desc&appid=730')
            steam_market = steam_market.json()
            self.html_site = bs4.BeautifulSoup(steam_market['results_html'], 'html.parser')
            self.START_ITEM_INDEX += 20
        except (TypeError, AttributeError):
            print(f'Стим не хочет пускать, выполняю повторный запрос.')
            time.sleep(60)
            self.get_site()

    def get_items(self):
        """функция получает 100 предметов и возвращает их имя, стоимость, ссылку стим"""
        items = []
        # names = self.html_site.find_all(
        #     'div', class_="market_listing_row market_recent_listing_row market_listing_searchresult")
        #
        # prices = self.html_site.find_all('span', class_='normal_price')

        for index in range(self.COUNT):
            item_container = self.html_site.find("div", id=f"result_{index}")
            name = item_container.find('span', id=f"result_{index}_name").string
            price = item_container.find('div', class_="market_listing_right_cell market_listing_their_price").contents[1].contents[3].string
            url = f'https://steamcommunity.com/market/listings/730/{str(name.replace(" ", "%20").replace("|", "%7C"))}'
            item = {'name': name, "price": round(float(price[1:-4]) * self.CURRENCY_RUB, 2), "url": url}
            print(item)
            self.get_data_item(item)
            items.append(item)
        return items

    def event(self):
        items = []
        while True:
            self.get_site()
            self.get_items()
            # item = self.get_items()
            # items += item
            time.sleep(2)

    def get_data_item(self, item):
        """функция получает данные с сайта маркета стим (НЕ ДОРАБОТАН)"""
        site = requests.get(item['url'])

        steam_graph = re.search(r'var line1=(.+);', site.text)
        steam_graph = steam_graph.group(1)

        values_graph = json.loads(steam_graph)
        prices = []
        date = datetime.datetime.strptime(values_graph[-1][0][:-4], "%b %d %Y %H") - datetime.timedelta(days=30)
        for values in values_graph:
            values[0] = datetime.datetime.strptime(values[0][:-4], "%b %d %Y %H")
            values[1] = round(float(values[1]) * self.CURRENCY_RUB, 2)
            if values[0] >= date:
                print(values)

    def get_top_list(self):
        steam_market = requests.get(
            f'https://steamcommunity.com/market/search?appid=730#p5_popular_desc')
        self.html_site = bs4.BeautifulSoup(steam_market.text, 'html.parser')
        print(self.html_site.find_all('div', id='searchResultsRows'))


steam = SteamMarket()





