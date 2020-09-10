from odoo import models, fields, api
from odoo.addons.component.core import Component


class MagentoSources(models.Model):
    _name = 'magento.sources'
    _inherit = ['magento.binding', 'magento.config.specializer']
    _description = 'Magento Sources'


    name = fields.Char(required=True, readonly=True)
    source_code = fields.Char(readonly=True)
    sort_order = fields.Integer(string='Sort Order', readonly=True)
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        help='Warehouse used to compute the '
             'stock quantities.',
    )


class SourcesAdapter(Component):
    _name = 'magento.sources.adapter'
    _inherit = 'magento.adapter'
    _apply_on = 'magento.sources'

    # I cannot find the model in Magento code to set the _magento_model and _magento2_model
    # I dont know how to set the _admin_path
    _magento_model = 'ol_websites'
    _magento2_model = 'store/sources'
    _admin_path = 'system_store/editWebsite/website_id/{id}'
