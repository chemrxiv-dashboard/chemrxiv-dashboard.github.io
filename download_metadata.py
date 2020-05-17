#!/usr/bin/env python3

import json
import os
import requests
import sys


def showProgress(n, total, prefix='', length=80, suffix='', fill='█', printEnd='\r'):
    """Display a progress bar"""

    percent = int(100 * (n + 1) / total)
    filledLength = int(length * (n + 1) // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    if len(suffix) > 0:
        suffix = ' ' + suffix
    print('\r%s |%s| %s%%%s' % (prefix, bar, percent, suffix), end=printEnd)
    if n >= total - 1:
        print()


class ChemRxivAPI:
    """Handle figshare API requests, using access token"""

    base = 'https://api.figshare.com/v2'
    pagesize = 100

    def __init__(self, token):
        """Initialiase the object and check access to the API"""

        self.token = token
        self.headers = {'Authorization': 'token ' + self.token}

        r = requests.get(f'{self.base}/account', headers=self.headers)
        r.raise_for_status()

    def request(self, url, method, params):
        """Send a figshare API request"""

        if method.casefold() == 'get':
            return requests.get(url, headers=self.headers, params=params)
        elif method.casefold() == 'post':
            return requests.post(url, headers=self.headers, json=params)
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
            params.update({'limit': self.pagesize, 'offset': n})
            r = self.request(f'{self.base}/{query}', method, params)
            r.raise_for_status()
            r = r.json()

            # Special case if a single item, not a list, was returned
            if not isinstance(r, list):
                yield r
                return

            # If we have no more results, bail out
            if len(r) == 0:
                return

            yield from r
            n += self.pagesize

    def query_list(self, *args, **kwargs):
        """Query of a list of item, handling paging internally, returning a
        list. May take a long time to return."""

        return list(self.query_generator(*args, **kwargs))

    def all_preprints(self):
        """Return a generator to all the chemRxiv preprints"""

        return api.query_generator('articles?institution=259')

    def preprint(self, identifier):
        """Information on a given preprint"""

        return api.query(f'articles/{identifier}')

    def author(self, identifier):
        """Information on a given preprint"""

        return api.query(f'account/authors/{identifier}')

    def custom_fields_as_dict(self, doc):
        """Retrieve chemRxiv custom fields as a dictionary"""

        return {i['name']: i['value'] for i in doc['custom_fields']}

    def search_authors(self, criteria):
        """Search for authors"""

        return api.query('account/authors/search', method='POST', params=criteria)

    def search_preprints(self, criteria):
        """Search for preprints"""

        p = {**criteria, 'institution': 259}
        return api.query_list('articles/search', method='POST', params=p)


################################################
# The main program

# We need a figshare API token, see https://docs.figshare.com
# You can insert it below, or store it as text in ~/.figshare_token
token = 'invalid'
try:
    f = open(os.path.expanduser('~/.figshare_token'), 'r')
    token = f.read().strip()
except IOError:
    pass

# Connect to figshare
try:
    api = ChemRxivAPI(token)
except requests.exceptions.HTTPError as e:
    print(f'Authentication did not succeed. Token was: {token}')
    print(f'Error: {e}')
    sys.exit(1)

# Iterate over all preprints
print(f'Downloading list of preprints')
preprints = {}
for doc in api.all_preprints():
    preprints[doc['id']] = doc['doi']

# Store the figshare IDs and associated DOIs
with open('data/allchemrxiv.json', 'w') as f:
    json.dump(preprints, f, sort_keys=True, indent=0)

print(f'Found {len(preprints)} preprints')
print(f'Now downloading full data')

data = {}
for k, p in enumerate(preprints):
    showProgress(k, len(preprints))
    data[p] = api.preprint(p)

# Store the metadata
# It's a JSON file, but in the higher-level dictionary we want
# one element per line, so diffs are readable and small in size
with open('data/allchemrxiv_data.json', 'w') as f:
    first = True
    f.write('{\n')
    for k, v in sorted(data.items()):
        if first:
            first = False
        else:
            f.write(',\n')
        f.write(f'"{k}": {json.dumps(v)}')
    f.write('\n}\n')

sys.exit(0)
