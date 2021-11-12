# -*- coding: utf-8 -*-

import urllib
import urllib.parse
import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, HttpResponse, render, HttpResponseRedirect
from django.conf import settings

from office.models import BrokerFilter, Broker, NOTIFICATION_TYPES
from cian.models import OffersFilter, OfferPosition, Retailer, Phone, Offer

PER_PAGE = 20


def upsert_broker(request):
    if request.user.is_authenticated():
        broker = request.user.broker.first()
        if not broker:
            broker = Broker(user=request.user)
            broker.save()
        return broker
    else:
        return None


def common_context(request):
    broker = upsert_broker(request)
    return {
        'uri': request.get_full_path(),
        'broker': broker,
        'notifications_count': broker.notifications.filter(is_viewed=False).count() if broker else 0,
    }


def with_paginator(request, items):
    paginator = Paginator(items, PER_PAGE)
    page = int(request.GET.get('page', '1'))
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        items = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        items = paginator.page(page)
    return items


@login_required()
def home(request):
    context = common_context(request)

    if not context['broker']:
        return HttpResponse(u'Вы не являетесь брокером. Отредактируйте профиль.')

    broker = context['broker']
    offer_filters = broker.filters.all().order_by('created_at')
    context['broker_filters'] = offer_filters
    context['broker_positions'] = broker.get_filter_positions()
    context['filters_notifications'] = broker.get_notification_summary()

    return render(request, 'home.html', context)


@login_required()
def filters(request):
    context = common_context(request)
    broker = context['broker']
    offer_filters = broker.filters.all().order_by('created_at')

    if request.method == "POST":
        for offer_filter in offer_filters:
            new_name = request.POST.get('name-%d' % offer_filter.id)
            is_deleted = request.POST.get('del-%d' % offer_filter.id) == 'true'
            if is_deleted:
                offer_filter.to_delete()
            else:
                offer_filter.name = new_name
                offer_filter.save()

        for i in range(1, 4):
            name = request.POST.get('name-new-%d' % i)
            url = request.POST.get('url-new-%d' % i)
            if name and url:
                BrokerFilter.create(broker, name, url)

        return HttpResponseRedirect('/filters/')

    context['broker_filters'] = offer_filters
    return render(request, 'filters.html', context)


@login_required()
def offers(request):
    context = common_context(request)
    broker = context['broker']

    if request.method == "POST":
        error = broker.update_phone(request.POST.get('broker_phone'))
        if error is None:
            return HttpResponseRedirect('/offers/')
        else:
            context['phone_error'] = error

    context['broker_offers'] = with_paginator(request, broker.offers.all())
    context['offers_positions'] = broker.get_offers_positions()
    context['filter_id_to_name_map'] = broker.filter_id_to_name_map()
    context['can_change_phone'] = True # not broker.offers.exists()

    return render(request, 'offers.html', context)


@login_required()
def offers_on_control(request):
    context = common_context(request)
    broker = context['broker']

    if request.method == "POST":
        for i in range(1, 4):
            url = request.POST.get('url-new-%d' % i)
            if url:
                cian_id = filter(None, url.split('/'))[-1]
                if not unicode(cian_id).isnumeric():
                    continue
                offer = Offer.objects.filter(cian_id=cian_id).first()
                if not offer:
                    offer = Offer(cian_id=cian_id)
                    offer.save()
                broker.control_offers.add(offer)

    context['broker_offers'] = with_paginator(request, broker.control_offers.all().order_by('id'))
    context['offers_positions'] = broker.get_offers_positions([x.id for x in context['broker_offers']])
    context['filter_id_to_name_map'] = broker.filter_id_to_name_map()

    return render(request, 'offers_on_control.html', context)


@login_required()
def phone_offers(request, phone):
    context = common_context(request)
    context['phone'] = phone
    phone_obj = Phone.objects.filter(phone=phone).first()
    if phone_obj:
        context['offers'] = Offer.objects.filter(phone=phone_obj)

    return render(request, 'phone_offers.html', context)


def _positions_cmp(a, b):
    if a.position and b.position:
        a_is_top = a.offer.is_top
        b_is_top = b.offer.is_top
        if a_is_top and b_is_top:
            return cmp(a.updated_at, b.updated_at)
        elif a_is_top and not b_is_top:
            return -1
        elif b_is_top and not a_is_top:
            return 1
        else:
            return cmp(a.position, b.position)
    elif a.position and not b.position:
        return -1
    elif b.position and not a.position:
        return 1
    else:
        return cmp(a.updated_at, b.updated_at)


