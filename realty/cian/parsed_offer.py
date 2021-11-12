# -*- coding: utf-8 -*-

from datetime import datetime
from models import OffersFilter, Offer, Retailer, RetailerAttribute, Phone, OfferAttribute, OfferPosition


class Parsed(object):
    MAP_TO_FIELDS = {}
    MAP_TO_FUNC = {}
    SKIP_ATTRS = set()

    def __init__(self):
        self.attributes = {}
        self.logger = None

    def set_logger(self, logger):
        self.logger = logger

    def go(self, data_dict):
        self.attributes = {}
        for k, v in data_dict.iteritems():
            if k in self.MAP_TO_FIELDS:
                setattr(self, self.MAP_TO_FIELDS[k], v)
            elif k in self.MAP_TO_FUNC:
                getattr(self, self.MAP_TO_FUNC[k])(v)
            elif (k not in self.SKIP_ATTRS) and (v is not None):
                self.attributes[k] = v

    def print_field(self, field):
        value = getattr(self, field)
        field_type = type(value)
        if field_type == list:
            print (' ' * 4, field)
            for v in value:
                print (' ' * 8, v)
        elif field_type == dict:
            print (' ' * 4, field)
            for k, v in value.iteritems():
                print (' ' * 8, k, ': ', v)
        else:
            print ('    ', field, '->', getattr(self, field))

    def print_attributes(self):
        for k, v in self.attributes.iteritems():
            print ((' ' * 4, k, ': ', v))

    def print_data(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError


class ParsedRetailer(Parsed):
    MAP_TO_FIELDS = {
        'cianUserId': 'cian_id',
        'agencyName': 'name',
        'isAgent': 'is_agent',
        'agentAvatarUrl': 'logo',
    }
    MAP_TO_FUNC = {
        'phoneNumbers': 'parse_phone',
    }
    SKIP_ATTRS = ['isHidden', ]

    def __init__(self):
        super(ParsedRetailer, self).__init__()
        self.cian_id = None
        self.name = None
        self.is_agent = None
        self.logo = None
        self.phones = []

    def parse_phone(self, phones_list):
        self.phones = []
        for phone in phones_list:
            self.phones.append(phone['countryCode'].replace('+', '') + phone['number'])

    def print_data(self):
        print ('*'*30 + self.__class__.__name__ + '*'*30)
        print ('Fields:')
        for field in ['cian_id', 'name', 'phones']:
            self.print_field(field)
        print ('Attributes:')
        self.print_attributes()

    def export(self):
        fields = {key: getattr(self, key) for key in ['cian_id', 'name', 'is_agent', 'logo']}
        retailer = Retailer.upsert(**fields)

        for k, v in self.attributes.iteritems():
            try:
                RetailerAttribute.upsert(retailer=retailer, key=k, value=v)
            except:
                pass

        phones_objs = []
        for phone in self.phones:
            phones_objs.append(Phone.upsert(phone=phone))
        retailer.phones = phones_objs

        return retailer


class ParsedOffer(Parsed):
    MAP_TO_FIELDS = {
        'cianId': 'cian_id',
        'isPremium': 'is_premium',
        'isTop3': 'is_top',
        'isPaid': 'is_paid',
        'description': 'description',
        'addedTimestamp': 'added_timestamp',
        'editDate': 'edit_date',
        'fullUrl': 'url',
        'userId': 'cian_user_id'
    }
    MAP_TO_FUNC = {
        'user': 'parse_retailer',
        'photos': 'parse_image',
        'bargainTerms': 'parse_price',  # возможно тут есть ещё важная инфа
        'geo': 'parse_address',         # возможно тут есть ещё важная инфа
        'building': 'parse_building',
        'phones': 'parse_phone',
    }
    SKIP_ATTRS = {'humanizedTimedelta', 'exportPdfLink', 'status', 'gaLabel', 'specialty', 'categoriesIds',
                  'newbuilding', 'added', 'exportDocLink', 'publishTerms', 'isColorized', 'isImported',
                  'isRecidivist', 'descriptionWordsHighlighted', 'videos', 'id', 'notes', 'objectGuid',
                  'windowsViewType', 'flags', 'repairType', 'jkUrl', 'category', 'isExcludedFromAction',
                  'isMulti', 'isFavorite', 'publishedUserId'}

    def __init__(self):
        super(ParsedOffer, self).__init__()
        self.cian_id = None
        self.price = None   # в рублях
        self.price_usd = None
        self.price_eur = None
        self.is_paid = None
        self.is_premium = None
        self.is_top = None
        self.image = None
        self.description = None
        self.url = None
        self.added_timestamp = None
        self.edit_date = None
        self.retailer = None
        self.address = None
        self.cian_user_id = None
        self.phone = None

    def parse_retailer(self, user_dict):
        self.retailer = ParsedRetailer()
        self.retailer.go(user_dict)

    def parse_image(self, photos):
        if photos:
            self.image = photos[0]['thumbnail2Url']

    def parse_price(self, bargain_terms):
        self.price = bargain_terms.get('priceRur')
        self.price_usd = bargain_terms.get('priceUsd')
        self.price_eur = bargain_terms.get('priceEur')

    def parse_address(self, geo):
        self.address = geo['userInput']

    def parse_phone(self, phones):
        if phones:
            phone = phones[0]
            self.phone = phone['countryCode'].replace('+', '') + phone['number']

    def parse_building(self, building):
        self.attributes['building'] = u'; '.join([u'%s: %s' % (k, v) for k, v in building.iteritems() if v is not None])

    def print_data(self):
        print ('')
        print ('*'*30 + self.__class__.__name__ + '*'*30)
        print ('Fields:')
        for field in ['cian_id', 'url', 'price', 'address', 'is_paid', 'is_premium', 'is_top', 'image', 'description', 'added_timestamp', 'edit_date']:
            self.print_field(field)
        print ('\nAttributes:')
        self.print_attributes()
        print ('\nRetailer:')
        self.retailer.print_data()

    def export(self):
        retailer = self.retailer.export()
        fields = {key: getattr(self, key) for key in ['cian_id', 'url', 'price', 'price_usd', 'price_eur', 'address', 'is_paid', 'is_premium', 'is_top', 'image', 'description', 'cian_user_id']}
        if self.edit_date:
            fields['edited'] = datetime.strptime(self.edit_date.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            fields['edited'] =datetime.fromtimestamp(self.added_timestamp)
        fields['phone'] = Phone.upsert(phone=self.phone)
        offer = Offer.upsert(**fields)

        for k, v in self.attributes.iteritems():
            try:
                OfferAttribute.upsert(offer=offer, key=k, value=v)
            except Exception:
                pass

        return offer


class ParsedList(Parsed):
    MAP_TO_FIELDS = {
        'totalOffers': 'offers_count',
        'jsonQuery': 'json_query',
        'queryString': 'query',
    }
    MAP_TO_FUNC = {
        'offers': 'parse_offers'
    }

    def __init__(self, url):
        super(ParsedList, self).__init__()
        self.url = url
        self.offers_count = None
        self.json_query = None
        self.query = None
        self.offers = []
        self.max_auction_bet = None

    def parse_offers(self, offers_list):
        for offer in offers_list:
            offer_obj = ParsedOffer()
            offer_obj.go(offer)
            self.offers.append(offer_obj)

    def print_data(self):
        print ('*'*30 + self.__class__.__name__ + '*'*30)
        print ('\nFields:')
        for field in ['url', 'offers_count', 'json_query', 'query']:
            self.print_field(field)
        #print ('\nOffers:')
        #for offer in self.offers:
        #    offer.print_data()

    def export(self):
        if not self.offers:
            self.logger.info('Empty offers. Break.')
            return

        self.logger.info('Export...')

        object_fields = {key: getattr(self, key) for key in ['url', 'offers_count', 'json_query', 'query']}
        offers_filter = OffersFilter.upsert(**object_fields)

        positions = []
        shift = 0
        #is_top_section = True
        #self.print_data()

        min_price = max_price = None

        for pos, offer in enumerate(self.offers):
            #if is_top_section and (offer.is_top):
            #    continue
            #if is_top_section and (not offer.is_top):
            #    is_top_section = False
            #    shift = pos

            position_result = pos - shift + 1
            if position_result > self.offers_count:
                self.logger.info('Skip other positions')
                break

            offer_obj = offer.export()
            if not offer_obj.is_moulage:
                if not min_price or offer_obj.price < min_price:
                    min_price = offer_obj.price
                if not max_price or offer_obj.price > max_price:
                    max_price = offer_obj.price

            self.logger.info('Position %d: Offer %s, %s', position_result, offer_obj, 'is_top' if offer.is_top else '-')
            posit = OfferPosition.upsert(offer_id=offer_obj.id, filter_id=offers_filter.id, position=position_result)
            positions.append(posit.id)

        OffersFilter.upsert(url=self.url, min_price=min_price, max_price=max_price, max_auction_bet=self.max_auction_bet)
        for op in OfferPosition.objects.filter(filter=offers_filter).exclude(id__in=positions): # те что вышли из выдачи
            op.upsert(offer_id=op.offer_id, filter_id=offers_filter.id, position=0)

        return offers_filter
