import requests
import bs4
import time
import datetime
import json
import re


class SteamMarket:
    def __init__(self):
        self.START_ITEM_INDEX = 0
        self.COUNT = 50
        self.CURRENCY_RUB = None
        self.html_site = None
        self.BLACK_LIST = 'Paris 2023'
        self.get_currency_rub()
        self.event()

    def get_currency_rub(self):
        """функция находит курс рубля для доллара в стим"""
        url = requests.get('https://api.steam-currency.ru/currency')
        url = url.json()
        self.CURRENCY_RUB = float(url['data'][0]['close_price'])

    def get_site(self):
        try:
            steam_market = requests.get(
                f'https://steamcommunity.com/market/search/render/?query=&start={self.START_ITEM_INDEX}&count={self.COUNT}&search_descriptions=0&sort_column=popular&sort_dir=desc&appid=730',)
            steam_market = steam_market.json()
            self.html_site = bs4.BeautifulSoup(steam_market['results_html'], 'html.parser')
            self.START_ITEM_INDEX += self.COUNT
        except (TypeError, AttributeError):
            print(f'Стим не хочет пускать, выполняю повторный запрос.')
            time.sleep(60)
            self.get_site()

    def get_items(self):
        """функция получает 100 предметов и возвращает их имя, стоимость, ссылку стим"""
        items = []
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
            if self.START_ITEM_INDEX != 200:
                self.get_site()
                item = self.get_items()
                items += item
                print(f'--------------Предметов {self.START_ITEM_INDEX}----------------')
            else:
                self.START_ITEM_INDEX = 0

    def get_data_item(self, item):
        """функция получает данные с сайта маркета стим (НЕ ДОРАБОТАН)"""
        try:
            site = requests.get(item['url'])
            steam_graph_sell = re.search(r'var line1=(.+);', site.text)
            steam_graph_buy = re.search(r'var line2=(.+);', site.text)
            steam_graph_sell = steam_graph_sell.group(1)
            steam_graph_buy = steam_graph_buy.group(1)

            values_buy_graph = json.loads(steam_graph_buy)
            values_sell_graph = json.loads(steam_graph_sell)

            month_date = datetime.datetime.strptime(values_buy_graph[-1][0][:-4], "%b %d %Y %H") - datetime.timedelta(
                days=30)
            week_date = datetime.datetime.strptime(values_buy_graph[-1][0][:-4], "%b %d %Y %H") - datetime.timedelta(days=7)
            day_date = datetime.datetime.strptime(values_buy_graph[-1][0][:-4], "%b %d %Y %H") - datetime.timedelta(days=1)
            hour_date = datetime.datetime.strptime(values_buy_graph[-1][0][:-4], "%b %d %Y %H") - datetime.timedelta(
                hours=1)

            month_max_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            month_min_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            weekly_max_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            weekly_min_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            day_max_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            day_min_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            hour_min_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            hour_max_price = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)

            last_price = round(float(values_buy_graph[len(values_buy_graph) - 2][1]) * self.CURRENCY_RUB, 2)
            current_price = round(float(values_buy_graph[len(values_buy_graph) - 1][1]) * self.CURRENCY_RUB, 2)
            first_order_buy = round(float(values_buy_graph[-1][1]) * self.CURRENCY_RUB, 2)
            first_order_sell = round(float(values_sell_graph[-1][1]) * self.CURRENCY_RUB, 2)
            print(last_price, current_price)
            print(f"Первый ордер на покупку по цене {first_order_buy}")
            print(f"Первый ордер на продажу по цене {first_order_sell}")
            print(f"Выгода {(first_order_buy - first_order_sell) / 1.15}")
            for values in values_buy_graph:
                values[0] = datetime.datetime.strptime(values[0][:-4], "%b %d %Y %H")
                values[1] = round(float(values[1]) * self.CURRENCY_RUB, 2)

                if values[0] >= month_date:
                    if month_min_price > values[1]:
                        month_min_price = values[1]
                    if month_max_price < values[1]:
                        month_max_price = values[1]
                if values[0] >= week_date:
                    if weekly_min_price > values[1]:
                        weekly_min_price = values[1]
                    if weekly_max_price < values[1]:
                        weekly_max_price = values[1]
                if values[0] >= day_date:
                    if day_min_price > values[1]:
                        day_min_price = values[1]
                    if day_max_price < values[1]:
                        day_max_price = values[1]
                if values[0] >= hour_date:
                    if hour_min_price > values[1]:
                        hour_min_price = values[1]
                    if hour_max_price < values[1]:
                        hour_max_price = values[1]
            if (month_max_price > month_min_price * 2) or (weekly_max_price > weekly_min_price * 2) or (
                    day_max_price > day_min_price * 2) or (hour_max_price > hour_min_price * 2):
                if item['name'].find(self.BLACK_LIST) == -1:
                    print(f"Минимальная цена за месяц {month_min_price}")
                    print(f"Максимальная цена за месяц {month_max_price}")
                    print(f"Минимальная цена за неделю {weekly_min_price}")
                    print(f"Максимальная цена за неделю {weekly_max_price}")
                    print(f"Минимальная цена за день {day_min_price}")
                    print(f"Максимальная цена за день {day_max_price}")
                    print(f"Минимальная цена за час {hour_min_price}")
                    print(f"Максимальная цена за час {hour_max_price}")




        except (TypeError, AttributeError):
            print(f'Стим не хочет пускать, выполняю повторный запрос.')
            time.sleep(120)
            self.get_data_item(item)
