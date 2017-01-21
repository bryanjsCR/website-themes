# -*- coding: utf-8 -*-

from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request


class WebsiteSaleAkpp(website_sale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()
        if search:
            dom = []
            criterias = [
                'name',
                'description',
                'description_sale',
                'product_variant_ids.default_code',
                'attribute_line_ids.value_ids.name'
            ]
            for srch in search.split(" "):
                for opt in criterias:
                    if len(dom) == 0:
                        dom = [(opt, 'ilike', srch)]
                    else:
                        dom = ['|'] + dom + [(opt, 'ilike', srch)]
            domain = domain + dom

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain
