import argparse
import json
import nltk
import os
import re

from collections import Counter
from datasets import load_dataset
from nltk import sent_tokenize

nltk.download('punkt')

lang_ids = ['olo', 'vep']

alphabet = {
    'olo': 'abcčdefghijklmnoprsšzžtuvyäöABCČDEFGHIJKLMNOPRSŠZŽTUVYÄÖ',
    'vep': 'abcčdefghijklmnoprsšzžtuvüäöABCČDEFGHIJKLMNOPRSŠZŽTUVÜÄÖ'
}

abbreviations = {
    'olo': ['alb.', 'algup.', 'ang.', 'angl.', 'arab.', 'arh.', 'bašk.', 'belor.', 'birm.', 'bul.',
            'dan.', 'eng.', 'esp.', 'ezim.', 'fr.', 'frans.', 'gait.', 'germ.', 'grec.', 'grek.', 'gret.', 'grets.',
            'guar.', 'horv.', 'indon.', 'isl.', 'it.', 'ital.', 'ivr.', 'Iänneoppi.',  'jap.', 'k.', 'karj.', 'kat.',
            'kor.', 'Kč.', 'kč.', 'lat.', 'lit.', 'livv.', 'lyh.', 'malais.', 'malaisk.', 'malaiz.', 'mald.', 'milj.',
            'mir.', 'mm.', 'mold.', 'mon.', 'mong.', 'ms.', 'muinaisgriek.', 'Muinasgrets.', 'n.', 'nepal.', 'niderl.',
            'nor.', 'nyg.', 'oks.', 'pers.', 'pols.', 'port.', 'portug.', 'r.', 'red.', 'roin.', 'ruots.', 'ruoč.',
            's.', 'serb.', 'sloven.', 'suom.', 'szerk.', 'tagalsk.', 'toim.', 'urd.', 'v.', 'vahn.', 'ven.', 'vengr.',
            'veps.', 'vrd.'],

    'vep': ['abaz.', 'alam.', 'amh.', 'amuižegipt.', 'amuižgr.', 'amuižgrek.', 'amuižnorv.', 'amuižpers.', 'amuižslav.',
            'amuižven.', 'ang.', 'angl.', 'arab.', 'armen.', 'azerb.', 'bašk.', 'beng.', 'bolg.', 'bosn.', 'dan.',
            'dial.', 'Dr.', 'enz.', 'est.', 'even.', 'evenk.', 'feat.', 'filipp.', 'fr.', 'franc.', 'ft.', 'gel.',
            'germ.', 'grek.', 'gruz.', 'guar.', 'hak.', 'haus.', 'Hrsg.', 'indonez.', 'inu.', 'irl.', 'isp.', 'it.',
            'ital.', 'iž.', 'jap.', 'jug.', 'k.', 'kalm.', 'karj.', 'kat.', 'kaz.', 'kc.', 'ket.', 'khmer.', 'kit.',
            'kol.', 'kor.', 'laos.', 'lat.', 'latin.', 'latv.', 'litv.', 'litvank.', 'liv.', 'lüh.', 'lüksemb.',
            'madj.', 'malagas.', 'mans.', 'maor.', 'mir.', 'monak.', 'mong.', 'mug.', 'mž.', 'negid.', 'nenc.', 'nivh.',
            'norv.', 'nug.', 'nüg.', 'ohj.', 'orok.', 'oset.', 'oz.', 'ozut.', 'pagin.', 'Ph.', 'ph.', 'phh.',
            'pohjoižsaam.', 'pol.', 'port.', 'rind.', 'rndt.', 'rom.', 'roč.', 'ruand.', 's.', 'saks.', 'sanskr.',
            'slovak.', 'somal.', 'suah.', 'sund.', 'suom.', 'svaz.', 'syn.', 'szerk.', 'sünd.', 'tadž.', 'tetum.',
            'tobj.', 'tof.', 'tong.', 'tot.', 'truh.', 'tsvan.', 'turk.', 'udin.', 'ukr.', 'v.', 'vanh.', 'var.',
            'vaug.', 'ven.', 'veps.', 'vod.', 'vs.', 'vv.', 'čeh.', 'čeč.']
}

REGEXES = (
    # removing redundant commas, colons and spaces in parentheses
    (re.compile(r'[ ]+[,;]'), r','),
    (re.compile(r',;'), r';'),
    (re.compile(r';,'), r';'),
    (re.compile(r',+'), r','),
    (re.compile(r';+'), r';'),
    (re.compile(r'\([ ,;]+'), r'('),
    (re.compile(r'[ ,;]+\)'), r')'),

    # removing empty parentheses
    (re.compile(r'[ ]*\([,? ]*\)'), r''),

    # whitespace character normalization
    (re.compile(r'\r'), r''),

    # normalizing dashes
    (re.compile(r' [-–] '), r' — '),

    # other
    (re.compile(r' '), r' '),
    (re.compile(r'‎'), r''),
    (re.compile(r'‏'), r''),
    (re.compile(r'﻿'), r''),

    # removing extra spaces
    (re.compile(r' +'), r' ')
)


