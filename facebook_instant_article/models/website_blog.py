# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class weche_Blog(models.Model):
    _inherit = 'blog.blog'

    fb_app_id = fields.Char(string='Facebook App ID')
    fb_user_token = fields.Char(string='User Access Token')
    fb_app_token = fields.Char(string='App Access Token')
