# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductPublicCatgoryAKPP(models.Model):
    _inherit = 'product.public.category'

    html_content = fields.Html(
        'HTML Content',
        default='<div class="oe_structure" />')
