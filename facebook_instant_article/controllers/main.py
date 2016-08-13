# -*- coding: utf-8 -*-

import werkzeug
from openerp.addons.web import http
from openerp import SUPERUSER_ID
import requests
from openerp.addons.web.http import request
from openerp.addons.website.models.website import slug, unslug

import pprint
import lxml.html as LH
from lxml import etree
import json
import logging

_logger = logging.getLogger(__name__)

FB_OAUTH_URL = 'https://graph.facebook.com/v2.3/oauth/access_token'


class FbInstantArticle(http.Controller):

    @http.route(
        ['/fb_instant_article/login_success'],
        type='http', auth='public', csrf=False, website=True)
    def login_success(self, **kw):

        state = kw.get('state', False)
        error = kw.get('error', False)
        error_description = kw.get('error_description', '')
        code = kw.get('code', False)
        if not request.validate_csrf(state):
            _logger.warning('Bad CSRF token')
            return 'Bad CSRF token'
        if error:
            return error_description

        res = request.env['website'].search(
            [('id', '=', request.website.id)],
            limit=1)
        if len(res) > 0:
            par = {
                'client_id': res.fb_app_id,
                'redirect_uri': request.httprequest.url_root +
                'fb_instant_article/login_success',
                'client_secret': res.fb_app_secret,
                'code': code,
            }
            r = requests.Session().get(FB_OAUTH_URL, params=par)
            if not r.status_code == 200:
                response = r.json()
                return request.redirect(request.httprequest.url_root)

            response = r.json()
            access_token = response.get('access_token', False)
            par = {
                'client_id': res.fb_app_id,
                'grant_type': 'fb_exchange_token',
                'client_secret': res.fb_app_secret,
                'fb_exchange_token': access_token,
            }
            r = requests.Session().get(FB_OAUTH_URL, params=par)
            if not r.status_code == 200:
                response = r.json()
                return request.redirect(request.httprequest.url_root)

            response = r.json()
            long_token = response.get('access_token', False)

            user_id = request.env['res.users'].search(
                [('id', '=', request.uid)],
                limit=1)
            if len(user_id) > 0:
                user_id.fb_long_term_token = long_token

            return request.redirect(request.httprequest.url_root)

        return 'error'

    #     curl \
    # -F 'access_token={access-token}' \
    # -F 'html_source=<!doctype html>...' \
    # -F 'published=true' \
    # -F 'development_mode=false' \
    # https://graph.facebook.com/{page-id}/instant_articles
    def _post_article_to_fb(self, html_source):
        '''Upload article to facebook.
        returns import id'''

        user_id = request.env['res.users'].search(
            [('id', '=', request.uid)],
            limit=1)
        if len(user_id) <= 0:
            return False

        res = request.env['website'].search(
            [('id', '=', request.website.id)],
            limit=1)
        if len(res) <= 0:
            return False

        par = {
            'access_token': user_id.fb_long_term_token,
            'html_source': html_source,
            'published': False,
            'development_mode': True,
        }
        fb_instant_url = 'https://graph.facebook.com/' +\
            res.fb_pages_id + '/instant_articles'
        r = requests.Session().post(fb_instant_url, params=par)
        if not r.status_code == 200:
            _logger.warning(r.json())
            return False

        response = r.json()
        _logger.info('resp : %s' % response)
        return response.get('id', '')

    @http.route(
        ['/fb_instant_article/disconnect'],
        type='http', auth='user')
    def disconnect(self, **kw):
        redirect_uri = kw.get('redirect_uri', False)
        user_id = request.env['res.users'].search(
            [('id', '=', request.uid)],
            limit=1)
        if len(user_id) > 0:
            user_id.fb_long_term_token = ''
        return http.redirect_with_hash(redirect_uri)

    @http.route([
        '''/fb_instant_article/<model("blog.blog"):blog>''' +
        '''/post/<model("blog.post",''' +
        ''' "[('blog_id','=',blog[0])]"):blog_post>''',
    ], type='http', auth="user", website=True)
    def fb_post(self,
                blog,
                blog_post):
        """ Convert blog post to Facebook Instant Article.
        """
        cr, uid, context = request.cr, request.uid, request.context
        blog_post_obj = request.registry['blog.post']

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/")

        # Find next Post
        all_post_ids = blog_post_obj.search(
            cr, SUPERUSER_ID, [('blog_id', '=', blog.id)], context=context)
        # should always return at least the current post
        current_blog_post_index = all_post_ids.index(blog_post.id)
        next_post_id = \
            all_post_ids[0 if current_blog_post_index ==
                         len(all_post_ids) - 1
                         else current_blog_post_index + 1]
        next_post = next_post_id and blog_post_obj.browse(
            cr, SUPERUSER_ID, next_post_id, context=context) or False

        post_cover_prop = json.loads(blog_post.cover_properties)
        next_post_cover_prop = \
            json.loads(next_post.cover_properties) if next_post else {}
        values = {
            'blog': blog,
            'blog_post': blog_post,
            'blog_post_cover_properties': post_cover_prop,
            'main_object': blog_post,
            'next_post': next_post,
            'next_post_cover_properties': next_post_cover_prop,
        }
        post_id = blog_post_obj.browse(
            cr, SUPERUSER_ID, blog_post.id, context=context)

        layout = '<div>' + post_id.content + '</div>'
        try:
            root = LH.fromstring(layout)
        except LH.ParseError as err:
            _logger.warning('Can not parse article: %s' % format(err))
            return False
        for element in root.iter('h3'):
            element.tag = 'h2'
        for element in root.iter('h4'):
            element.tag = 'h2'
        for element in root.iter('img'):
            src = element.attrib.get('src', '')
            element.tag = 'figure'
            for key in element.attrib.keys():
                element.attrib.pop(key)
            etree.SubElement(element, 'img').set('src', src)

        post_id.fb_content = LH.tostring(root,
                                         encoding='utf-8',
                                         method='xml')

        response = request.website.render(
            "facebook_instant_article.blog_post_instant_article", values)
        response.flatten()
        html_source = '<!doctype html>' + response.data
        import_id = self._post_article_to_fb(html_source)
        if import_id:
            post_id.fb_import_id = import_id
        url = '/blog/' + str(blog.id) + '/post/' + str(blog_post.id)
        return http.redirect_with_hash(url)

    @http.route(
        ['/fb_instant_article/check_import'],
        type='json', auth='user', website=True)
    def check_import(self, fb_import_id):
        user_id = request.env['res.users'].search(
            [('id', '=', request.uid)],
            limit=1)
        if len(user_id) <= 0:
            return False

        res = request.env['website'].search(
            [('id', '=', request.website.id)],
            limit=1)
        if len(res) <= 0:
            return False

        par = {
            'access_token': user_id.fb_long_term_token,
            'fields': 'errors,instant_article,status',
        }
        # 1476960168997006 - fb_import_id lina kostenko
        fb_instant_url = 'https://graph.facebook.com/' + fb_import_id
        r = requests.Session().get(fb_instant_url, params=par)
        if not r.status_code == 200:
            _logger.warning(r.json())
            return False

        response = r.json()
        _logger.info('resp : %s' % response)
        if response.get('status', '') == 'SUCCESS':
            _logger.info('import succefully')
            blog_post_obj = request.registry['blog.post']
            blog_post_id = blog_post_obj.search(
                cr, SUPERUSER_ID,
                [('fb_import_id', '=', fb_import_id)],
                limit=1, context=context)
            if not blog_post_id:
                return False
            blog_post = blog_post_obj.browse(
                cr, SUPERUSER_ID, blog_post_id, context=context)
            blog_post.fb_import_status_ok = True
            blog_post.fb_article_id = response.get('id', '')
            return True
        return False
