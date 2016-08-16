# -*- coding: utf-8 -*-

# from openerp import api, fields, models, _

from openerp.osv import osv, fields
from openerp.addons.website.models.website import slug
from openerp import SUPERUSER_ID
import requests


class FbBlogPost(osv.Model):
    _inherit = 'blog.post'

    _columns = {
        'fb_content': fields.html('FB Content', sanitize=False),
        'fb_import_id': fields.char('FB Import ID'),
        'fb_import_status_ok': fields.boolean('FB Import Status',
                                              default=False),
        'fb_article_id': fields.char('FB Article ID'),
        'fb_publisher_token': fields.char('FB Publisher Token'),
    }
