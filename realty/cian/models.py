# -*- coding: utf-8 -*-

import os
from datetime import datetime
from time import sleep
import pytils
import logging
import traceback
import sys

from django.db import models


UPDATING_STATUSES = [
    ('waiting', u'Ожидание'),
    ('processing', u'Обновляется'),
    ('success', u'Обновлено успешно'),
    ('retry', u'cian не даёт'),
    ('error', u'Произошла ошибка'),
]

BASE_LOGS_DIR = '/'.join([os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'updates'])
LOGGING_FORMATTER = logging.Formatter('%(levelname)s: %(asctime)s -> %(message)s', datefmt='%H:%M:%S')


class BaseModel(models.Model):
    PRIMARY_KEY = None

    class Meta:
        abstract = True

    @classmethod
    def upsert(cls, **kwargs):
        if type(cls.PRIMARY_KEY) == tuple:
            obj = cls.objects.filter(**{field: kwargs[field] for field in cls.PRIMARY_KEY}).first()
        else:
            obj = cls.objects.filter(**{cls.PRIMARY_KEY: kwargs[cls.PRIMARY_KEY]}).first()
        if not obj:
            obj = cls(**kwargs)
            obj.save()
            obj.handle_create()
        else:
            changes = {}
            for k, v in kwargs.iteritems():
                if getattr(obj, k, None) != v:
                    old = getattr(obj, k)
                    if (v is not None) and (old is not None) and (type(v) != type(old)):
                        to_type = type(old)
                        v = to_type(v)
                      
                    if old != v:
                        changes[k] = (old, v)
                        setattr(obj, k, v)
            if changes:
                obj.save()
                obj.handle_changes(changes)
        return obj

    def handle_create(self):
        """
        Вызывается после создания нового объекта
        """
        pass

    def handle_changes(self, changes):
        """
        Вызывается после изменения значения некоторых полей
        """
        pass   # переопределяется если нужно


class Phone(BaseModel):
    PRIMARY_KEY = 'phone'

    phone = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return unicode(self.phone)
    
    @property
    def fmt_retailer(self):
        retailer = self.retailers.first()
        if retailer:
            return retailer.fmt
        else:
            return '-'


class Retailer(BaseModel):
    PRIMARY_KEY = 'cian_id'

    cian_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    is_agent = models.BooleanField(default=False, blank=True)
    logo = models.CharField(max_length=512, blank=True, null=True)
    phones = models.ManyToManyField(Phone, blank=True, related_name='retailers')
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)

    def __unicode__(self):
        return unicode(self.cian_id)

    @property
    def phones_str(self):
        return ', '.join(map(lambda x: x.phone, self.phones.all()))

    @property
    def fmt(self):
        if not self.is_agent:
            return u'<b>НЕ АГЕНТ!</b>'
        else:
            result = ''
            if self.logo:
                result += u'<br /><img src="%s" style="max-height: 70px"/>' % self.logo
            if self.name:
                result += '<br />' + self.name
            return result


class RetailerAttribute(BaseModel):
    PRIMARY_KEY = ('retailer', 'key')

    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=1024)

    class Meta:
        unique_together = ('retailer', 'key')


class Offer(BaseModel):
    PRIMARY_KEY = 'cian_id'

    cian_id = models.IntegerField(unique=True)
    cian_user_id = models.IntegerField(blank=True, null=True)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, null=True, related_name='offers')
    price = models.IntegerField(null=True)  # rub
    price_usd = models.IntegerField(null=True)
    price_eur = models.IntegerField(null=True)
    is_paid = models.BooleanField(default=False, blank=True)
    is_premium = models.BooleanField(default=False, blank=True)
    is_top = models.BooleanField(default=False, blank=True)
    image = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=512)
    address = models.CharField(max_length=1024)
    is_moulage = models.BooleanField(blank=True, default=False)
    edited = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return unicode(self.cian_id)

    @property
    def fmt_price(self):
        return "{:,}".format(self.price)

    def handle_create(self):
        OfferPrice(offer=self, price=self.price).save()
        for broker_owner in self.phone.brokers.all():
            broker_owner.offers.add(self)
            broker_owner.add_notification('new_watching_offer', {'offer_id': self.id})

    def handle_changes(self, changes):
        if 'price' in changes:
            OfferPrice(offer=self, price=changes['price'][1]).save()

        if ('price' in changes) and ('price_usd' in changes) and ('price_eur' in changes):
            for broker in self.controled.all():
                broker.add_notification('control_price_changed', {'old': changes['price'][0], 'new': changes['price'][1], 'offer_id': self.id})

        if 'is_top' in changes:
            for broker in self.controled.all():
                broker.add_notification('control_istop_changed', {'old': changes['is_top'][0], 'new': changes['is_top'][1], 'offer_id': self.id})


