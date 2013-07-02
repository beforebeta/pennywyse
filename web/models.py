from django.db import models

class Category(models.Model):
    code            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    name            = models.CharField(max_length=255,blank=True, null=True, db_index=True)
    description     = models.CharField(max_length=255,blank=True, null=True)

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
    #Our proprietary coupon ID - especially useful in identifying deals that are delivered more than once because they have changed.
    ref_id          = models.CharField(max_length=255, db_index=True)
    merchant        = models.ForeignKey(Merchant)
    categories      = models.ManyToManyField(Category)
    dealtypes       = models.ManyToManyField(DealType)
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
    countries       = models.ManyToManyField(Country)
    price           = models.FloatField(default=0)
    listprice       = models.FloatField(default=0)
    discount        = models.FloatField(default=0)
    percent         = models.IntegerField(default=0)





