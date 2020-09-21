from odoo import models, fields, api
from odoo.addons.queue_job.job import job
from odoo.addons.component.core import Component


class MagentoSource(models.Model):
    _name = 'magento.source'
    _inherit = ['magento.binding', 'magento.config.specializer']
    _description = 'Magento Source'

    name = fields.Char(readonly=True)
    source_code = fields.Char(readonly=True)
    warehouse = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        help='Warehouse used to compute the '
             'stock quantities.',
    )
    active = fields.Boolean('Active', default=True)

    @job(default_channel='root.magento')
    @api.multi
    def export_stock_levels(self):
        """ Push stock levels for products per source """
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage='stock.exporter')
            return exporter.run(self)


class SourceAdapter(Component):
    _name = 'magento.source.adapter'
    _inherit = 'magento.adapter'
    _apply_on = 'magento.source'

    _magento2_model = 'inventory/sources'
    _magento2_key = 'source_code'
    _magento2_search = 'inventory/sources'
