# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import pytils

from cian.models import BaseModel, Offer, OffersFilter, Phone, OfferPosition, OffersUpdate


NOTIFICATION_TYPES = [
    ('default', u'Простое'),
    ('filter_min_price_changed', u'Изменилась минимальная цена'),
    ('filter_count_changed', u'Изменилось количество объектов'),
    ('position_changed', u'Изменилась позиция вашего объекта'),
    ('new_watching_offer', u'Добавлен объект для наблюдения'),
    ('control_position_changed', u'Изменилась позиция объекта на контроле'),
    ('control_price_changed', u'Изменилась цена объекта на контроле'),
    ('control_istop_changed', u'Изменение ТОП статус у объекта на котроле'),
]


class Broker(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, blank=True, null=True, related_name='broker')    # django user
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, blank=True, null=True, related_name='brokers')
    offers = models.ManyToManyField(Offer, blank=True, related_name='viewers')  # его собственные офферы
    control_offers = models.ManyToManyField(Offer, blank=True, related_name='controled')  # офферы на особом контроле
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    def __unicode__(self):
        return self.user.username

    def get_offer_ids(self):
        return map(lambda x: x['offer_id'], Broker.offers.through.objects.filter(broker=self).values('offer_id'))

    def get_top_offer_ids(self):
        return map(lambda x: x['offer_id'], Broker.offers.through.objects.filter(broker=self, offer__is_top=True).values('offer_id'))

    def get_control_ids(self):
        return map(lambda x: x['offer_id'], Broker.control_offers.through.objects.filter(broker=self).values('offer_id'))

    def get_filters_ids(self):
        return map(lambda x: x['filter_id'], BrokerFilter.objects.filter(broker=self).values('filter_id'))

    def get_filter_positions(self):
        """
        Возвращает позиции офферов брокера по всем его фильтрам
        """
        offer_filters_ids = self.get_filters_ids()
        result = {filter_id: [] for filter_id in offer_filters_ids}
        top_offer_ids = set(self.get_top_offer_ids())
        for op in OfferPosition.objects.filter(filter_id__in=offer_filters_ids, offer_id__in=self.get_offer_ids()):
            result[op.filter_id].append(op)

        def get_positions_str(offer_positions):
            filter_result = []
            for op in offer_positions:
                if op.offer_id in top_offer_ids:
                    filter_result.append(u'ТОП')
            for op in offer_positions:
                if op.position > 0:
                    filter_result.append(str(op.position))
            lose_offers_count = 0
            for op in offer_positions:
                if op.position == 0:
                    lose_offers_count += 1
            if lose_offers_count:
                if lose_offers_count == 1:
                    filter_result.append(u'Один объект вышел из выдачи')
                else:
                    filter_result.append(u'Вышедших объектов: %d' % lose_offers_count)
            return ', '.join(filter_result)

        return {k: get_positions_str(v) for k, v in result.iteritems()}

    def get_offers_positions(self, offers_ids=None):
        """
        Возвращает позиции в фильтрах брокера по всем его офферам
        """
        if not offers_ids:
            offers_ids = self.get_offer_ids()
        result = {offer_id: {} for offer_id in offers_ids}
        for op in OfferPosition.objects.filter(filter_id__in=self.get_filters_ids(), offer_id__in=offers_ids):
            result[op.offer_id][op.filter_id] = op.position
        return result

    def get_notification_summary(self):
        result = {} # broker_filter_id: (all, new)
        for broker_filter in self.filters.all():
            notifications = Notification.objects.filter(broker=self, offers_filter_id=broker_filter.filter_id)
            result[broker_filter.id] = (notifications.count(), notifications.filter(is_viewed=False).count())
        return result

    def get_new_filters_notifications(self):
        result = {}  # broker_filter_id: (all, new)
        for broker_filter in self.filters.all():
            notifications = Notification.objects.filter(broker=self, offers_filter_id=broker_filter.filter_id)
            result[broker_filter.id] = map(lambda n: n.fmt_message, notifications.order_by('-created_at'))
        return result

    def add_notification(self, type_, values, message=None, offers_filter=None):
        Notification(broker=self, type=type_, values=values, message=message, offers_filter=offers_filter).save()

    def filter_id_to_name_map(self):
        return {int(x.filter_id): x.name for x in BrokerFilter.objects.filter(broker=self)}

    def update_phone(self, new_phone):
        if not new_phone:
            return u'Введите телефон'
        new_phone = new_phone.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')
        if not unicode(new_phone).isnumeric() or len(new_phone) != 11:
            return u'Телефон вводится в формате 7 и дальше 10 цифр'
        self.phone = Phone.upsert(phone=new_phone)
        self.save()
        self.offers = self.phone.offers.all()


