import logging

from odoo import api, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MagentoBackend(models.Model):
    _inherit = 'magento.backend'

    @api.multi
    def synchronize_metadata(self):
        super(MagentoBackend, self).synchronize_metadata()
        try:
            for backend in self:
                self.env['magento.sources'].import_batch(backend)
            return True
        except Exception as e:
            _logger.error(ustr(e))
            raise UserError(
                _("Check your configuration, we can't get the data. "
                  "Here is the error:\n%s") %
                ustr(e))
