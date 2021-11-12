# -*- coding: utf-8 -*-

import urllib
import urllib.parse


def update_querystring(url, **kwargs):
    base_url = urllib.parse.urlsplit(url)
    query_args = urllib.parse.parse_qs(base_url.query)
    query_args.update(kwargs)

    for arg_name, arg_value in query_args.iteritems():
        if arg_value is None:
            if query_args.has_key(arg_name):
                del query_args[arg_name]
        else:
            if type(arg_value) == list:
                if len(arg_value) == 0:
                    del query_args[arg_name]
                #if all(map(lambda x: x.isnumeric(), arg_value)):
                if True:
                    arg_value = ','.join(arg_value)
            try:
                query_args[arg_name] = arg_value.encode('utf-8')
            except Exception:
                query_args[arg_name] = arg_value

    query_string = urllib.urlencode(query_args)
    result = urllib.parse.urlunsplit((base_url.scheme, base_url.netloc, base_url.path, query_string, base_url.fragment))
    return result


def url_for_other_page(uri, page):
    return update_querystring(uri, page=page)


def url_args(query_args):
    """
    :param query_args: dict of args 
    :return: string with get params 
    """
    for k, v in query_args.iteritems():
        if type(v) == list:
            query_args[k] = ','.join(map(str, v))
        query_args[k] = query_args[k].encode('utf-8')
    return urllib.urlencode(query_args)
