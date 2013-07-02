from django.db import models

class Category(models.Model):
    ref_id          = models.CharField(max_length=255, db_index=True)
    code            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    name            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    description     = models.CharField(max_length=255,blank=True, null=True)
    parent          = models.ForeignKey("Category", blank=True, null=True)

class DealType(models.Model):
    code            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    name            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    description     = models.CharField(max_length=255,blank=True, null=True)

class Merchant(models.Model):
    ref_id          = models.CharField(max_length=255, db_index=True)
    name            = models.CharField(max_length=255, db_index=True)

class CouponNetwork(models.Model):
    name            = models.CharField(max_length=255, db_index=True)

class Country(models.Model):
    code            = models.CharField(max_length=255, db_index=True)
    name            = models.CharField(max_length=255, db_index=True)

class Coupon(models.Model):
    """
    CouponID - Our proprietary coupon ID - especially useful in identifying deals that are delivered more than once because they have changed.
    MerchantName
    MerchantID
    Network
    Label - The main description text the merchant describes the deal with. May be have been modified to fix typos.
    Restrictions - Any information the merchant provides regarding any restrictions relating to how the coupon can be redeemed. May have been modified to fix typos.
    CouponCode - If the coupon requires the user to enter a code, it is in this field. Any deal with a code will also contain "coupon" in the DealTypes field.
    StartDate
    EndDate
    Link - This is the actual affiliate link used to go to the merchant's landing page and set the appropriate network cookies with your affiliate info. It requires that you have inserted your affiliate IDs in the Feed Settings. NOTE: For deals marked "coupon" in the DealTypes field (below) this link may be required in order to activate the deal.
    DirectLink - This field is deprecated, please ignore it. It remains for backward compatibility.
    Categories        (Multiple values are seperatated by commas)
    DealTypes        (Multiple values are seperatated by commas)
    Image
    Status - The status should always be checked, and only "active" deals should be displayed (regardless of expiration date). The status is critical to tell if the deal is currently valid. Values may be: active - Deal is live and may be displayed; deleted - Deal was deleted or otherwise invalidated - ignore other values and remove deal; suspended - The merchant was deactivated in the network so this deal may not be paybale; or expired - The deal expired normally.
    LastUpdated - When this deal was last modified in the system.
    ErrorReportURL   (Optional, Turn on/off on Manage Feed Settings page)
    ChangeAudit      (Optional, Turn on/off on Manage Feed Settings page)
    Created      (When this deal was added to the system)
    Country      (Countries of the deal)
    Price      (Product Price, not applied to all deals)
    List Price      (Product List Price, not applied to all deals)
    Discount      (Product Discount, not applied to all deals)
    Percent      (Product Discount Percent, not applied to all deals)
    """
    #Our proprietary coupon ID - especially useful in identifying deals that are delivered more than once because they have changed.
    ref_id          = models.CharField(max_length=255, db_index=True)
    merchant        = models.ForeignKey(Merchant, blank=True, null=True)
    categories      = models.ManyToManyField(Category, blank=True, null=True)
    dealtypes       = models.ManyToManyField(DealType, blank=True, null=True)
    #The main description text the merchant describes the deal with. May be have been modified to fix typos.
    description     = models.TextField(blank=True, null=True)
    #Any information the merchant provides regarding any restrictions relating to how the coupon can be redeemed. May have been modified to fix typos.
    restriction     = models.TextField(blank=True, null=True)
    #If the coupon requires the user to enter a code, it is in this field. Any deal with a code will also contain "coupon" in the DealTypes field.
    code            = models.CharField(max_length=255, blank=True, null=True)
    start           = models.DateTimeField(blank=True, null=True)
    end             = models.DateTimeField(blank=True, null=True)
    link            = models.CharField(max_length=255, blank=True, null=True)
    directlink      = models.CharField(max_length=255, blank=True, null=True)
    skimlinks       = models.CharField(max_length=255, blank=True, null=True)
    status          = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    lastupdated     = models.DateTimeField(blank=True, null=True)
    created         = models.DateTimeField(blank=True, null=True)
    countries       = models.ManyToManyField(Country, blank=True, null=True)
    price           = models.FloatField(default=0)
    listprice       = models.FloatField(default=0)
    discount        = models.FloatField(default=0)
    percent         = models.IntegerField(default=0)





