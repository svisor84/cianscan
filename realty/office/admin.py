# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from . import models


class BrokerFilterInline(admin.TabularInline):
    model = models.BrokerFilter
    can_delete = True
    extra = 0
    raw_id_fields = ('filter', )


class NotificationInline(admin.TabularInline):
    model = models.Notification
    can_delete = True
    extra = 0
    raw_id_fields = ('offers_filter', )


class BrokerAdmin(admin.ModelAdmin):
    inlines = (BrokerFilterInline, )
    list_display = ('user', 'phone', 'offers_count', 'filters_count', 'notifications_count', 'created_at')
    raw_id_fields = ('offers', 'phone', 'control_offers')

    def offers_count(self, obj):
        if obj:
            return obj.offers.count()

    def filters_count(self, obj):
        if obj:
            return obj.filters.count()

    def notifications_count(self, obj):
        if obj:
            return obj.notifications.filter(is_viewed=False).count()


class BrokerFilterAdmin(admin.ModelAdmin):
    list_display = ('broker', 'name', 'filter', 'created_at')
    raw_id_fields = ('filter', )


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('broker', 'type', 'fmt_values', 'message', 'offers_filter', 'is_viewed')
    list_filter = ('is_viewed', 'type')
    raw_id_fields = ('offers_filter', )
    readonly_fields = ('fmt_values', )

    def fmt_values(self, obj):
        if obj:
            return obj.fmt_values
    fmt_values.allow_tags=True


admin.site.register(models.Broker, BrokerAdmin)
admin.site.register(models.BrokerFilter, BrokerFilterAdmin)
admin.site.register(models.Notification, NotificationAdmin)
