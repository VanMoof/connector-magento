import responses
import json
from odoo.tests.common import TransactionCase


class TestStockWarehouse(TransactionCase):

    def set_quantity(self, location, product, quantity):
        # create stock at location (update product quantity)
        wiz = self.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'new_quantity': quantity,
            'location_id': location.id})
        wiz.change_product_qty()

    @responses.activate
    def test_product_qty_per_location(self):
        self.regular_prod_payload = []

        def callback(request):
            payload = json.loads(request.body)
            self.regular_prod_payload = payload.get('sourceItems')
            return 200, {}, '"OK"'
        responses.add_callback(
            responses.POST,
            'https://test3.vanmoof.com/rest/V1/inventory/source-items',
            callback=callback)

        self.warehouse = self.env.ref('stock.warehouse0')
        self.backend = self.env['magento.backend'].create({
            'name': 'Test Magento',
            'version': '2.0',
            'location': 'https://test3.vanmoof.com/rest/V1',
            'username': 'username',
            'warehouse_id': self.warehouse.id,
            'password': '42',
        })
        self.product = self.env.ref('product.product_product_3')
        self.magento_product = self.env['magento.product.product'].create({
            'name': 'Bla',
            'product_type': 'simple',
            'backend_id': self.backend.id,
            'manage_stock': 'use_default',
            'openerp_id': self.product.id,
            'backorders': 'use_default',
            'external_id': 'VM01-061'})
        self.magento_warehouse = self.env['magento.warehouse'].create({
            'warehouse_id': self.warehouse.id,
            'backend_id': self.backend.id,
            'magento_id': 'default',
        })

        # execute cron
        self.env['magento.stock.update'].set_product_stock_levels_in_magento()

        expected_regular = {'sku': self.magento_product.external_id,
                            'status': 0,
                            'source_code': self.magento_warehouse.magento_id,
                            'quantity': 0}
        self.assertEqual(self.regular_prod_payload, [expected_regular])