class OfferAttribute(BaseModel):     # для всяких дополнительных мини-атрибутов
    PRIMARY_KEY = ('offer', 'key')

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=2048)

    class Meta:
        unique_together = ('offer', 'key')

    def __unicode__(self):
        return self.key


class OfferPrice(BaseModel):     # история цен
    PRIMARY_KEY = ('offer', 'key')

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='prices')
    price = models.IntegerField()
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)

    def __unicode__(self):
        return unicode(self.offer) + unicode(self.created_at)

    @property
    def fmt_price(self):
        return "{:,}".format(self.price)


class OffersFilter(BaseModel):
    PRIMARY_KEY = 'url'

    url = models.CharField(max_length=2048)
    max_pages = models.IntegerField(default=3)     # максимальное кол-во страниц серпа для парсинга
    query = models.TextField(blank=True, null=True)         # описание фильтров в виде url
    json_query = models.TextField(blank=True, null=True)   # описание фильтров в json
    offers_count = models.IntegerField(blank=True, null=True)   # den
    min_price = models.IntegerField(blank=True, null=True)  # den
    max_price = models.IntegerField(blank=True, null=True)  # den
    max_auction_bet = models.IntegerField(blank=True, null=True)
    is_updating = models.BooleanField(blank=True, default=True)
    watch_top3 = models.BooleanField(blank=True, default=False)
    our_max_auction_bet = models.IntegerField(blank=True, null=True)
    auction_step = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        if len(self.url) > 103:
            return '%d: ' % self.id + self.url[:100] + '...'
        else:
            return '%d: ' % self.id + self.url

    def handle_changes(self, changes):
        if 'min_price' in changes:
            for broker_filter in self.observed.all():
                broker_filter.broker.add_notification('filter_min_price_changed', {'old': changes['min_price'][0], 'new': changes['min_price'][1]}, offers_filter=self)
        if 'offers_count' in changes:
            for broker_filter in self.observed.all():
                broker_filter.broker.add_notification('filter_count_changed', {'old': changes['offers_count'][0], 'new': changes['offers_count'][1]}, offers_filter=self)

    @property
    def fmt_price(self):
        if self.min_price and self.max_price:
            return "{:,}".format(self.min_price) + ' - '"{:,}".format(self.max_price)
        else:
            return '-'

    @property
    def update_status(self):
        recent = self.updates.all().order_by('-created_at').first()
        if not recent:
            if self.is_updating:
                return u'Ожидает обновления'
            else:
                return u'Не обновляется'
        else:
            if recent.status == 'processing':
                return u'Обновляется сейчас'
            elif recent.status == 'error':
                return u'Произошла ошибка при обновлении =('
            elif recent.status == 'success':
                return u'Последнее обновление: %s' % pytils.dt.distance_of_time_in_words(recent.started_at)

    @property
    def update_status_html(self):
        """
        Используется в шаблоне в таблице, выводится юзеру
        """
        recent = self.updates.all().order_by('-created_at').first()
        text_color_class = ''
        icon_class = ''
        text=''
        if not recent:
            if self.is_updating:
                icon_class = 'fa fa-hourglass-start'
                text_color_class = 'text-info'
                text = u'Ожидание'
            else:
                icon_class = 'fa fa-times'
                text_color_class = 'text-warning'
                text = u'Не обновляется'
        else:
            if recent.status == 'waiting':
                icon_class = 'fa fa-hourglass-start'
                text_color_class = 'text-info'
                text = u'Ожидание'
            elif recent.status == 'processing':
                icon_class = 'fa fa-hourglass-end'
                text_color_class = 'text-info'
                text = u'Обновляется'
            elif recent.status == 'error':
                icon_class = 'fa fa-warning'
                text_color_class = 'text-danger'
                text = u'Произошла ошибка'
            elif recent.status == 'success':
                icon_class = 'fa fa-clock-o'
                text_color_class = 'text-success'
                text = u'Обновлено ' + pytils.dt.distance_of_time_in_words(recent.started_at)
            elif recent.status == 'retry':
                recent = self.updates.filter(status='success').order_by('-created_at').first()
                if recent:
                    icon_class = 'fa fa-clock-o'
                    text_color_class = 'text-success'
                    text = u'Обновлено ' + pytils.dt.distance_of_time_in_words(recent.started_at)
                else:
                    icon_class = 'fa fa-hourglass-start'
                    text_color_class = 'text-info'
                    text = u'Ожидание'

        return '<span class="%s %s"> %s</span>' % (icon_class, text_color_class, text)

    def offer_position_changed(self, offer_id):
        offer_position = OfferPosition.objects.filter(offer_id=offer_id, filter=self).first()
        if not offer_position:
            return None
        else:
            return offer_position.updated_at

    def get_feed_row(self):
        from office.models import Broker

        our_objects = [x['offer_id'] for x in Broker.offers.through.objects.filter(offer__is_top=True).values('offer_id')]
        our_positions = OfferPosition.objects.filter(offer_id__in=our_objects, filter=self, position__gt=0).order_by('position')
        return {
            'filter_name': self.observed.first().name,
            'filter_id': self.id,
            'max_auction_bet': self.max_auction_bet,
            'our_max_auction_bet': self.our_max_auction_bet,
            'our_positions': {p.position: p.offer.cian_id for p in our_positions},
            'auction_step': self.auction_step,
        }


