# -*- coding: utf-8 -*-


from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSaleAkpp(website_sale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSaleAkpp, self)._get_search_domain(
            search,
            category,
            attrib_values)
        if search:
            for src in search.split(" "):
                pre = domain[:1]
                post = domain[1:]
                domain = pre + [
                    '|',
                    ('attribute_line_ids.value_ids.name', 'ilike', src)] + post
        return domain