class Notification(BaseModel):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=32, choices=NOTIFICATION_TYPES, default='default', blank=True)
    values = models.CharField(max_length=1024, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_viewed = models.BooleanField(default=False, blank=True)
    offers_filter = models.ForeignKey(OffersFilter, on_delete=models.CASCADE,  blank=True, null=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)

    @property
    def fmt_date(self):
        text = self.created_at.strftime('%d.%m.%Y %H:%M')
        if self.is_viewed:
            return text
        else:
            return '<b>%s</b>' % text

    @property
    def fmt_values(self):
        values = eval(str(self.values))
        if not values:
            return ''
        if values.get('offer_id'):
            offer_id = values.get('offer_id')
            offer = Offer.objects.get(id=offer_id)
            result = u'Объект ' + '<a href="/offer/%s/"> %s</a>. ' % (offer_id, offer.cian_id)
        else:
            result = ''
        if values.get('old') is not None and values.get('new') is not None:
            if u'position_changed' in self.type:
                if values['old'] == 0:
                    result += u'<b>Вошёл</b> в выдачу под номером <b>%s</b>' % values['new']
                    is_up = True
                elif values['new'] == 0:
                    result += u'<b>Вышел</b> из выдачи. Был под номером <b>%s</b>' % values['old']
                    is_up = False
                else:
                    result += u'Было: <b>%s</b>, стало: <b>%s</b> ' % (values['old'], values['new'])
                    is_up = values['old'] > values['new']
            elif u'istop_changed' in self.type:
                if values['new'] == True:
                    result += u'<b>Вошёл</b> в ТОП'
                    is_up = True
                else:
                    result += u'<b>Вышел</b> из ТОП'
                    is_up = False
            else:
                result += u'Было: <b>%s</b>, стало: <b>%s</b> ' % (values['old'], values['new'])
                is_up = values['old'] < values['new']

            if is_up:
                result += ' <i class="fa fa-arrow-up"> </i> '
            else:
                result += ' <i class="fa fa-arrow-down"> </i> '
        elif values.get('new'): # не должно быть такого на самом деле
            result += u'Cтало: <b>%s</b> ' % values['new']
        return result

    @property
    def fmt_message(self):
        if self.message:
            return self.message
        else:
            return self.get_type_display() + '. ' + self.fmt_values

    @property
    def filter_ordering(self):
        """
        Возвращает тип, по которому нужно сортировать фильтр чтобы нужные объекты были сверху 
        """
        ordering = {
            'filter_min_price_changed': 'price',
            'filter_count_changed': 'changed_at',
        }
        return ordering.get(self.type)


class BrokerFilter(BaseModel):
    PRIMARY_KEY = ('broker', 'filter')

    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='filters')
    filter = models.ForeignKey(OffersFilter, on_delete=models.CASCADE, related_name='observed')
    name = models.CharField(max_length=256)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('broker', 'filter')

    def set_notifications_viewed(self):
        Notification.objects.filter(broker=self.broker, offers_filter_id=self.filter_id, is_viewed=False).update(is_viewed=True)

    def to_delete(self):
        brokers_count = self.filter.observed.count()
        if brokers_count == 1:
            self.filter.is_updating = False
            self.filter.save()

        Notification.objects.filter(broker=self.broker, offers_filter_id=self.filter_id).delete()
        self.delete()

    @classmethod
    def create(cls, broker, name, url):
        offers_filter = OffersFilter.upsert(url=url, is_updating=True)
        broker_filter = BrokerFilter.upsert(broker=broker, filter=offers_filter, name=name)
        OffersUpdate.create_if_not_exists(offers_filter)
        return broker_filter

    @property
    def control_offers_count(self):
        return OfferPosition.objects.filter(filter=self.filter, offer__in=self.broker.control_offers.all()).count()
