# -*- coding: utf-8 -*-

import json
import requests

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "realty.settings"

import django
django.setup()

from cian.parsed_offer import ParsedList
from cian.working import run

URL = 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&maxprice=18000000&metro%5B0%5D=116&minprice=14000000&offer_type=flat&parking_type%5B0%5D=1&parking_type%5B1%5D=2&parking_type%5B2%5D=3&room2=1'



for k, v in data.iteritems():
    print( '*'*80 )
    print( k, type(v) )
    if type(v) == list:
        print( len(v) )
    elif type(v) == dict:
        for ch_k, ch_v in v.iteritems():
            print( '  -', ch_k, type(ch_v) )
    else:
        print( v )

for k, v in results.iteritems():
    print( '*' * 80 )
    print( k, type(v) )
    if type(v) == list:
        print( len(v) )
    elif type(v) == dict:
        for ch_k, ch_v in v.iteritems():
            print( '  -', ch_k, type(ch_v) )
    else:
        print( v )

total_offers = results['totalOffers']
json_query = results['jsonQuery']
query_string = results['queryString']
print( '*'*80 )
for p in results['paginationUrls']:
    print( p )



def download(url=URL, filename='test_downloaded.html'):
    with open(filename, 'w') as f:
        f.write(requests.get(url).text.encode('utf-8'))


def extract_json(filename):
    prefix = 'window.__serp_data__='
    json_data = ''
    with open(filename, 'r') as f:
        for i, l in enumerate(f.readlines()):
            l = l.strip()
            if l.startswith(prefix):
                json_data = l[len(prefix):-1]
                break
    with open('json_' + filename, 'w') as f:
        f.write(json_data)


def repair_prices():
    from cian.models import OfferPrice

    recent = None
    for op in OfferPrice.objects.all().order_by('offer', 'created_at'):
        if recent and recent.offer_id == op.offer_id and recent.price == op.price:
            print( 'to_delete', op.offer_id, op.price )
            op.delete()
        else:
            print( 'ok', op.offer_id, op.price )
            recent = op


def repair_notifications():
    from office.models import Notification
    for n in Notification.objects.filter(type='new_watching_offer'):
        values = eval(str(n.values))
        if type(values) != dict:
            n.values = "{'offer_id': %s}" % values
            n.save()


def debug_positions():
    from cian.models import OffersUpdate

    ou = OffersUpdate.objects.get(id=403)
    ou.go()

    repair_notifications()



if __name__ == '__main__':
    debug_positions()
