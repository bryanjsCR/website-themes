# -*- coding: utf-8 -*-

import werkzeug
from openerp.addons.web import http
from openerp import SUPERUSER_ID
import requests
from openerp.addons.web.http import request
from openerp.addons.website.models.website import slug, unslug

from copy import deepcopy
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

    def _post_article_to_fb(self, html_source):
        '''Upload article to facebook.
        returns import id'''

        user_id = request.env['res.users'].search(
            [('id', '=', request.uid)],
            limit=1)
        if len(user_id) <= 0:
            return False, False

        res = request.env['website'].search(
            [('id', '=', request.website.id)],
            limit=1)
        if len(res) <= 0:
            return False, False

        par = {
            'access_token': user_id.fb_long_term_token,
            'html_source': html_source,
            'published': False,
            'development_mode': False,
        }
        fb_instant_url = 'https://graph.facebook.com/' +\
            res.fb_pages_id + '/instant_articles'
        r = requests.Session().post(fb_instant_url, params=par)
        if not r.status_code == 200:
            _logger.warning('unable to post article')
            return False, False

        response = r.json()
        return response.get('id', ''), user_id.fb_long_term_token

    def _convert_to_article(self, layout):
        '''Convert html to instant article format.'''
        try:
            root = LH.fromstring(layout)
        except LH.ParseError as err:
            _logger.warning('Can not parse article: %s' % format(err))
            return False
        # change all h3s to h2
        for element in root.iter('h3'):
            element.tag = 'h2'
        # change all h4s to h2
        for element in root.iter('h4'):
            element.tag = 'h2'
        # wrap each <img> with <figure>
        for element in root.iter('img'):
            src = element.attrib.get('src', '')
            element.tag = 'figure'
            for key in element.attrib.keys():
                element.attrib.pop(key)
            etree.SubElement(element, 'img').set('src', src)
        # wrap each <iframe> with <figure>
        for element in root.iter('iframe'):
            src = element.attrib.get('src', '')
            if src[0:2] == '//':    # fix url
                src = 'http:' + src
            element.tag = 'figure'

            for key in element.attrib.keys():
                element.attrib.pop(key)
            element.set('class', 'op-interactive')
            iframe = etree.SubElement(element, 'iframe')
            iframe.set('width', '560')
            iframe.set('height', '315')
            iframe.set('src', src)
        # convert image floating in s_text_image_floating
        # to image with caption
        for section in root.iter('section'):
            if section.attrib.get('class', '') != 's_text_image_floating':
                continue
            for el in section.iter('div'):
                if el.attrib.get('class', '') == 'o_footer':
                    caption = deepcopy(el)
                    el.getparent().remove(el)
                    for figure in section.iter('figure'):
                        figcaption = etree.SubElement(figure, 'figcaption')
                        figcaption.append(caption)
        # convert gallery to slideshow
        for section in root.iter('section'):
            if 'o_gallery' not in section.attrib.get('class', ''):
                continue
            root_figure = etree.SubElement(section, 'figure')
            root_figure.set('class', 'op-slideshow')
            for div in section.iter('div'):
                if div.attrib.get('class') != 'container':
                    continue
                for fig in div.iter('figure'):
                    root_figure.append(deepcopy(fig))
            for el in section:
                if el is not root_figure:
                    el.getparent().remove(el)
        # convert fb embed to figure+iframe
        for element in root.iter('div'):
            if element.attrib.get('class', '') == 'fb-post':
                data_href = element.attrib.get('data-href', '')
                root_figure = etree.SubElement(element, 'figure')
                root_figure.set('class', 'op-interactive')
                iframe_el = etree.SubElement(root_figure, 'iframe')
                iframe_el.set('src', data_href)
                iframe_el.set('width', 'auto')

        return LH.tostring(root, encoding='utf-8', method='xml')

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
        """ Publish blog post to Facebook Instant Article.
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
        post_id.fb_content = self._convert_to_article(layout)

        response = request.website.render(
            "facebook_instant_article.blog_post_instant_article", values)
        response.flatten()
        html_source = '<!doctype html>' + response.data
        # print html_source
        import_id, acc_token = self._post_article_to_fb(html_source)
        if import_id:
            post_id.fb_import_id = import_id
        if acc_token:
            post_id.fb_publisher_token = acc_token
        url = '/blog/' + str(blog.id) + '/post/' + str(blog_post.id)
        return http.redirect_with_hash(url)

    @http.route(
        ['/fb_instant_article/check_import'],
        type='json', auth='user', website=True)
    def check_import(self, fb_import_id):
        cr, uid, context = request.cr, request.uid, request.context
        user_id = request.env['res.users'].search(
            [('id', '=', request.uid)],
            limit=1)
        if len(user_id) <= 0:
            return False

        blog_post_obj = request.registry['blog.post']
        blog_post_id = blog_post_obj.search(
            cr, SUPERUSER_ID,
            [('fb_import_id', '=', fb_import_id)],
            limit=1, context=context)
        if not blog_post_id:
            return False
        blog_post = blog_post_obj.browse(
            cr, SUPERUSER_ID, blog_post_id, context=context)

        res = request.env['website'].search(
            [('id', '=', request.website.id)],
            limit=1)
        if len(res) <= 0:
            return False
        access_token = blog_post.fb_publisher_token or\
            user_id.fb_long_term_token
        par = {
            'access_token': access_token,
            'fields': 'errors,instant_article,status',
        }
        fb_instant_url = 'https://graph.facebook.com/' + fb_import_id
        r = requests.Session().get(fb_instant_url, params=par)
        if not r.status_code == 200:
            return False

        response = r.json()
        if response.get('status', '') == 'SUCCESS':
            _logger.info('import succefully')

            blog_post.fb_import_status_ok = True
            blog_post.fb_article_id = response.get('id', '')
            return True
        return False
