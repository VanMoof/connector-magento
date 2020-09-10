# © 2019 Opener BV (<https://vanmoof.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class MagentoWarehouse(models.Model):
    _name = 'magento.warehouse'
    _description = 'Magento Warehouse Mapping'

    active = fields.Boolean('Active', default=True)
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        required=True)
    backend_id = fields.Many2one(
        comodel_name='magento.backend',
        string='Magento Backend',
        required=True
    )
    magento_id = fields.Char(
        string='Magento Warehouse Code',
        required=True)
