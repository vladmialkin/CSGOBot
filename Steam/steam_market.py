import requests
import bs4
import time, datetime
import json
import re


class SteamMarket:
    def __init__(self):
        self.START_ITEM_INDEX = 0
        self.CURRENCY_RUB = None
        self.html_site = None
        self.get_currency_rub()
        self.event()
        # self.get_data_item()

    def get_currency_rub(self):
        """функция находит курс рубля для доллара в стим"""
        url = requests.get('https://api.steam-currency.ru/currency')
        url = url.json()
        self.CURRENCY_RUB = float(url['data'][0]['close_price'])

    def get_site(self):
        try:
            steam_market = requests.get(
                f'https://steamcommunity.com/market/search/render/?query=&start={self.START_ITEM_INDEX}&count=100&search_descriptions=0&sort_column=popular&sort_dir=desc')
            steam_market = steam_market.json()
            self.html_site = bs4.BeautifulSoup(steam_market['results_html'], 'html.parser')
            self.START_ITEM_INDEX += 100
        except (TypeError, AttributeError):
            print(f'Стим не хочет пускать, выполняю повторный запрос.')
            time.sleep(60)
            self.get_site()

    def get_items(self):
        """функция получает 100 предметов и возвращает их имя, стоимость, ссылку стим"""
        items = []
        names = self.html_site.find_all(
            'div', class_="market_listing_row market_recent_listing_row market_listing_searchresult")

        prices = self.html_site.find_all('span', class_='normal_price')
        for values in zip(names, prices):
            name = values[0].contents[5].contents[1].string
            url = f'https://steamcommunity.com/market/listings/730/{str(name.replace(" ", "%20").replace("|", "%7C"))}'
            try:
                price = values[1].contents[3].string
            except IndexError:
                """При получении тега с ценой может попасться пустой тег.
                При появлении этого тега возникает ошибка, при которой цикл продолжает работу"""
                continue
            item = {'name': name, "price": round(float(price[1:-4])*self.CURRENCY_RUB,2), "url": url}
            print(item)
            self.get_data_item(item)
            items.append(item)
        return items

    def event(self):
        items = []
        while True:
            self.get_site()
            item = self.get_items()
            items += item
            time.sleep(2)

    def get_data_item(self, item):
        """функция получает данные с сайта маркета стим (НЕ ДОРАБОТАН)"""
        # https://steamcommunity.com/market/listings/730/Revolution%20Case
        # item = {'name': 'Sticker | FURIA (Holo) | Paris 2023', 'price': 142.98,
        #         'url': 'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20FURIA%20(Holo)%20%7C%20Paris%202023'}
        # sess = requests.Session()
        # url = sess.post(item['url'])
        # item_site = bs4.BeautifulSoup(url.text, 'html.parser')
        # item_site = item_site.find('body')
        # scripts = item_site.find_all('script')

        site = requests.get(item['url'])

        steam_graph = re.search(r'var line1=(.+);', site.text)
        steam_graph = steam_graph.group(1)

        values_graph = json.loads(steam_graph)
        prices = []
        for values in values_graph:
            # print(round(float(value[1])*self.CURRENCY_RUB, 2))
            values[0] = datetime.datetime.strptime(values[0][:-7], "%b %d %Y")
            values[1] = round(float(values[1]) * self.CURRENCY_RUB, 2)
            if values[0] >= datetime.datetime.strptime('2023-06-01', "%Y-%m-%d"):
                print(values)


steam = SteamMarket()





