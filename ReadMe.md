# PennyWyse

Set featured coupons

	from web.models import *
	for c in Coupon.objects.all()[:10]:
		FeaturedCoupon(coupon=c).save()

Delete images from DB

	from websvcs.models import *
	ImageStore.objects.all().delete()
