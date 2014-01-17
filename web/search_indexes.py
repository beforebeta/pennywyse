from haystack import indexes
from core.models import Coupon, Merchant, CityPicture

class CouponIndex(indexes.SearchIndex, indexes.Indexable):
    merchant_name = indexes.CharField(null=True)
    text = indexes.CharField(document=True, model_attr='description', null=True)
    code = indexes.CharField(model_attr='code', null=True)
    start = indexes.DateTimeField(model_attr='start', null=True)
    end = indexes.DateTimeField(model_attr='end', null=True)
    link = indexes.CharField(model_attr='link', null=True)
    skimlinks = indexes.CharField(model_attr='skimlinks', null=True)
    image = indexes.CharField(model_attr='image', null=True)
    merchant_image = indexes.CharField(model_attr='merchant__image', null=True)
    short_desc = indexes.CharField(model_attr='short_desc', null=True)
    date_added = indexes.DateTimeField(model_attr='date_added', null=True)
    merchant_local_path = indexes.CharField(model_attr='merchant__local_path', null=True)
    success_path = indexes.CharField(null=True)
    full_success_path = indexes.CharField(null=True, model_attr='full_success_path')
    merchant_id = indexes.IntegerField(model_attr='merchant__id', null=True)
    coupon_type = indexes.CharField(model_attr='coupon_type', null=True)
    is_new = indexes.BooleanField(model_attr='is_new', null=True)
    is_popular = indexes.BooleanField(model_attr='is_popular', null=True)

    def get_model(self):
        return Coupon

    def index_queryset(self, using=None):
        return self.get_model().active_objects



class LocalCouponIndex(CouponIndex):
    coupon_ref_id           = indexes.IntegerField(model_attr='ref_id', null=True)
    embedly_title           = indexes.CharField(model_attr='embedly_title', null=True)
    embedly_description     = indexes.CharField(model_attr='embedly_description', null=True)
    restrictions            = indexes.CharField(model_attr='restrictions', null=True)
    directlink              = indexes.CharField(model_attr='directlink', null=True)
    price                   = indexes.FloatField(model_attr='price', null=True)
    listprice               = indexes.FloatField(model_attr='listprice', null=True)
    discount                = indexes.FloatField(model_attr='discount', null=True)
    percent                 = indexes.IntegerField(model_attr='percent', null=True)
    merchant_location       = indexes.LocationField(model_attr='merchant_location__get_location', null=True)
    online                  = indexes.BooleanField(model_attr='online', null=True)
    lastupdated             = indexes.DateTimeField(model_attr='lastupdated', null=True)
    mobilequery             = indexes.CharField(use_template=True, null=True)
    provider_slug           = indexes.CharField(model_attr='coupon_network__code', null=True)
    provider                = indexes.CharField(model_attr='coupon_network__name', null=True)
    category_slugs          = indexes.MultiValueField(null=True)
    categories              = indexes.MultiValueField(null=True)
    is_duplicate            = indexes.BooleanField(model_attr='is_duplicate', null=True)
    status                  = indexes.CharField(model_attr='status', null=True)
    merchant_ref_id         = indexes.IntegerField(model_attr='merchant__ref_id', null=True)
    merchant_name           = indexes.CharField(model_attr='merchant__name', null=True)
    merchant_link           = indexes.CharField(model_attr='merchant__link', null=True)
    merchant_address        = indexes.CharField(model_attr='merchant_location__address', null=True)
    merchant_locality       = indexes.CharField(model_attr='merchant_location__locality', null=True)
    merchant_region         = indexes.CharField(model_attr='merchant_location__region', null=True)
    merchant_postal_code    = indexes.CharField(model_attr='merchant_location__postal_code', null=True)
    related_deals_count     = indexes.IntegerField(null=True)

    def get_model(self):
        return Coupon

    def index_queryset(self, using=None):
        return self.get_model().all_objects.filter(ref_id_source='sqoot')

    def prepare_categories(self, obj):
        return [c.name for c in obj.categories.all()]

    def prepare_category_slugs(self, obj):
        return [c.code for c in obj.categories.all()]

    def prepare_related_deals_count(self, obj):
        return Coupon.all_objects.filter(related_deal=obj).count()

class CityPictureIndex(indexes.SearchIndex, indexes.Indexable):
    text            = indexes.CharField(document=True, model_attr='name', null=True)
    geometry        = indexes.LocationField(model_attr='geometry', null=True)
    picture_url     = indexes.CharField(model_attr='picture_url', null=True)
    radius          = indexes.IntegerField(model_attr='radius', null=True)

    def get_model(self):
        return CityPicture

class MerchantIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name')
    name_slug = indexes.CharField(model_attr='name_slug', null=True)
    image = indexes.CharField(model_attr='image', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    coupon_count = indexes.IntegerField(model_attr='coupon_count', null=True)
    total_coupon_count = indexes.IntegerField(model_attr='total_coupon_count', null=True)
    link = indexes.CharField(model_attr='link', null=True)
    local_path = indexes.CharField(model_attr='local_path', null=True)

    def get_model(self):
        return Merchant
