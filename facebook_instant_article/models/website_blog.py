# -*- coding: utf-8 -*-

# from openerp import api, fields, models, _

from openerp.osv import osv, fields


class FbBlogPost(osv.Model):
    _inherit = 'blog.post'

    def _check_for_publication(self, cr, uid, ids, vals, context=None):
        super(FbBlogPost, self)._check_for_publication(
            cr, uid, ids, vals, context)
        if vals.get('website_published'):
            print 'published.'
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            if user and user.fb_long_term_token:
                print 'fb connected'
