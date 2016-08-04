# -*- coding: utf-8 -*-

from openerp import fields, models, api


class fb_config_website(models.Model):
    _inherit = 'website'

    fb_pages_id = fields.Char(
        string='Facebook pages meta',
        default='1')
    fb_app_id = fields.Char(string='Facebook App ID')
    fb_user_token = fields.Char(string='User Access Token')
    fb_app_token = fields.Char(string='App Access Token')


class fb_config_website_settings(models.TransientModel):
    _inherit = 'website.config.settings'

    fb_pages_id = fields.Char(
        related='website_id.fb_pages_id',
        string='Facebook pages meta')
    fb_app_id = fields.Char(
        related='website_id.fb_app_id',
        string='Facebook App ID')
    fb_user_token = fields.Char(
        related='website_id.fb_user_token',
        string='User Access Token')
    fb_app_token = fields.Char(
        related='website_id.fb_app_token',
        string='App Access Token')
