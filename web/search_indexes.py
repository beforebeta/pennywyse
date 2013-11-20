from haystack import indexes
from core.models import Coupon, Merchant

class CouponIndex(indexes.SearchIndex, indexes.Indexable):
    merchant_name = indexes.CharField(model_attr='merchant.name')
    text = indexes.CharField(document=True, model_attr='description')
    code = indexes.CharField(model_attr='code', null=True)
    start = indexes.DateTimeField(model_attr='start', null=True)
    end = indexes.DateTimeField(model_attr='end', null=True)
    link = indexes.CharField(model_attr='link', null=True)
    skimlinks = indexes.CharField(model_attr='skimlinks', null=True)
    image = indexes.CharField(model_attr='image', null=True)
    short_desc = indexes.CharField(model_attr='short_desc', null=True)

    def get_model(self):
        return Coupon

class MerchantIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    name_slug = indexes.CharField(model_attr='name_slug', null=True)
    image = indexes.CharField(model_attr='image', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    coupon_count = indexes.IntegerField(model_attr='coupon_count', null=True)
    link = indexes.CharField(model_attr='link', null=True)

    def get_model(self):
        return Merchant