@login_required()
def serp(request, filter_id):
    context = common_context(request)
    broker = context['broker']

    offer_filter = get_object_or_404(OffersFilter, id=filter_id)
    broker_filter = BrokerFilter.objects.filter(filter=offer_filter, broker=broker).first()
    offer_positions = list(OfferPosition.objects.filter(filter=offer_filter))

    context['broker_filter'] = broker_filter
    context['offer_filter'] = offer_filter
    context['broker_offer_ids'] = set(broker.get_offer_ids())
    context['offers_on_control'] = set(broker.get_control_ids())
    context['order_types'] = [
        ('position', u'По порядку'),
        ('price', u'По цене'),
        ('created_at', u'По дате добавления'),
        ('updated_at', u'По дате обновления'),
        ('changed_at', u'По дате изменения позиции'),
    ]

    def _changed_at_cmp(a, b):
        a_dt = offer_filter.offer_position_changed(a.offer_id)
        b_dt = offer_filter.offer_position_changed(b.offer_id)
        return cmp(a_dt, b_dt)

    ordering = request.GET.get('type', 'position')
    if ordering == 'position':
        offer_positions.sort(cmp=_positions_cmp)
    elif ordering == 'changed_at':
        offer_positions.sort(cmp=_changed_at_cmp, reverse=True)
    else:
        reverse = ordering in ['created_at', 'updated_at']
        try:
            offer_positions.sort(key=lambda x: getattr(x.offer, ordering), reverse=reverse)
        except Exception:
            pass    # ну и ладно

    context['offers_positions'] = with_paginator(request, offer_positions)
    context['selected_type'] = request.GET.get('type')
    return render(request, 'serp.html', context)


@login_required()
def offer(request, offer_id):
    context = common_context(request)
    offer_obj = get_object_or_404(Offer, id=offer_id)
    broker = context['broker']
    context['item'] = offer_obj
    context['on_control'] = Broker.control_offers.through.objects.filter(broker=broker, offer=offer_obj).exists()
    context['is_mine'] = Broker.offers.through.objects.filter(broker=broker, offer=offer_obj).exists()

    context['offer_positions'] = broker.get_offers_positions([offer_obj.id])
    context['filter_id_to_name_map'] = broker.filter_id_to_name_map()

    return render(request, 'offer.html', context)


@login_required()
def notifications(request):
    context = common_context(request)
    broker = context['broker']
    notifications = broker.notifications.all()

    context['filter_id_to_name_map'] = broker.filter_id_to_name_map()

    context['filters_types'] = filter(lambda x: x[0] not in ['default'], NOTIFICATION_TYPES)
    context['filters_filters'] = set([x['offers_filter_id'] for x in notifications.values('offers_filter_id') if x['offers_filter_id']])

    selected_types = request.GET.getlist('type')
    if selected_types:
        notifications = notifications.filter(type__in=selected_types)
    context['selected_types'] = selected_types

    selected_filters = request.GET.getlist('filter')
    if selected_filters:
        selected_filters = map(int, selected_filters)
        notifications = notifications.filter(offers_filter_id__in=selected_filters)
    context['selected_filters'] = selected_filters

    if request.GET.get('dates'):
        dates = request.GET.get('dates')
        if dates == 'day':
            notifications = notifications.filter(created_at__gte=(datetime.now() - timedelta(days=1)))
        elif dates == 'week':
            notifications = notifications.filter(created_at__gte=(datetime.now() - timedelta(days=7)))

    if request.GET.get('only_new') == 'on':
        notifications = notifications.filter(is_viewed=False)

    if request.GET.get('mark_viewed') == 't':
        notifications.update(is_viewed=True)

    context['selected_dates'] = request.GET.get('dates', '')
    items = notifications.order_by('-created_at')

    context['notifications'] = with_paginator(request, items)
    context.update(common_context(request))

    return render(request, 'notifications.html', context)


@login_required()
def retailers(request):
    context = common_context(request)

    items = Retailer.objects.filter(phones__isnull=False).distinct()

    if request.GET.get('query'):
        items = items.filter(name__icontains=request.GET.get('query'))

    if request.GET.get('dates'):
        dates = request.GET.get('dates')
        if dates == 'day':
            items = items.filter(created_at__gte=(datetime.now() - timedelta(days=1)))
        elif dates == 'week':
            items = items.filter(created_at__gte=(datetime.now() - timedelta(days=7)))
    context['selected_dates'] = request.GET.get('dates', '')
    context['query'] = request.GET.get('query', '')

    context['retailers'] = with_paginator(request, items.order_by('name'))
    return render(request, 'retailers.html', context)


def documentation(request):
    context = common_context(request)
    return render(request, 'documentation.html', context)


@login_required()
def ajax_set_offer_moulage(request):
    offer_id = request.GET.get('offer_id')
    is_moulage = request.GET.get('is_moulage') == 'true'

    offer = get_object_or_404(Offer, id=offer_id)
    offer.is_moulage = is_moulage
    offer.save()
    return HttpResponse('')


@login_required()
def ajax_set_on_control(request):
    offer_id = request.GET.get('offer_id')
    active = request.GET.get('active') == 'true'

    offer = get_object_or_404(Offer, id=offer_id)
    broker = upsert_broker(request)
    if active:
        broker.control_offers.add(offer)
    else:
        broker.control_offers.remove(offer)

    return HttpResponse('')


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
                arg_value = arg_value[0]
            try:
                query_args[arg_name] = arg_value.encode('utf-8')
            except Exception:
                query_args[arg_name] = arg_value

    query_string = urllib.urlencode(query_args)
    return urllib.parse.urlunsplit((base_url.scheme, base_url.netloc, base_url.path, query_string, base_url.fragment))


def url_for_other_page(uri, page):
    return update_querystring(uri, page=page)


def feed(request):
    if 'key' in request.GET and request.GET.get('key') == settings.FEED_KEY:
        data = [of.get_feed_row() for of in OffersFilter.objects.filter(watch_top3=True)]
        # data = [of.get_feed_row() for of in OffersFilter.objects.all()]
        return HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), content_type="application/json")
    else:
        return HttpResponse('')
