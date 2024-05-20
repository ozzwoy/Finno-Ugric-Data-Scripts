# Finno-Ugric-Data-Scripts

Repository with scripts for parsing and preprocessing data from VepKar, Omamedia and Wikipedia, covering texts in Proper Karelian, Livvi, Ludian and Veps.

### VepKar parser

Parses texts and saves them in a separate .json file for each language. The output path is <out>/<language name>.json. Each .json file keeps a list of text entries. Each entry contains the following fields: "id", "dialect", "corpus", "genre", "title", "mono" (whether supplemented with a translation into Russian), "text" (a list of source sentences), "translation" (a list of translated sentences). Normalization removes HTML-characters and fixes whitespaces.

```
python parse_vepkar.py out [-norm]
```

positional arguments:
 - `out`&nbsp;&nbsp;&nbsp;&nbsp;an output directory

options:
 - `norm`&nbsp;&nbsp;&nbsp;&nbsp;normalize outputs