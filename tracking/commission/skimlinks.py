import hashlib
import datetime
from time import strftime
import urllib
from django.conf import settings
import requests
from tracking.utils import u_clean
import json

REPORTING_ENDPOINT = 'https://api-reports.skimlinks.com'

class ReportingAPI():

    def test(self):
        return _get_response('/publisher/test', {}).content

    def get_commissions(self):
        return json.loads(_get_response('/publisher/reportcommissions', {
            'startDate'     : '2011-12-01',
            'endDate'       : datetime.date.today().isoformat()
        }).content)

def _md5(message):
    return hashlib.md5(message).hexdigest()

def _get_timestamp():
    return strftime("%Y-%m-%dT%H:%M:%S+00:00")

def _get_quoted(components):
    return urllib.quote(components.encode("utf-8"))

def _create_auth_token():
    timestamp = _get_timestamp()
    return timestamp, _md5(timestamp + settings.SKIMLINKS_REPORTING_PRIVATE_KEY)

def _get_response(path, arguments):
    timestamp, token = _create_auth_token()
    arguments['timestamp']  = timestamp
    arguments['apikey']     = settings.SKIMLINKS_REPORTING_PUBLIC_KEY,
    arguments['authtoken']  = token,
    arguments['format']     = 'json'
    return requests.get(REPORTING_ENDPOINT + path, params=arguments)

_merchant_descriptions = {
   "macys"             :["macys"          , 3, "Macy's is the online destination for today's customer. Offering quality, style, value and great selections."],
   "sephora"           :["sephora"        , 13, "Choose from over 200 top beauty brands including Bare Escentuals, Dior, Philosophy, Smashbox and more!"],
   "nordstrom"         :["nordstrom"      , 6, "Choose from over 200 top beauty brands including Bare Escentuals, Dior, Philosophy, Smashbox and more!"],
   "thinkgeekcom"      :["thinkgeekcom"   , 15, "From apparel to gadgets and computer accessories to caffeine, ThinkGeek is a one-stop shop for everything geeky."],
   "luisaviaroma"      :["luisaviaroma"   , 16, "LUISAVIAROMA has a a wide selection from over 400 Designer collections, such as Dior Homme, Dsquared2, Dolce&Gabbana, Christian Louboutin, Lanvin, Moncler, Marc Jacobs, Chloe and more."],
   "neiman-marcus"     :["neiman-marcus"  , 10, "Shop fashion's top designers and beauty's best brands, plus designer jewelry, luxurious decor, and distinctive gifts for any occasion."],
   "jcpenney"          :["jcpenney"       , 7, "FREE Shipping at jcpenney.com. Shop for women's clothing, men's clothing, boy's and girl's clothing, home furniture, bedding, jewelry and shoes."],
   "sears"             :["sears"          , 8, "Begin your Shopping Experience at Sears. Buy Online, Pick up in Store. Find Store Locations. Find Great Brands such as Kenmore, Craftsman & Diehard."],
   "target"            :["target"         , 5, "Expect more pay less with Target. Spend $50, get free shipping on over 500K items. Chose from a wide selection of furniture, baby, electronics, toys, shoes."],
   "kmart"             :["kmart"          , 9, "Quality products through a portfolio of exclusive brands that include Jaclyn Smith, Joe Boxer, County Living, Sofia Vergara, Gordon Ramsay and Smart Sense. Kmart offers a wide range of categories from appliances, to electronics, toys, apparel, sporting goods and more."],
   "kohls"             :["kohls"          , 12, "Kohl's stores are stocked with everything you need for yourself and your home - apparel, shoes & accessories for women, children and men, plus home products like small electrics, bedding, luggage and more."],
   "ssense"            :["ssense"         , 11, "SSENSE.com is the online fashion destination for discerning men and women shopping for luxury apparel. With a repertoire of over 200 designer collections, SSENSE boasts a selection of carefully curated runway and high-street fashions from designers such as Dsquared2, Diesel, Rag & Bone, Marc Jacobs, Alice + Olivia, Givenchy, Lanvin, Alexander Wang, Proenza Schouler and many more."],
   "bluefly"           :["bluefly"        , 2, "The online destination for the fashion savvy insider looking for the most current trends & hot designer brands. Fabulous new styles are added every day including Prada, Fendi, Gucci, Dolce & Gabbana, BCBG Max Azria, Theory, Nicole Miller, Michael Kors & many more."],
   "levis"             :["levis"          , 1, "Shop Jeans, Tops, Jackets, Shorts, and Accessories for men, women, juniors, kids, and babies at Levi's!"],
   "life-is-good"      :["life-is-good"   , 4, "Optimistic apparel and accessories featuring positive messaging and comfortable fits for men, women and kids."],
   "charlotte-russe"   :["charlotte-russe", 14, "Fashion that's trendy, not spendy! Shop the glam at Charlotte Russe, and snag major savings on the hottest clothes, shoes, denim, accessories and more. XOXO!"]
}

def get_merchant_description(merchant_name_slug):
    try:
        return _merchant_descriptions[merchant_name_slug][2]
    except:
        return merchant_name_slug

def merchant_slugs(self):
    sorted_tuples = sorted(_merchant_descriptions.values(), key=lambda tuple: tuple[1])
    return [tuple[0] for tuple in sorted_tuples]