class OfferPosition(BaseModel):
    PRIMARY_KEY = ('offer_id', 'filter_id')

    offer = models.ForeignKey(Offer,on_delete=models.CASCADE)
    filter = models.ForeignKey(OffersFilter,on_delete=models.CASCADE)
    position = models.IntegerField(default=0)  # если 0 - то не показывается, позиции идут от 1
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return str(self.id)

    def handle_changes(self, changes):
        if 'position' in changes:
            old = changes['position'][0]
            new = changes['position'][1]
            if self.offer.is_top and (old > 0) and (new > 0):
                return  # это всё не имеет смысла
            from office.models import BrokerFilter, Broker
            brokers_with_filter = set(map(lambda x:x['broker_id'], BrokerFilter.objects.filter(filter_id=self.filter_id).values('broker_id')))
            brokers_with_offer = set(map(lambda x:x['broker_id'], Broker.offers.through.objects.filter(offer_id=self.offer_id).values('broker_id')))
            brokers_with_controlled = set(map(lambda x:x['broker_id'], Broker.control_offers.through.objects.filter(offer_id=self.offer_id).values('broker_id')))

            for broker_id in brokers_with_filter & brokers_with_offer:
                broker = Broker.objects.get(id=broker_id)
                broker.add_notification('position_changed', {'old': old, 'new': new, 'offer_id': self.offer_id}, offers_filter=self.filter)
            for broker_id in brokers_with_filter & brokers_with_controlled:
                broker = Broker.objects.get(id=broker_id)
                broker.add_notification('control_position_changed', {'old': old, 'new': new, 'offer_id': self.offer_id}, offers_filter=self.filter)


class OffersUpdate(BaseModel):
    filter = models.ForeignKey(OffersFilter, on_delete=models.CASCADE, related_name='updates')
    status = models.CharField(max_length=16, choices=UPDATING_STATUSES, default='waiting', blank=True)
    priority = models.IntegerField(default=0, blank=True)  # чем больше, тем выше
    started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)

    def __unicode__(self):
        return str(self.id)

    @property
    def log_filename(self):
        return '%d_%d.txt' % (self.filter_id, self.id)

    def create_logger(self):
        if hasattr(self, 'logger'):
            return self.logger
        logger = logging.getLogger(__name__)
        filename = os.path.join(BASE_LOGS_DIR, self.log_filename)
        handler = logging.handlers.RotatingFileHandler(filename, maxBytes=10 * 1024 * 1024, backupCount=5)
        handler.setFormatter(LOGGING_FORMATTER)
        self.logger_handler = handler
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        self.logger = logger
        return logger

    def release_logger(self):
        if not hasattr(self, 'logger'):
            return
        self.logger_handler.close()
        self.logger.removeHandler(self.logger_handler)
        delattr(self, 'logger')
        delattr(self, 'logger_handler')

    @staticmethod
    def create_if_not_exists(offers_filter):
        if not OffersUpdate.objects.filter(filter=offers_filter, status='waiting').exists():
            OffersUpdate(filter=offers_filter).save()

    @staticmethod
    def update_queue():
        for offers_filter in OffersFilter.objects.filter(is_updating=True):
            OffersUpdate.create_if_not_exists(offers_filter)

    @staticmethod
    def run(sleep_time=60):
        while True:
            curr_task = OffersUpdate.objects.filter(status='waiting').order_by('-priority', 'created_at').first()
            if curr_task:
                logger = curr_task.create_logger()

                logger.info('Task %d started', curr_task.id)
                curr_task.status = 'processing'
                curr_task.started_at = datetime.now()
                curr_task.save()
                try:
                    is_ok = curr_task.go()
                    if is_ok:
                        curr_task.status = 'success'
                        curr_task.save()
                    else:
                        curr_task.status = 'retry'
                        curr_task.save()
                except KeyboardInterrupt:
                    logger.warning('KeyboardInterrupt on updating')
                    curr_task.status = 'waiting'
                    curr_task.save()
                except Exception as e:
                    logger.error('Update error')
                    logger.error(e)
                    logger.error(traceback.format_exc())
                    curr_task.status = 'error'
                    curr_task.save()
            else:
                print ('Waiting...')
                sleep(sleep_time)

    def go(self):
        from cian.working import run
        self.create_logger()
        result = run(self.filter.url, str(self.id), self.filter.max_pages, self.logger)
        self.release_logger()
        return result

