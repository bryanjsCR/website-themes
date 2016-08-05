# -*- coding: utf-8 -*-

import werkzeug
from openerp.addons.web import http
import requests
from openerp.addons.web.http import request

import pprint
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
                pprint.pprint(response)
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
                pprint.pprint(response)
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
