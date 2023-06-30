import requests
import bs4
import time


def create_url(count):
    steam_market = requests.get(f'https://steamcommunity.com/market/search?appid=730#p2_popular_desc')
    html = bs4.BeautifulSoup(steam_market.text, 'html.parser')
    return html

# [('Dreams & Nightmares Case', '$1.26 USD'), ('Revolution Case', '$1.41 USD'), ('Fracture Case', '$0.61 USD'), ('Recoil Case', '$0.62 USD'), ('Snakebite Case', '$0.37 USD'), ('Clutch Case', '$0.89 USD'), ('Glove Case', '$5.22 USD'), ('Operation Breakout Weapon Case', '$6.27 USD'), ('Gamma 2 Case', '$2.37 USD'), ('Chroma 3 Case', '$2.33 USD')]
def get_items(site):
    list = []
    names = site.find_all(class_="market_listing_item_name_block")
    prices = site.find_all(class_="market_table_value normal_price")
    for name, price in zip(names, prices):
        tag_name = name.find(class_='market_listing_item_name').string
        tag_price = price.find('span', class_='normal_price').string
        list.append((tag_name, tag_price))
    return list


def main():
    count = 1
    for index in range(2000):
        if count != 2000:
            time.sleep(2)
            html = create_url(count)
            items = get_items(site=html)
            print(items)
            count += 1
        else:
            count = 1


if __name__ == "__main__":
    main()