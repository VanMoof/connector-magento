import json
import logging
import requests
import time
from odoo import api, models
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


class MagentoStockUpdate(models.AbstractModel):
    _name = 'magento.stock.update'

    @api.multi
    def _get_magento_endpoint(self, call_type):
        conf = self.env['magento.backend'].search([], limit=1)
        headers = {'Authorization': 'Bearer %s' % conf.password,
                   'Cache-Control': 'no-cache',
                   'Content-Type': 'application/json'}
        url = '{magento_location}/{call_type}'.format(
            magento_location=conf.location, call_type=call_type)
        return url, headers

    @api.multi
    def push_to_magento(self, payload):
        """ Push products list dictionary to Magento
        :param payload dict() """
        url, headers = self._get_magento_endpoint(
            call_type='inventory/source-items')
        _logger.debug('Push product quantity to Magento endpoint %s' % url)
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        res.raise_for_status()
        _logger.debug('Push done. Result %s' % res.status_code)

    @api.multi
    def get_regular_products_dict(self):
        """ Get normal products that are present in Magento and return a list
            of dictionaries to be sent for update of quantity.
        :return: {'sourceItems': [
                    {'sku': (str) binding.magento_id, # magento sku
                    'source_code': (str) warehouse.magento_id, # warehouse code
                    'quantity': (int) quantity,
                    'status': (int) 1},]}
        """
        products = self.env['product.product'].search(
            [('magento_bind_ids', '!=', False)])
        _logger.debug(
            'Update regular products levels products in Magento. %s products',
            len(products))
        payload = {'sourceItems': []}
        for product in openupgrade.chunked(products.sudo()):
            for binding in product.magento_bind_ids:
                stock_field = (
                    binding.backend_id.product_stock_field_id.name or
                    'virtual_available')
                for warehouse in self.env['magento.warehouse'].search(
                        [('active', '=', True),
                         ('backend_id', '=', binding.backend_id.id)]):
                    wh_product = product.with_context(
                        location=warehouse.warehouse_id.lot_stock_id.id)
                    quantity = max(0, wh_product[stock_field])
                    prod_dict = {'sku': binding.external_id,
                                 'source_code': warehouse.magento_id,
                                 'quantity': quantity,
                                 'status': 1 if quantity > 0 else 0}
                    payload['sourceItems'].append(prod_dict)
        return payload

    @api.model
    def set_product_stock_levels_in_magento(self):
        start_time = time.time()
        _logger.debug('Update regular product levels in Magento.')

        payload = self.get_regular_products_dict()
        _logger.debug('Product update payload: %s' % payload)
        if payload and payload.get('sourceItems'):
            self.push_to_magento(payload)

        _logger.debug(
            'Update regular product levels done in %s' %
            (time.time() - start_time))
