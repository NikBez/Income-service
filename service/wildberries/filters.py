from django_filters import FilterSet
from models import WBPayment

class PVZFilter(FilterSet):
    class Meta:
        model = WBPayment
        fields = ['pvz_id__title']


