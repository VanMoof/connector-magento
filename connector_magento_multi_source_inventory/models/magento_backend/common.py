import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class MagentoBackend(models.Model):
    _inherit = 'magento.backend'

    @api.multi
    def synchronize_metadata(self):
        # super(MagentoBackend, self).synchronize_metadata()
        for backend in self:
            # self.env['magento.store'].import_batch(backend)
            self.env['magento.source'].import_batch(backend)
        return True
