#!/usr/bin/env python3

import bz2
import json
import os
import requests
import sys


def showProgress(n, total, prefix='', length=80, suffix='', fill='█', printEnd='\r'):
    """Display a progress bar"""

    if sys.stdout.isatty():
        # Display a progress bar
        percent = int(100 * (n + 1) / total)
        filledLength = int(length * (n + 1) // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        if len(suffix) > 0:
            suffix = ' ' + suffix
        print('\r%s |%s| %s%%%s' % (prefix, bar, percent, suffix), end=printEnd)
        if n >= total - 1:
            print()
    else:
        # Display progress at regular intervals
        step = total // 20
        if n % step == 0 or n == total:
            print(f'   {n} / {total}')


class ChemRxivAPI:
    """Handle Open Engage API requests"""

    # Defined as per https://chemrxiv.org/engage/chemrxiv/public-api/documentation
    base = 'https://chemrxiv.org/engage/chemrxiv/public-api/v1'
    pagesize = 50

    def request(self, url, method, params):
        """Send an API request"""

        if method.casefold() == 'get':
            return requests.get(url, params=params)
        elif method.casefold() == 'post':
            return requests.post(url, json=params)
        else:
            raise Exception(f'Unknow method for query: {method}')

    def query(self, query, method='get', params=None):
        """Perform a direct query"""

        r = self.request(f'{self.base}/{query}', method, params)
        r.raise_for_status()
        return r.json()

    def query_generator(self, query, method='get', params={}):
        """Query for a list of items, with paging. Returns a generator."""

        n = 0
        while True:
            params.update({'limit': self.pagesize, 'skip': n * self.pagesize})
            r = self.request(f'{self.base}/{query}', method, params)
            r.raise_for_status()
            r = r.json()

            r = r['itemHits']

            # If we have no more results, bail out
            if len(r) == 0:
                return

            yield from r
            n += 1

    def all_preprints(self):
        """Return a generator to all the chemRxiv preprints"""

        return api.query_generator('items')

    def number_of_preprints(self):
        """Return the number of chemRxiv preprints"""

        return api.query('items')['totalCount']

    def preprint(self, identifier):
        """Information on a given preprint"""

        return api.query(f'items/{identifier}')


################################################
# The main program

# API does not currently have token authentication
api = ChemRxivAPI()

# Iterate over all preprints
total = api.number_of_preprints()
print(f'Downloading list of preprints ({total})')
preprints = {}
data = {}

n = 0
for preprint in api.all_preprints():
    showProgress(n, total)
    n += 1
    doc = preprint['item']

    # Remove metrics, since they change all the time
    del doc['metrics']

    # Store the remaining metadata
    preprints[doc['id']] = doc['doi']
    data[doc['id']] = doc

# Store the preprint IDs and associated DOIs
with open('data/allchemrxiv.json', 'w') as f:
    json.dump(preprints, f, sort_keys=True, indent=0)

# Store the metadata
with bz2.open('data/allchemrxiv_data.json.bz2', 'wt') as f:
    json.dump(data, f, sort_keys=True, indent=0)

# Retrieve the journal names associated with each published preprint
print('Retrieving data about published papers')
try:
    with open('data/doi_journal.json', 'r') as f:
        journals = json.load(f)
except Exception:
    journals = {}

for k, p in enumerate(data.values()):
    showProgress(k, len(data))
    if p['vor']:
        pubdoi = p['vor']['vorDoi']
        if pubdoi not in journals:
            response = requests.get(f'https://api.crossref.org/works/{pubdoi}')
            try:
                j = response.json()['message']['container-title'][0]
                journals[pubdoi] = j
            except Exception:
                pass

with open('data/doi_journal.json', 'w') as f:
    json.dump(journals, f, sort_keys=True, indent=0)

sys.exit(0)
