import argparse
import json
import re
import requests

from bs4 import BeautifulSoup


class DocumentEntry:

    def __init__(self):
        self.id = ''
        self.dialect = ''
        self.corpus = ''
        self.genre = ''
        self.title = ''
        self.mono = False
        self.text = {}
        self.translation = {}

    def __str__(self):
        return str(self.__dict__)


lang2id = {
    'Karelian Proper': 4,
    'Livvi': 5,
    'Ludian': 6,
    'Veps': 1
           }


REGEXES = (
    # whitespace character normalization
    (re.compile(r' '), ' '),
    (re.compile(r'\r'), r''),
    (re.compile(r'\n'), r' '),

    # remove extra spaces
    (re.compile(r' +'), r' ')
)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('out')
    parser.add_argument('-norm', action='store_true')

    return parser.parse_args()


def get_link_by_lang(lang):
    return 'http://dictorpus.krc.karelia.ru/en/corpus/text'\
           f'?limit_num=50&search_lang%5B%5D={lang2id[lang]}'


def parse_text_page(link, entry):
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    text_div = soup.find(class_='row corpus-text')
    text = text_div.find(id='text')
    translation = text_div.find(id='transtext')

    def extract_id(element, trans=False):
        indent = 11 if trans else 6

        if element.has_attr('id'):
            return int(element['id'][indent:])
        elif element.has_attr('ie'):
            return int(element['ie'])
        else:
            raise Exception('Error. Typo in an id-tag.')

    text_sentences = {extract_id(sent): sent.text for sent in text.find_all(class_='sentence')}
    entry.text = text_sentences

    if translation is not None:
        translation_sentences = {extract_id(sent, True): sent.text for sent in
                                 translation.find_all(class_='trans_sentence')}
        entry.translation = translation_sentences
    else:
        entry.mono = True


def parse_catalogue_page(tree):
    table = tree.find(class_='table-bordered table-striped table-wide rwd-table wide-md')
    entries = []

    for row in table.find_all('tr')[1:]:
        entry = DocumentEntry()

        entry.id = row.find(attrs={'data-th': 'No'}).text.strip()
        entry.dialect = row.find(attrs={'data-th': 'Dialect'}).text.strip()
        entry.corpus = row.find(attrs={'data-th': 'corpus'}).text.strip()
        entry.genre = row.find(attrs={'data-th': 'genre'}).text.strip()

        title = row.find(attrs={'data-th': 'Title'})
        entry.title = title.text.strip()
        link = title.find('a')['href']
        parse_text_page(link, entry)

        entries.append(entry)

    return entries


def get_next_page_link(tree):
    navigation_bar = tree.find(class_='pagination')
    pages = navigation_bar.find_all('li')
    next_page = pages[-1]

    if next_page.has_attr('class') and next_page['class'][0] == 'disabled':
        return None
    else:
        return next_page.find('a')['href']


def get_num_pages(tree):
    navigation_bar = tree.find(class_='pagination')
    pages = navigation_bar.find_all('li')
    last_page = pages[-2]

    return last_page.text


def parse(lang):
    entries = []
    link = get_link_by_lang(lang)
    n = 0
    i = 1

    while link is not None:
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        entries += parse_catalogue_page(soup)
        link = get_next_page_link(soup)

        if n == 0:
            n = get_num_pages(soup)
        print(f'Processed pages: {i}/{n}')
        i += 1

    return entries


def save_as_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)


def normalize_sentence(sentence):
    sentence = sentence.strip()
    for regex, sub in REGEXES:
        sentence = regex.sub(sub, sentence)

    return sentence


def normalize_entry(entry):
    entry.text = {key: normalize_sentence(value) for key, value in entry.text.items()}
    entry.translation = {key: normalize_sentence(value) for key, value in entry.translation.items()}

    return entry


if __name__ == '__main__':
    args = parse_args()
    out_path = args.out
    to_norm = args.norm

    result = {}

    for lang_ in lang2id.keys():
        print(f'Currently processing language: {lang_}...')
        result[lang_] = parse(lang_)

        n_mono = len([entry for entry in result[lang_] if entry.mono])
        print(f'Done! Found {len(result[lang_])} examples. Without translation: {n_mono}.')

        if to_norm:
            for entry in result[lang_]:
                normalize_entry(entry)

        print('Saving the data...')
        save_as_json(result[lang_], f'{out_path}/{lang_.replace(' ', '_')}.json')
        print('Saved!')
