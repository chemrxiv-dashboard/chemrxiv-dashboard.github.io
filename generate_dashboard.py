#!/usr/bin/env python3

import collections
import datetime
import json
import os
import sys


def country(s):
    s = country_lower(s)
    if s == 'usa':
        return 'USA'
    else:
        return s.title()

def country_lower(s):
    s = s.lower().replace('.', '').strip()
    if s[:4] == 'the ':
        s = s[4:]

    if 'russia' in s:
        s = 'russia'
    if 'korea' in s:
        if 'north' in s or 'people' in s or 'pr' in s:
            s = 'north korea'
        else:
            s = 'south korea'
    if 'hong kong' in s or 'hk' in s:
        s = 'hong kong'

    if 'algérie' in s:
        return 'algeria'
    if 'türkiye' in s:
        return 'turkey'
    if 'belgique' in s:
        return 'belgium'
    if 'deutschland' in s:
        return 'germany'
    if 'italia' in s:
        return 'italy'
    if 'méxico' in s:
        return 'mexico'
    if 'españa' in s:
        return 'spain'
    if 'polska' in s:
        return 'poland'
    if 'sverige' in s:
        return 'sweden'
    if 'danmark' in s:
        return 'denmark'

    if 'united state' in s or 'unites states' in s or 'america' in s:
        return 'usa'
    if s == 'us':
        return 'usa'

    if s == 'uk' or 'great britain' in s or 'england' in s:
        s = 'united kingdom'
    if 'northern ireland' in s:
        s = 'united kingdom'

    if 'prc' in s or 'china' in s:
        s = 'china'

    if ',' in s:
        return country_lower(s.split(',')[0])
    if ';' in s:
        return country_lower(s.split(';')[0])
    if '/' in s:
        return country_lower(s.split('/')[0])
    if ' and ' in s:
        return country_lower(s.split(' and ')[0])
    if ' - ' in s:
        return country_lower(s.split(' - ')[0])

    return s


def homogenise_journals(journals):
    for j in journals:
        if ' International Edition' in journals[j]:
            # Angewandte references are split between two journal names, merge them
            journals[j] = journals[j].replace(' International Edition', '')
        elif 'A European Journal' in journals[j] and 'Chemistry' in journals[j]:
            # Chem Eur J is spelt differently sometimes
            journals[j] = 'Chemistry: A European Journal'
        elif 'Acta Crystallographica Section B' in journals[j]:
            # This is just too long
            journals[j] = 'Acta Crystallographica B'


def read_include(filename):
    with open(filename, 'r') as f:
        print(f.read())


# Main program
if __name__ == "__main__":

    with open('data/allchemrxiv_data.json', 'r') as f:
        preprints = json.load(f)

    read_include('static/include_head.html')

    # Find the latest data
    latest = '2020-01-01'
    for p in preprints.values():
        d = p['statusDate'].split('T')[0]
        if d > latest:
            latest = d
    print(f'<h4>(updated on {latest})</h4>')

    # Number of preprints and revisions
    ntot = len(preprints)
    nrev = -ntot
    for p in preprints.values():
        nrev += int(p['version'])

    print('<div id="summary">')
    print(f'<div id="total">{ntot} preprints</div>')
    print(f'<div id="revisions">{nrev} revisions</div>')
    print('</div>')

    monthly = []
    for i in preprints.values():
        # FIXME -- this should be "first publication" but it is
        # not provided by the new API
        m = i['publishedDate']
        monthly.append(m[:7])

    monthly = collections.Counter(monthly)
    monthly = sorted(monthly.most_common())

    print('''
<h2>Preprints per month</h2>
<canvas id="monthlyChart" height="120"></canvas>
<script>
var ctx = document.getElementById('monthlyChart').getContext('2d');
var chart = new Chart(ctx, {
    type: 'bar',
    data: {
        datasets: [{
            label: 'preprints per month',
            backgroundColor: 'rgba(99, 99, 255, 0.8)',
            data: [
    ''')
    for i, j in monthly[:-1]:
        d = i[:4] + '-' + i[5:] + '-01'
        print("{x: '" + d + "', y: " + str(j) + "},")
    print(''']
        },{
            label: 'current month',
            backgroundColor: 'rgba(140, 99, 255, 0.4)',
            data: [
    ''')
    i, j = monthly[-1]
    print(f"{{x: '{i[:4]}-{i[5:]}-01', y: {j}}},")
    print(f"{{x: '{i[:4]}-{i[5:]}-28', y: 0}},")
    print(''']
        }]
    },
    options: {
        scales: {
            xAxes: [{
                stacked: true,
                type: 'time',
                time: {
                    unit: 'month'
                }
            }]
        }
    }
});
</script>
    ''')

    c = collections.Counter()
    for i in preprints.values():
        countries = [y['country'] for x in i['authors'] for y in x['institutions']]
        # Normalize country names, remove empty fields, count only once per paper
        countries = list(set(country(x) for x in countries if x))
        c.update(countries)

    print('''
<h2>Preprints per country</h2>
<div id="countryPie">
<canvas id="countryChart" height="200"></canvas>
</div>
<script>
var ctx = document.getElementById('countryChart').getContext('2d');
var chart = new Chart(ctx, {
    type: 'pie',
    data: {
    ''')

    x = c.most_common(20)
    s = sum(j for i, j in x)
    n = sum(c.values())
    x.append(('Others', n - s))

    print(f'labels: {json.dumps([i for i,j in x])},')
    print('datasets: [{data: ' + json.dumps([j for i, j in x]) + ',')
    print("backgroundColor: ['rgb(31 119 180)', 'rgb(255 127 14)', 'rgb(44 160 44)', 'rgb(214 39 40)', 'rgb(148 103 189)', 'rgb(140 86 75)', 'rgb(227 119 194)', 'rgb(127 127 127)', 'rgb(188 189 34)', 'rgb(23 190 229)', 'rgb(174 199 232)', 'rgb(255 187 120)', 'rgb(152 223 138)', 'rgb(255 152 150)', 'rgb(197 176 213)', 'rgb(196 156 148)', 'rgb(247 182 210)', 'rgb(180 180 180)', 'rgb(219 219 141)', 'rgb(158 218 229)', 'rgb(225 225 225)'],")
    print('borderWidth: [2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,0.5,0.5,0.5,0.5,0.5,2]}],')
    print('}, options: {cutoutPercentage: 10}});')
    print('</script>')

    print('<div id="countryTable">')
    print('<table><thead><tr><th>Country</th><th># preprints</th></tr></thead><tbody>')
    for i, j in c.most_common(30):
        print(f'<tr><td>{i}</td><td>{j}</td></tr>')
    print('</table>')
    print('</div>')

    print('''
<div class="clear"></div>
<h2>Preprints by journal</h2>
<p>What are the journals in which ChemRxiv preprints are published (after peer review)?
   The top journals are:</p>''')

    with open('data/doi_journal.json', 'r') as f:
        journals = json.load(f)
    homogenise_journals(journals)

    c = collections.Counter(journals.values())
    print('<table id="journalTable"><thead><tr><th>Journal</th><th># preprints</th></tr></thead><tbody>')
    for i, j in c.most_common():
        if j >= 3:
            print(f'<tr><td>{i}</td><td>{j}</td></tr>')
    print('<tfoot><tr><td colspan="2">Show all journals with at least 3 papers</td></tr></tfoot></table>')

    read_include('static/include_foot.html')
    sys.exit(0)
