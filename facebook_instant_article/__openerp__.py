# -*- coding: utf-8 -*-
{
    'name': 'Facebook Instant Article',
    'description': 'Publish Blog Posts to Facebook as Instant Articles.',
    'category': 'Website',
    'version': '1.2',
    'price': 20.00,
    'currency': 'EUR',
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'data': [
        'views/assets.xml',
        'views/templates.xml',
        'views/website_views.xml'
    ],
    'application': True,
    'depends': ['website', 'website_blog'],
    'images': [
        'static/description/icon.png',
    ],
}
