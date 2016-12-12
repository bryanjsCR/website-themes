# -*- encoding: utf-8 -*-

{
    'name': 'Show extra fields on product',
    'version': '1.0',
    'license': 'OPL-1',
    'category': 'Sale',
    'author': 'ERP Ukraine',
    'website': 'http://erp.co.ua',
    'description': """
This module adds 'Product marking' and 'Sales text' fields to
product form and canban view.
""",
    'depends': [
        'product',
    ],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
