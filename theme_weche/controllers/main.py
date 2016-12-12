# -*- coding: utf-8 -*-

import datetime
import json
import werkzeug

from openerp import fields
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_blog.controllers.main import WebsiteBlog
from openerp.tools import html2plaintext

from pytz import timezone

import locale
import threading
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()


@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


class WebsiteBlog(WebsiteBlog):

    @http.route(['/blog/<model("blog.blog"):blog>/rss'],
                type='http', auth="public")
    def blog_rss(self, blog, limit='15'):
        v = {}
        v['blog'] = blog
        v['base_url'] = request.env[
            'ir.config_parameter'].get_param('web.base.url')
        v['posts'] = request.env['blog.post'].search(
            [('blog_id', '=', blog.id)], limit=min(int(limit), 50))
        v['rfc_dates'] = {}
        v['posts_plaintext'] = {}
        v['blog_post_cover_properties'] = {}
        for p in v['posts']:
            # add date in rfc-822 format
            pdate = fields.Datetime.from_string(p.write_date)
            tz = 'Europe/Kiev'
            if p.sudo().author_id.tz:
                tz = p.sudo().author_id.tz
            localtz = timezone(tz)
            pdate = localtz.localize(pdate)
            with setlocale('C'):
                p_rfc_date = pdate.strftime('%a, %d %b %Y %H:%M:%S %z')
            v['rfc_dates'][p.id] = p_rfc_date
            # add post body as plain text
            v['posts_plaintext'][p.id] = html2plaintext(p.content)
            # add cover Image
            cov_prop = {}
            cov_prop = json.loads(p.cover_properties)
            v['blog_post_cover_properties'][p.id] = cov_prop.get(
                'background-image', False)[4:-1]
        r = request.render(
            "theme_weche.blog_rss",
            v, headers=[('Content-Type', 'application/rss+xml')])
        return r
