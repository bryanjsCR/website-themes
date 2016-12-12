# -*- encoding: utf-8 -*-

from odoo import models, fields, api, tools, _


class ProductTemplatePEF(models.Model):
    _inherit = 'product.template'

    product_marking = fields.Char(string='Product Marking')
    sales_text = fields.Char(string='Sales Text')
