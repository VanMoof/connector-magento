from odoo.addons.component.core import Component


class SourceImportMapper(Component):
    _name = 'magento.source.mapper'
    _inherit = 'magento.import.mapper'
    _apply_on = 'magento.source'

    direct = [('name', 'name'),
              ('source_code', 'source_code')]


class SourceImporter(Component):
    """ Import Source """

    _name = 'magento.source.importer'
    _inherit = 'magento.importer'
    _apply_on = ['magento.source']

    def _create(self, data):
        if not data.get('backed_id'):
            data['backend_id'] = self._backend_adapter.backend_record.id
        binding = super(SourceImporter, self)._create(data)
        self.backend_record.add_checkpoint(binding)
        return binding
