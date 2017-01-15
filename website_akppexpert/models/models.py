# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductPublicCatgoryAKPP(models.Model):
    _inherit = 'product.public.category'

    html_content = fields.Html(
        'HTML Content',
        default='<div class="oe_structure" />',
        translate=True)


class ProductAttributeValutAKPP(models.Model):
    _inherit = 'product.attribute.value'

    website_active = fields.Boolean('Active', default=True)
