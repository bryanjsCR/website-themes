# -*- coding: utf-8 -*-

# from openerp import api, fields, models, _

from openerp.osv import osv, fields
from openerp.addons.website.models.website import slug
from openerp import SUPERUSER_ID
import requests


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
                base_url = self.pool['ir.config_parameter'].get_param(
                    cr, SUPERUSER_ID, 'web.base.url')
                for post in self.browse(cr, uid, ids, context=context):
                    post_url = '%(base_url)s/blog/%(blog_slug)s/post/%(post_slug)s' % {
                        'base_url': base_url,
                        'blog_slug': slug(post.blog_id),
                        'post_slug': slug(post),
                    }
                    fb_article_url = '%(base_url)s/fb_instant_article/%(blog_slug)s/post/%(post_slug)s' % {
                        'base_url': base_url,
                        'blog_slug': slug(post.blog_id),
                        'post_slug': slug(post),
                    }
                    print fb_article_url
                    r = requests.Session().get(fb_article_url)
                    if not r.status_code == 200:
                        return
                    response = r.json()
                    print r.raw

    _columns = {
        'fb_content': fields.html('FB Content', sanitize=False),
        'fb_import_id': fields.char('FB Content'),
    }
