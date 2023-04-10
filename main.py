""" 
1. Получить html-code страницы
2. Получить карточки с товаром из html-кода
3. Распарсить данные из карточек
4. Полученные данные записать в файл (json, csv)
"""
import json
import csv

import requests

from bs4 import BeautifulSoup as BS
from bs4 import Tag, ResultSet

URL = 'https://www.sulpak.kg/'


def get_html(url: str, category: str, params: str='') -> str:
    
    html = requests.get(
        url + 'f/' + category,
        params=params,
        verify=False
    )
    if html.status_code == 200:
        return html.text
    elif html.status_code == 404:
        raise Exception('wrong url')
    else: 
        raise Exception('dont response')
        


def get_cards_from_html(html:str) -> ResultSet:
    soup = BS(html, 'lxml')
    cards = soup.find_all('div', {'class': 'product__item product__item-js tile-container'})
    return cards


def parse_data_from_cards(cards: ResultSet[Tag]) -> list[dict]:
    result = []
    card: Tag
    for card in cards:
        try:
            in_stock = card.find('div', {'class': 'product__item-showcase'}).text
        except AttributeError:
            in_stock = 'Нет в наличии'
        product = {
            'title': card.get('data-name'),
            'price': card.get('data-price'),
            'brand': card.get('data-brand'),
            'in_stock': in_stock,
            'product_link': URL[:-1] + card.find('div', {'class': 'product__item-name'}).find('a').get('href')
        }
        result.append(product)
    return result

def write_to_json(data: list, category: str) -> None:
    with open(f'{category}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_last_page(category):
    html = get_html(URL, category)
    soup = BS(html, 'lxml')
    last_page = soup.find('div', {'class': 'pagination'}).get('data-pagescount')
    return int(last_page)

def paginated_parse(category: str, page_num:int=None) -> list:
    if page_num:
        last_page = page_num
    else:
        last_page = get_last_page(category)
    result = []
    for page in range(last_page+1):
        html = get_html(URL, category, params=f'page={page}')
        cards = get_cards_from_html(html)
        data = parse_data_from_cards(cards)
        result.extend(data)
    return result


def main(category):
    data = paginated_parse(category)
    write_to_json(data, category)

main('wertyui')
