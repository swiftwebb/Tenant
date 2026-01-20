from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticSitemap(Sitemap):
    def items(self):
        return [
            'customers:home',
            'customers:about',
            'customers:plan_list',
            'customers:terms',
            'customers:privacy',
        ]

    def location(self, item):
        return reverse(item)
