# -*- coding: utf-8 -*-
{
    'name': "Mail Attachment Preview",
    'summary': """Show thumbnails for images in chatter""",
    'description': """
        Show thumbnails for images in chatter and open attachments in new tab.
    """,
    'author': "ERP Ukraine",
    'website': "https://erp.co.ua",
    'license': 'AGPL-3',
    'price': 20.00,
    'currency': 'EUR',
    'category': 'Discuss',
    'version': '1.0',
    'depends': ['mail'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/thread.xml',
    ],
}
