import argparse
import json
import re
import requests
import time

from bs4 import BeautifulSoup


class DocumentEntry:

    def __init__(self):
        self.title = ''
        self.subtitle = ''
        self.text = []

    def __str__(self):
        return str(self.__dict__)


langs = ['rus', 'fin', 'krl', 'vep']


# define and compile all the patterns
REGEXES = (
    # whitespace character normalization
    (re.compile(r' '), ' '),
    (re.compile(r' '), r' '),

    # remove extra spaces
    (re.compile(r' +'), r' ')
)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('out')
    parser.add_argument('-norm', action='store_true')
    parser.add_argument('-segm', action='store_true')

    return parser.parse_args()


def normalize_text(text):
    for regex, sub in REGEXES:
        text = regex.sub(sub, text)
    return text


def get_link_by_lang(lang):
    return f'https://omamedia.ru/news/?language={lang}'


def parse_article_page(link, entry, norm=False):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')

    article = soup.find('div', class_='news-wrapper')
    entry.subtitle = article.find('div', class_='news-subtitle').text.strip()

    for paragraph in article.find_all('p'):
        p = paragraph.text.strip()
        if len(p) > 0:
            p = normalize_text(p) if norm else p
            entry.text.append(p)


def parse_catalogue_page(tree, norm=False):
    entries = []
    news_list = tree.find('div', class_='news-list')

    for item in news_list.find_all('div', class_='news-list-item'):
        link = 'https://omamedia.ru' + item.find('a', class_='news-list-item__link')['href']
        title = item.find('div', class_='news-list-item__title').text.strip()

        entry = DocumentEntry()
        entry.title = title
        parse_article_page(link, entry, norm)

        entries.append(entry)

    return entries


def get_next_page_link(tree):
    pagination = tree.find('div', class_='pagination')
    next_page = pagination.find('a', class_='pagination__item next')
    time.sleep(5)

    if next_page.has_attr('href'):
        return 'https://omamedia.ru' + next_page['href']
    return None


def get_num_pages(tree):
    pagination = tree.find('div', class_='pagination')
    return pagination.find('div', class_='pagination__count').text[1:]


def parse(lang, norm=False):
    entries = []
    link = get_link_by_lang(lang)
    n = 0
    i = 1

    while link is not None:
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        entries += parse_catalogue_page(soup, norm)
        link = get_next_page_link(soup)

        if n == 0:
            n = get_num_pages(soup)
        print(f'Processed pages: {i}/{n}')
        i += 1

    return entries


def process_entry(entry):
    sentences = []

    for paragraph in entry.text:
        sentences += sent_tokenize(paragraph, language='estonian')
    entry.text = sentences

    return entry


def save_as_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    args = parse_args()
    out_path = args.out
    to_norm = args.norm
    to_segm = args.segm

    result = {}

    for lang in langs:
        print(f'Currently processing language: {lang}...')
        result[lang] = parse(lang, to_norm)
        print(f'Done! Found {len(result[lang])} articles.')
        if to_segm:
            result[lang] = [process_entry(entry) for entry in result[lang]]
        print('Saving the data...')
        save_as_json(result[lang], f'{out_path}/{lang}.json')
        print('Saved!')
