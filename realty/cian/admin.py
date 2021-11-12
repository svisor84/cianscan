# -*- coding: utf-8 -*-

from django.contrib import admin
from cian import models
from office.admin import BrokerFilterInline


def link(url, content):
    return '<a href="%s" target="_blank">%s</a>' % (url, content)


def img_preview(src, url, height=100):
    return link(url, '<img src="%s" style="max-height: %dpx" /></a>' % (src, height))


def url_to_update_log(filename):
    return u'<a href="%s%s" target="_blank">Download &rarr;</a>' % ('/updates_logs/', filename)


class OfferAttributeInline(admin.TabularInline):
    model = models.OfferAttribute
    extra = 1
    readonly_fields = ('key', 'value')


class OfferPriceInline(admin.TabularInline):
    model = models.OfferPrice
    extra = 1
    ordering = ('created_at', )


class RetailerAttributeInline(admin.TabularInline):
    model = models.RetailerAttribute
    can_delete = True
    extra = 0
    readonly_fields = ('key', 'value')


class OfferPositionInline(admin.TabularInline):
    model = models.OfferPosition
    can_delete = True
    extra = 0
    raw_id_fields = ('offer', )
    readonly_fields = ('is_top', )
    ordering = ('position', )

    def is_top(self, obj):
        if obj:
            if obj.position != 0:
                if obj.offer.is_top:
                    return u'ДА'
                else:
                    return u'нет'
            else:
                return '-'
    is_top.short_description = 'is top'


class OfferInline(admin.TabularInline):
    model = models.Offer
    can_delete = True
    extra = 0
    fields = ('cian_id', 'photo', 'price', 'is_paid', 'is_premium', 'is_top', 'url', 'address')
    readonly_fields = ('cian_id', 'photo', 'price', 'is_paid', 'is_premium', 'is_top', 'url', 'address')

    def photo(self, obj):
        if obj and obj.image:
            return img_preview(obj.image, obj.url)
        elif obj and obj.url:
            return link(obj.url, '&rarr;')
    photo.short_description = 'link'
    photo.allow_tags = True


class RetailerPhoneInline(admin.TabularInline):
    model = models.Retailer.phones.through
    can_delete = True
    extra = 0
    raw_id_fields = ('retailer', )
    readonly_fields = ('phone', )


class RetailerAdmin(admin.ModelAdmin):
    inlines = (RetailerPhoneInline, RetailerAttributeInline)
    list_display = ('cian_id', 'name', 'phones_str', 'created_at')
    fields = ('cian_id', 'name', 'created_at')
    readonly_fields = ('created_at', )

    def phones_str(self, obj):
        if obj:
            return obj.phones_str


class OfferAdmin(admin.ModelAdmin):
    inlines = (OfferPriceInline, OfferAttributeInline, OfferPositionInline)
    list_display = ('cian_id', 'photo', 'price', 'phone', 'is_paid', 'is_premium', 'is_top', 'is_moulage', 'viewers_count', 'edited', 'created_at')
    search_fields = ('cian_id', )
    raw_id_fields = ('phone',)
    ordering = ('-created_at',)

    def viewers_count(self, obj):
        if obj:
            return obj.viewers.count()

    def photo(self, obj):
        if obj and obj.image:
            return img_preview(obj.image, obj.url)
        elif obj and obj.url:
            return link(obj.url, '&rarr;')
    photo.short_description = 'link'
    photo.allow_tags = True


class OffersFilterAdmin(admin.ModelAdmin):
    inlines = (BrokerFilterInline, )
    list_display = ('id', 'max_pages', 'min_price', 'max_price', 'offers_count', 'is_updating', 'watch_top3', 'max_auction_bet', 'our_max_auction_bet', 'created_at', 'url')
    list_filter = ('is_updating', 'watch_top3')
    readonly_fields = ('id', 'name', 'created_at', 'updated_at', 'offers_count', 'max_price', 'max_auction_bet')
    fields = [
        'id', 'name', 'watch_top3', 'our_max_auction_bet', 'auction_step',
        'url', 'max_pages', 'is_updating',
        'offers_count', 'max_price', 'max_auction_bet', 'created_at', 'updated_at',
    ]

    def name(self, obj):
        if obj and obj.id:
            try:
                return obj.observed.first().name
            except Exception:
                pass
        return '-'


class OffersUpdateAdmin(admin.ModelAdmin):
    list_display = ('filter', 'status', 'created_at', 'started_at')
    list_filter = ('status', 'filter')
    raw_id_fields = ('filter', )
    readonly_fields = ('download_log_link', )

    def download_log_link(self, obj):
        if obj and obj.id:
            return url_to_update_log(obj.log_filename)

    download_log_link.short_description = u'Full log'
    download_log_link.allow_tags = True


class OfferPositionAdmin(admin.ModelAdmin):
    list_display = ('filter', 'offer', 'position', 'created_at', 'updated_at')


class OfferPriceAdmin(admin.ModelAdmin):
    list_display = ('offer', 'price', 'created_at')
    readonly_fields = ('created_at', )
    ordering = ('offer', 'created_at')


class PhoneAdmin(admin.ModelAdmin):
    inlines = (RetailerPhoneInline, OfferInline)
    list_display = ('phone', 'retailers_count', 'offers_count')

    def retailers_count(self, obj):
        if obj:
            return obj.retailers.count()

    def offers_count(self, obj):
        if obj:
            return obj.offers.count()


admin.site.register(models.Retailer, RetailerAdmin)
admin.site.register(models.Offer, OfferAdmin)
admin.site.register(models.OffersFilter, OffersFilterAdmin)
admin.site.register(models.OffersUpdate, OffersUpdateAdmin)
admin.site.register(models.Phone, PhoneAdmin)
admin.site.register(models.OfferPosition, OfferPositionAdmin)
admin.site.register(models.OfferPrice, OfferPriceAdmin)
