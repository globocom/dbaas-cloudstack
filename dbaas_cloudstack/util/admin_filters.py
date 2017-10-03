from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
import collections

class BaseGroupFilter(admin.SimpleListFilter):

    title = 'filter_title'

    parameter_name = 'filter'

    filter_option_queryset = None

    def lookups(self, request, model_admin):

        if not isinstance(self.filter_option_queryset, collections.Iterable):
            raise ImproperlyConfigured("filter_option_queryset is supposed to be an Iterable")
        if not isinstance(self.filter_option_queryset[0], tuple):
            raise ImproperlyConfigured("filter_option_queryset is supposed to have tuples as elements")

        tuple_list = self.filter_option_queryset

        return (
            set(tuple_list)
        )

    def queryset(self, request, queryset):

        if not self.value():
            return

        acceptable_ids = self.get_acceptable_ids(self.value)

        return queryset.filter(id__in=set(acceptable_ids))

    def get_acceptable_ids(self, value):
        pass