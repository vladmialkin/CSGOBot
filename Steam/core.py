import requests
import bs4
import lxml
# # steam_market = requests.get('https://steamcommunity.com/market/search?q=')
steam_market = requests.get('https://steamcommunity.com/market/search/render/?query=&start=0&count=1000&search_descriptions=0&sort_column=popular&sort_dir=desc')
steam_market = steam_market.json()
html = bs4.BeautifulSoup(steam_market['results_html'], 'html.parser')
# print(html.find_all('span', class_='normal_price'))