class WikiEntry:

    def __init__(self):
        self.id = ''
        self.url = ''
        self.title = ''
        self.text = []

    def __str__(self):
        return str(self.__dict__)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('out')
    parser.add_argument('-norm', action='store_true')
    parser.add_argument('-filter', action='store_true')

    return parser.parse_args()


def remove_appendices(text, lang):
    sections = {
        'olo': ['Lähtehet', 'Kirjalližuttu', 'Aihies muijal'],  # References, Bibliography, External links
        'vep': ['Kacu mugažo', 'Homaičendad', 'Literatur', 'Edesine lugemine', 'Irdkosketused']  # See also, References, Bibliography, Further reading, External links
    }

    for section in sections[lang]:
        match = re.search('\n\n' + section, text, re.MULTILINE)
        if match is not None:
            text = text[:match.start()]

    return text


def normalize(text):
    text = text.strip()
    for regex, sub in REGEXES:
        text = regex.sub(sub, text)

    return text


def fix_segments(segments, lang):
    i = 0
    pattern = r'[[( ](' + '|'.join(abbreviations[lang]) + r')$'

    # join segments split at contractions of the kind: "c. 1987"
    while i < len(segments) - 1:
        if re.search(pattern, segments[i]) is not None:
            segments[i] = segments[i] + ' ' + segments[i + 1]
            segments.pop(i + 1)
        else:
            i += 1

    i = 1
    # join segments which begin with a lowercase letter with a previous segment
    while i < len(segments):
        if segments[i][0] in alphabet[lang].lower():
            segments[i - 1] = segments[i - 1] + ' ' + segments[i]
            segments.pop(i)
        else:
            i += 1

    return segments


def isolate_sentences(segment):
    split = [chunk.strip() for chunk in segment.split('\n')]
    split = filter(lambda chunk: len(chunk) > 0, split)

    filtered = []
    for chunk in split:
        # check if the sentence is properly terminated (otherwise it can be an auxiliary sign, etc.)
        if re.search(r'''(([.!?])|([.!?]["'»]))$''', chunk) is not None:
            filtered.append(chunk)

    return filtered


def parse_entries(dataset, lang, norm=True):
    entries = []

    for example in dataset:
        entry = WikiEntry()

        entry.id = example['id']
        entry.url = example['url']
        entry.title = example['title']

        stripped = remove_appendices(example['text'], lang)
        normalized = normalize(stripped) if norm else stripped
        segmented = sent_tokenize(normalized, 'estonian')
        segmented = fix_segments(segmented, lang)

        sentences = []
        for segment in segmented:
            sentences += isolate_sentences(segment)

        entry.text = sentences
        entries.append(entry)

    return entries


def check_title(entry, lang):
    stop_words = {
        'olo': ['Kirjalližusluvettelo'],
        'vep': []
    }

    for stop_word in stop_words[lang]:
        if re.search(stop_word, entry.title) is not None:
            return False

    return True


def is_valid(sentence, lang, ratio, min_length):
    num_latin = len(re.findall('[' + alphabet[lang] +']+', sentence))
    num_cyrillic = len(re.findall(r'[а-яА-Я]', sentence))

    if num_latin == 0 or num_cyrillic / num_latin > ratio:
        return False

    num_words = len(re.findall('[' + alphabet[lang] +']+', sentence))
    if num_words < min_length:
        return False

    return True


def filter_sentences(sentences, lang):
    filtered = []

    for sentence in sentences:
        if is_valid(sentence, lang, 1.0, 3):
            filtered.append(sentence)

    return filtered


def filter_entries(entries, lang):
    filtered = []

    for entry in entries:
        if not check_title(entry, lang):
            continue

        entry.text = filter_sentences(entry.text, lang)
        if len(entry.text) > 0:
            filtered.append(entry)

    return filtered


def save_as_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)


def main():
    args = parse_args()
    out_path = args.out
    to_norm = args.norm
    to_filter = args.filter

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for lang in lang_ids:
        print(f'\nProcessing language: {lang}...')
        dataset = load_dataset('wikipedia', language=lang, date='20240301', trust_remote_code=True)
        print(dataset)

        data = parse_entries(dataset['train'], lang, to_norm)
        print(f'Number of sentences: {sum(len(example.text) for example in data)}')

        if to_filter:
            data = filter_entries(data, lang)
            print(f'Number of filtered sentences: {sum(len(example.text) for example in data)}')

        save_as_json(data, out_path + f'/{lang}.json')
        print('Saved and finished!')


if __name__ == '__main__':
    main()
