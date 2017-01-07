# -*- coding: utf-8 -*-
from openerp import http

# class WebsiteAkppexpert(http.Controller):
#     @http.route('/website_akppexpert/website_akppexpert/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_akppexpert/website_akppexpert/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_akppexpert.listing', {
#             'root': '/website_akppexpert/website_akppexpert',
#             'objects': http.request.env['website_akppexpert.website_akppexpert'].search([]),
#         })

#     @http.route('/website_akppexpert/website_akppexpert/objects/<model("website_akppexpert.website_akppexpert"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_akppexpert.object', {
#             'object': obj
#         })