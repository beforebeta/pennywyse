from haystack import indexes
from core.models import Coupon, Merchant

class CouponIndex(indexes.SearchIndex, indexes.Indexable):
    merchant_name = indexes.CharField(null=True)
    text = indexes.CharField(document=True, model_attr='description', null=True)
    code = indexes.CharField(model_attr='code', null=True)
    start = indexes.DateTimeField(model_attr='start', null=True)
    end = indexes.DateTimeField(model_attr='end', null=True)
    link = indexes.CharField(model_attr='link', null=True)
    skimlinks = indexes.CharField(model_attr='skimlinks', null=True)
    image = indexes.CharField(model_attr='image', null=True)
    merchant_image = indexes.CharField(model_attr='merchant__get_image', null=True)
    short_desc = indexes.CharField(model_attr='short_desc', null=True)
    date_added = indexes.DateTimeField(model_attr='date_added', null=True)
    merchant_local_path = indexes.CharField(model_attr='merchant__local_path', null=True)
    success_path = indexes.CharField(null=True)
    merchant_id = indexes.IntegerField(model_attr='merchant__id', null=True)

    def get_model(self):
        return Coupon

    def index_queryset(self, using=None):
        return self.get_model().active_objects

    def prepare_success_path(self, obj):
        if obj.merchant:
            return obj.success_path()
        return

class MerchantIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    name_slug = indexes.CharField(model_attr='name_slug', null=True)
    image = indexes.CharField(model_attr='get_image', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    coupon_count = indexes.IntegerField(model_attr='coupon_count', null=True)
    link = indexes.CharField(model_attr='link', null=True)
    local_path = indexes.CharField(model_attr='local_path', null=True)

    def get_model(self):
        return Merchant