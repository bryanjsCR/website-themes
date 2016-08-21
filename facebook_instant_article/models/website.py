# -*- coding: utf-8 -*-

from openerp import fields, models, api


class FbConfigWebsite(models.Model):
    _inherit = 'website'

    fb_pages_id = fields.Char(
        string='Facebook page ID',
        default='')
    fb_app_id = fields.Char(
        string='Facebook App ID',
        default='')
    fb_app_secret = fields.Char(
        string='Facebook App Secret',
        default='')
    fb_show_ads = fields.Boolean(
        string='Show Embed Ads',
        default=True)
    fb_development_mode = fields.Boolean(
        string='Development Mode',
        desription='Post articles in development mode before review',
        default=True)
    fb_published_articles = fields.Boolean(
      string='Post Articles Published',
      description='Check if You want your articles be automatically published',
      default=False)


class FbConfigWebsiteSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    fb_pages_id = fields.Char(
        related='website_id.fb_pages_id',
        string='Facebook pages meta')
    fb_app_id = fields.Char(
        related='website_id.fb_app_id',
        string='Facebook App ID')
    fb_app_secret = fields.Char(
        related='website_id.fb_app_secret',
        string='Facebook App Secret')
    fb_show_ads = fields.Boolean(
        related='website_id.fb_show_ads',
        string='Show Embed Ads')
    fb_development_mode = fields.Boolean(
        related='website_id.fb_development_mode',
        string='Development Mode')
    fb_published_articles = fields.Boolean(
        related='website_id.fb_published_articles',
        string='Post Articles Published')


class FbConfigResUsers(models.Model):
    _inherit = 'res.users'

    fb_long_term_token = fields.Char(
        string='App Long Term Token',
        default='')
