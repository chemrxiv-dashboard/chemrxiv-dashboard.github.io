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
            backgroundColor: 'rgba(99, 99, 255, 0.2)',
            data: [
    ''')
    i, j = monthly[-1]
    d = i[:4] + '-' + i[5:] + '-01'
    print("{x: '" + d + "', y: " + str(j) + "},")
    print(''']
        }]
    },
    options: {
        scales: {
            xAxes: [{
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
    print('datasets: [{data: ' + json.dumps([j for i, j in x]) + ' }],')
    print('''
        },
    options: {
        plugins: {
            colorschemes: {
                scheme: 'brewer.Paired12'
            }
        }
    }
    });''')
    print('</script>')

    print('<div id="countryTable">')
    print('<table><tr><th>Country</th><th># preprints</th></tr>')
    for i, j in c.most_common(30):
        print(f'<tr><td>{i}</td><td>{j}</td></tr>')
    print('</table>')
    print('</div>')

    read_include('static/include_foot.html')
    sys.exit(0)
