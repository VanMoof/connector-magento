from odoo.addons.component.core import Component


class SourcesImportMapper(Component):
    _name = 'magento.website.mapper'
    _inherit = 'magento.import.mapper'
    _apply_on = 'magento.sources'

    direct = [('name', 'name'),
              ('source_code', 'source_code')]


class SourcesImporter(Component):
    """ Import Sources """

    _name = 'magento.website.record.importer'
    _inherit = 'magento.importer'
    _apply_on = 'magento.sources'
