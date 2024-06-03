# Finno-Ugric-Data-Scripts

Repository with scripts for parsing and preprocessing data from [VepKar](http://dictorpus.krc.karelia.ru/en), [Omamedia](https://omamedia.ru/en/news/) and Wikipedia, covering texts in Proper Karelian, Livvi, Ludian and Veps.

### VepKar parser

Parses texts as a list of sentences and saves them into a separate .json file for each language. The output path is "\<out\>/\<language name\>.json." Each .json file keeps a list of text entries. Each entry contains the following fields: "id", "dialect", "corpus", "genre", "title", "mono" (whether supplemented with a translation into Russian), "text" (a list of source sentences), "translation" (a list of translated sentences). Normalization removes HTML-characters and fixes whitespaces.

```
python parse_vepkar.py out [-norm]
```

positional arguments:
 - `out`&nbsp;&nbsp;&nbsp;&nbsp;an output directory

options:
 - `norm`&nbsp;&nbsp;&nbsp;&nbsp;normalize outputs


 ### Omamedia parser

Parses texts as a list of paragraphs and saves them into a separate .json file for each language. The output path is "\<out\>/\<language code\>.json." Each .json file keeps a list of text entries. Each entry contains the following fields: "title", "subtitle", "text" (a list of source paragraphs/sentences). Normalization removes HTML-characters and fixes whitespaces. Segmentation splits the paragraphs into sentences.

```
python parse_omamedia.py out [-norm] [-segm]
```

positional arguments:
 - `out`&nbsp;&nbsp;&nbsp;&nbsp;an output directory

options:
 - `norm`&nbsp;&nbsp;&nbsp;&nbsp;normalize outputs
 - `segm`&nbsp;&nbsp;&nbsp;&nbsp;segmentize paragraphs into sentences


 ### Wikipedia parser

Parses Wikipedia articles as a list of sentences and saves them into a separate .json file for each language. Specific sections (See also, References, Bibliography, Further reading, External links) are removed. Section titles are removed as well. The output path is "\<out\>/\<language name\>.json." The script normalizes punctuation and whitespace characters. Filtering removes outliers which are either too short (less than 3 words in length) or contain more cyrillic characters than latin ones.

```
python parse_wikipedia.py out [-norm] [-filter]
```

positional arguments:
 - `out`&nbsp;&nbsp;&nbsp;&nbsp;an output directory

options:
 - `norm`&nbsp;&nbsp;&nbsp;&nbsp;normalize outputs
 - `filter`&nbsp;&nbsp;&nbsp;&nbsp;filter outputs