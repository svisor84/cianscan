# -*- coding: utf-8 -*-

import os
import json
import requests
import logging
from time import sleep

from cian.parsed_offer import ParsedList
from realty.settings import PROXY, DATA_FOLDER


def parse_serp(filenames, url_name, logger):
    pl = ParsedList(url_name)
    pl.set_logger(logger)

    with open(filenames[0], 'r') as f:
        data = json.load(f)
        pl.go(data['results'])
        pl.max_auction_bet = data['maxAuctionBet']

    for next_page_filename in filenames[1:]:
        with open(next_page_filename, 'r') as f:
            data = json.load(f)
            pl.parse_offers(data['results']['offers'])

    #pl.print_data()
    pl.export()


def _filename(base, page):
    return DATA_FOLDER + '%s_%d.json' % (base, page)


def _try_serp(url, proxies=None):
    prefix = 'window.__serp_data__='
    if proxies:
        response = requests.get(url, proxies=proxies)
    else:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})

    html_data = response.text
    json_data = ''
    for i, l in enumerate(html_data.split('\n')):
        l = l.strip()
        if l.startswith(prefix):
            json_data = l[len(prefix):-1]
            break
    return json_data


def run_page(url, base_filename, page_number, logger):
    logger.info('Run page %s -> %d', url, page_number)

    serp_filename = _filename(base_filename, page_number)

    sleep(3)  # на всякий
    json_data = _try_serp(url, PROXY)
    if not json_data:
        json_data = _try_serp(url)

    if json_data:
        with open(serp_filename, 'w') as f:
            f.write(json_data.encode('utf-8'))
        return json_data
    else:
        return None


def run(url, base_filename, max_pages=3, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)

    is_ok = True
    json_data_first_page = run_page(url, base_filename, 1, logger)
    if not json_data_first_page:
        return False

    pages_count = 1
    data = json.loads(json_data_first_page)
    for page_n, page_url in enumerate(data['results']['paginationUrls'][1:max_pages]):
        page_ok = run_page(page_url, base_filename, page_n + 2, logger)
        pages_count += 1
        is_ok = is_ok and page_ok

    filenames = [_filename(base_filename, page) for page in range(1, pages_count+1)]
    logger.info('Filenames: %s', filenames)
    logger.info('Parse...')
    if is_ok:
        parse_serp(filenames, url, logger)

        for fn in filenames:
            os.remove(fn)
        logger.info('Done.')
    return is_ok
