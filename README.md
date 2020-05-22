# Welcome to the ChemRxiv Dashboard

This project provides an **[unofficial dashboard](https://chemrxiv-dashboard.github.io)** to the [ChemRxiv preprint server](https://chemrxiv.org), based on the data publicly available from the [figshare API](https://docs.figshare.com).

## The code

Code requires Python 3.6 or later. Data is downloaded from the figshare API with [`download_metadata.py`](download_metadata.py). This requires a figshare token, read from your home directory `~/.figshare_token`.

## ChemRxiv metadata

The metadata about ChemRxiv preprints is stored in two files:
- [`data/allchemrxiv.json`](data/allchemrxiv.json) holds a list of all the preprints, pairing their figshare identifier with their DOI
- [`data/allchemrxiv_data.json`](data/allchemrxiv_data.json) contains the complete metadata

That metadata is under the [CC0 licence](https://knowledge.figshare.com/articles/item/copyright-and-licence-policy) ([Creative Commons “Public Domain Dedication”](https://creativecommons.org/publicdomain/zero/1.0/)).
