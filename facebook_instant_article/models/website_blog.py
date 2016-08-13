# -*- coding: utf-8 -*-

# from openerp import api, fields, models, _

from openerp.osv import osv, fields
from openerp.addons.website.models.website import slug
from openerp import SUPERUSER_ID
import requests


class FbBlogPost(osv.Model):
    _inherit = 'blog.post'

    # def _check_for_publication(self, cr, uid, ids, vals, context=None):
    #     super(FbBlogPost, self)._check_for_publication(
    #         cr, uid, ids, vals, context)
    #     if vals.get('website_published'):
    #         print 'published.'
    #         user = self.pool['res.users'].browse(cr, uid, uid, context=context)
    #         if user and user.fb_long_term_token:
    #             print 'fb connected'

    _columns = {
        'fb_content': fields.html('FB Content', sanitize=False),
        'fb_import_id': fields.char('FB Import ID'),
        'fb_import_status_ok': fields.boolean('FB Import Status',
                                              default=False),
        'fb_article_id': fields.char('FB Article ID'),
    }
