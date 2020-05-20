#!/usr/bin/env python3

import collections
import datetime
import json
import os
import sys


def country(s):
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

    if 'united states' in s or 'america' in s:
        s = 'usa'
    if s == 'us':
        s = 'usa'

    if s == 'uk' or 'great britain' in s or 'england' in s:
        s = 'united kingdom'
    if 'northern ireland' in s:
        s = 'united kingdom'

    if 'prc' in s or 'china' in s:
        s = 'china'

    if ',' in s:
        return country(s.split(',')[0])
    if ';' in s:
        return country(s.split(';')[0])
    if '/' in s:
        return country(s.split('/')[0])
    if ' and ' in s:
        return country(s.split(' and ')[0])
    if ' - ' in s:
        return country(s.split(' - ')[0])

    if s == 'usa':
        return 'USA'
    else:
        return s.title()


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
        for d in p['timeline'].values():
            d = d.split('T')[0]
            if d > latest:
                latest = d
    print(f'<h4>(data updated on {latest})</h4>')

    # Number of preprints and revisions
    ntot = len(preprints)
    nrev = -ntot
    for p in preprints.values():
        nrev += p['version']

    print('<div id="summary">')
    print(f'<div id="total">{ntot} preprints</div>')
    print(f'<div id="revisions">{nrev} revisions</div>')
    print('</div>')

    monthly = []
    for i in preprints.values():
        m = i['timeline']['firstOnline']
        monthly.append(m[:7])

    monthly = collections.Counter(monthly)
    monthly = sorted(monthly.most_common())

    print('''
<h2>Preprints per month</h2>
<canvas id="monthlyChart" height="120px"></canvas>
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

    countries = []
    for i in preprints.values():
        for f in i['custom_fields']:
            if f['name'] == 'Country':
                countries.append(country(f['value']))

    c = collections.Counter(countries)

    print('''
<h2>Preprints per country</h2>
<div id="countryPie">
<canvas id="countryChart" height="200px"></canvas>
</div>
<script>
var ctx = document.getElementById('countryChart').getContext('2d');
var chart = new Chart(ctx, {
    type: 'pie',
    data: {
    ''')

    x = c.most_common(20)
    s = sum(j for i, j in x)
    n = len(countries)
    x.append(('Others', n-s))

    print(f'labels: {json.dumps([i for i,j in x])},')
    print('datasets: [{data: ' + json.dumps([j for i, j in x]) + ',')
    print("backgroundColor: ['rgb(31 119 180)', 'rgb(255 127 14)', 'rgb(44 160 44)', 'rgb(214 39 40)', 'rgb(148 103 189)', 'rgb(140 86 75)', 'rgb(227 119 194)', 'rgb(127 127 127)', 'rgb(188 189 34)', 'rgb(23 190 229)', 'rgb(174 199 232)', 'rgb(255 187 120)', 'rgb(152 223 138)', 'rgb(255 152 150)', 'rgb(197 176 213)', 'rgb(196 156 148)', 'rgb(247 182 210)', 'rgb(180 180 180)', 'rgb(219 219 141)', 'rgb(158 218 229)', 'rgb(225 225 225)'],")
    print('borderWidth: [2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,0.5,0.5,0.5,0.5,0.5,2]}],')
    print('}, options: {cutoutPercentage: 10}});')
    print('</script>')

    print('<div id="countryTable">')
    print('<table><tr><th>Country</th><th># preprints</th></tr>')
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
    c = collections.Counter(journals.values())
    print('<table id="journalTable"><tr><th>Journal</th><th># preprints</th></tr>')
    for i, j in c.most_common(30):
        print(f'<tr><td>{i}</td><td>{j}</td></tr>')
    print('</table>')


    read_include('static/include_foot.html')
    sys.exit(0)
