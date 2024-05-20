import json
import os


def parse(path, paragraph_size):
    paragraphs = []

    with open(path, encoding='utf-8') as file:
        data = json.load(file)

    for example in data:
        text = example['text']
        current_paragraph = []
        count = 0

        for sentence in text:
            if count == paragraph_size:
                paragraphs.append(current_paragraph)
                current_paragraph = []
                count = 0

            current_paragraph.append(sentence)
            count += 1

        if count > 0:
            paragraphs.append(current_paragraph)

    return paragraphs


def save_txt(paragraphs, lang, dest):
    with open(dest + f'/mono.{lang}', 'w', encoding='utf-8') as file:
        for paragraph in paragraphs:
            file.write('\n'.join(paragraph) + '\n\n')


def main():
    paths = [
        'data/omamedia/olo.json',
        'data/omamedia/vep.json'
    ]
    lang_ids = ['olo', 'vep']

    for path, lang in zip(paths, lang_ids):
        print(f'\nProcessing file {path}...')
        paragraphs = parse(path, 5)
        print(f'Number of paragraphs: {len(paragraphs)}.')
        print(f'Number of sentences: {sum([len(par) for par in paragraphs])}.')

        if not os.path.exists(f'out/omamedia'):
            os.makedirs(f'out/omamedia')

        save_txt(paragraphs, lang, 'out/omamedia')
        print('Saved and finished!')


if __name__ == '__main__':
    main()
