# Finno-Ugric-Data-Scripts

Repository with scripts for parsing and preprocessing data from VepKar, Omamedia and Wikipedia, covering texts in Proper Karelian, Livvi, Ludian and Veps.

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