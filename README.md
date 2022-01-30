# MTG Tourney Scrapper

## Setup

1. Setup python env

```bash
poetry install
```

2. Get MTG JSON data

```bash
wget -O alldata.json https://mtgjson.com/api/v5/AllPrintings.json
```

## Run scrapper

**IMPORTANT** - -O must always be `tmp-data.json`. A bit stupid, but it is what it is.
```bash
poetry run scrapy crawl mtggoldfish -O tmp-scrapped-data.json -a format=modern  
poetry run scrapy crawl mtggoldfish -O tmp-scrapped-data.json -a format=pauper  
poetry run scrapy crawl mtggoldfish -O tmp-scrapped-data.json -a format=pauper -a date_from=2022-01-01 -a date_to=2022-02-01 
```

Arguments:
- format=<str> (Defaults to modern)
- date_from=<iso-date-str> (Defaults to 60 days from now). `eg. date_from=2022-01-01`
- date_to=<iso-date-str> (Defaults to now) `eg. date_from=2022-01-31`
- alldata_json=<path to file> (Defaults to alldata.json) - This is an AllPrintings.json file from mtgjson.com
- out_dir=<path to dir> (Defaults to visualizer/output_data) - Aggregated visualization json files will be output here

Note the usage of capital <kbd>O</kbd> to create a clan output file each time instead of appending with -o.
