import string
import unittest

from django.core.urlresolvers import reverse
from django_webtest import WebTest

from selenium import webdriver

from web.models import FeaturedCoupon
from core.models import Coupon, Merchant, Category

# Functional tests with WebTest
class TestViewsWebtest(WebTest):

    def test_index_page(self):
        dummy_merchant = Merchant.objects.create(name="Dummy Merchant", name_slug='dummy-merchant')
        dummy_coupon = Coupon.objects.create(merchant=dummy_merchant)
        FeaturedCoupon.objects.create(coupon=dummy_coupon)
        page = self.app.get(reverse('web.views.main.index'))
        assert page.status_int == 200

    # def test_coupon_page(self):
    #     dummy_merchant = Merchant.objects.create(name="Dummy Merchant", name_slug='dummy-merchant')
    #     dummy_coupon = Coupon.objects.create(merchant=dummy_merchant)
    #     page = self.app.get('/coupons/{}/{}/'.format(dummy_merchant.name_slug, dummy_merchant.id))
    #     assert page.status_int == 200

    def test_all_categories_page(self):
        page = self.app.get(reverse('web.views.main.categories'))
        assert page.status_int == 200

    def test_one_category_page(self):
        dummy_category = Category.objects.create(name='Dummy Category', code='dummy-category')
        url = '/categories/{}/'.format(dummy_category.code)
        page = self.app.get(url)
        assert page.status_int == 200

    def test_store_page(self):
        page = self.app.get('/stores/')
        assert page.status_int == 200

    def test_store_page_by_alphabet(self):
        alphabet_list = list(string.ascii_lowercase)
        for a in alphabet_list:
            url = '/stores/{}/'.format(a)
            page = self.app.get(url)
            assert page.status_int == 200

    def test_terms_conditions_page(self):
        page = self.app.get(reverse('web.views.main.privacy'))
        assert page.status_int == 200

    def test_sitemap(self):
        page = self.app.get(reverse('web.views.main.sitemap'))
        assert page.status_int == 302
        assert page.url == 'http://s3.amazonaws.com/pushpenny/sitemap.xml'

    def test_robots_txt(self):
        page = self.app.get(reverse('web.views.main.robots_txt'))
        assert page.status_int == 200
        assert "Sitemap: http://s3.amazonaws.com/pushpenny/sitemap.xml" in page.content

    def test_search_page(self):
        sample_string = 'test'
        page = self.app.get('/search/?q={}'.format(sample_string))
        assert page.status_int == 200

# Functional tests with Selenium

class TestViewsSelenium(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.browser.get('http://localhost:8000')

    def tearDown(self):
        self.browser.quit()

    def test_index_page(self):
        # User goes to pushpenny site (done in setUp)

        # User sees the featured deal in the slider
        featured_deal_link = self.browser.find_elements_by_link_text('Use Coupon')
        self.assertEqual(len(featured_deal_link), 1)

        # User also sees at least one 'New' or 'Popular' coupons
        deal_links_list = self.browser.find_elements_by_xpath('/html/body/div/div/div[2]/div[2]/div/div/ul/li')
        self.assertGreater(len(deal_links_list), 0)

        # User also sees at least one 'Popular' companies
        popular_companies_list = self.browser.find_elements_by_xpath('/html/body/div/footer/div[1]/div[2]/div/div/ul/li')
        self.assertGreater(len(popular_companies_list), 0)

