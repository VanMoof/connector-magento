# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
import mock

from openerp import api
from openerp.fields import Datetime
from openerp.modules.registry import RegistryManager
from openerp.tests.common import get_db_name
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.exception import (
    InvalidDataError,
    RetryableJobError,
)
from openerp.addons.connector.queue.job import _unpickle
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.magentoerpconnect.connector import get_environment
from openerp.addons.magentoerpconnect.sale import SaleOrderBatchImport
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    import_batch,
    import_record)
from openerp.addons.magentoerpconnect.product_category import (
    ProductCategoryImporter,
)
from .common import (mock_api,
                     mock_urlopen_image,
                     SetUpMagentoBase,
                     SetUpMagentoSynchronized,
                     )
from .data_base import magento_base_responses


class TestBaseMagento(SetUpMagentoBase):

    def test_import_backend(self):
        """ Synchronize initial metadata """
        with mock_api(magento_base_responses):
            import_batch(self.session, 'magento.website', self.backend_id)
            import_batch(self.session, 'magento.store', self.backend_id)
            import_batch(self.session, 'magento.storeview', self.backend_id)

        website_model = self.env['magento.website']
        websites = website_model.search([('backend_id', '=', self.backend_id)])
        self.assertEqual(len(websites), 2)

        store_model = self.env['magento.store']
        stores = store_model.search([('backend_id', '=', self.backend_id)])
        self.assertEqual(len(stores), 2)

        storeview_model = self.env['magento.storeview']
        storeviews = storeview_model.search(
            [('backend_id', '=', self.backend_id)])
        self.assertEqual(len(storeviews), 4)

        # TODO; install & configure languages on storeviews


class TestImportMagento(SetUpMagentoSynchronized):
    """ Test the imports from a Magento Mock. """

    def test_import_product_category(self):
        """ Import of a product category """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            import_record(self.session, 'magento.product.category',
                          backend_id, 1)

        category_model = self.env['magento.product.category']
        category = category_model.search([('backend_id', '=', backend_id)])
        self.assertEqual(len(category), 1)

    def test_import_product_category_with_gap(self):
        """ Import of a product category when parent categories are missing """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            import_record(self.session, 'magento.product.category',
                          backend_id, 8)

        category_model = self.env['magento.product.category']
        categories = category_model.search([('backend_id', '=', backend_id)])
        self.assertEqual(len(categories), 4)

    def test_import_product(self):
        """ Import of a simple product """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.product.product',
                              backend_id, 16)

        product_model = self.env['magento.product.product']
        product = product_model.search([('backend_id', '=', backend_id),
                                        ('magento_id', '=', '16')])
        self.assertEqual(len(product), 1)

    def test_import_product_category_missing(self):
        """ Import of a simple product when the category is missing """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.product.product',
                              backend_id, 25)

        product_model = self.env['magento.product.product']
        product = product_model.search([('backend_id', '=', backend_id),
                                        ('magento_id', '=', '25')])
        self.assertEqual(len(product), 1)

    def test_import_product_configurable(self):
        """ Import of a configurable product : no need to import it """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.product.product',
                              backend_id, 126)

        product_model = self.env['magento.product.product']
        products = product_model.search([('backend_id', '=', backend_id),
                                         ('magento_id', '=', '126')])
        self.assertEqual(len(products), 0)

    def test_import_product_bundle(self):
        """ Bundle should fail: not yet supported """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with self.assertRaises(InvalidDataError):
                import_record(self.session,
                              'magento.product.product',
                              backend_id, 165)

    def test_import_product_grouped(self):
        """ Grouped should fail: not yet supported """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with self.assertRaises(InvalidDataError):
                import_record(self.session,
                              'magento.product.product',
                              backend_id, 54)

    def test_import_product_virtual(self):
        """ Virtual products are created as service products """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            import_record(self.session,
                          'magento.product.product',
                          backend_id, 144)

        product_model = self.env['magento.product.product']
        product = product_model.search([('backend_id', '=', backend_id),
                                        ('magento_id', '=', '144')])
        self.assertEqual(product.type, 'service')

    def test_import_sale_order(self):
        """ Import sale order: check """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.sale.order',
                              backend_id, 900000691)
        order_model = self.env['magento.sale.order']
        order = order_model.search([('backend_id', '=', backend_id),
                                    ('magento_id', '=', '900000691')])
        self.assertEqual(len(order), 1)
        self.assertEqual(order.payment_term, self.payment_term,
                         "If the payment term is empty, the onchanges have not"
                         " been applied.")

    def test_import_sale_order_no_website_id(self):
        """ Import sale order: website_id is missing, happens with magento """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.sale.order',
                              backend_id, 900000692)
        order_model = self.env['magento.sale.order']
        order = order_model.search([('backend_id', '=', backend_id),
                                    ('magento_id', '=', '900000692')])
        self.assertEqual(len(order), 1)

    def test_import_sale_order_with_prefix(self):
        """ Import sale order with prefix """
        backend = self.backend_model.browse(self.backend_id)
        backend.write({'sale_prefix': 'EC'})
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.sale.order',
                              backend.id, 900000693)
        order_model = self.env['magento.sale.order']
        order = order_model.search([('backend_id', '=', backend.id),
                                    ('magento_id', '=', '900000693')])
        self.assertEqual(len(order), 1)
        self.assertEqual(order.name, 'EC900000693')

    def test_import_sale_order_with_configurable(self):
        """ Import sale order with configurable product """
        backend_id = self.backend_id
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.sale.order',
                              backend_id, 900000694)
        mag_order_model = self.env['magento.sale.order']
        mag_order = mag_order_model.search([('backend_id', '=', backend_id),
                                            ('magento_id', '=', '900000694')])
        self.assertEqual(len(mag_order), 1)
        mag_order_line_model = self.env['magento.sale.order.line']
        mag_order_line = mag_order_line_model.search(
            [('backend_id', '=', backend_id),
             ('magento_order_id', '=', mag_order.id)])
        self.assertEqual(len(mag_order_line), 1)
        order_line = mag_order_line.openerp_id
        price_unit = order_line.price_unit
        # Prices have been propagated from the child to the parent item as per
        # customization
        self.assertAlmostEqual(price_unit, 41.0500)

    def crete_next_fiscalyear_and_periods(self):
        fiscalyear_obj = self.env['account.fiscalyear']
        year = str(datetime.now().year + 1)
        for company in self.env['res.company'].search([]):
            fiscalyear_id = fiscalyear_obj.create({
                'name': year,
                'code': year,
                'date_start': year + '-01-01',
                'date_stop': year + '-12-31',
                'company_id': company.id
            })
            fiscalyear_id.create_period()

    def test_import_sale_order_with_taxes_included(self):
        """ Import sale order with taxes included """
        self.crete_next_fiscalyear_and_periods()
        backend_id = self.backend_id
        storeview_model = self.env['magento.storeview']
        storeview = storeview_model.search([('backend_id', '=', backend_id),
                                            ('magento_id', '=', '1')])
        storeview.write({'catalog_price_tax_included': True})
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.sale.order',
                              backend_id, 900000695)
        mag_order_model = self.env['magento.sale.order']
        mag_order = mag_order_model.search([('backend_id', '=', backend_id),
                                            ('magento_id', '=', '900000695')])
        self.assertEqual(len(mag_order), 1)
        order = mag_order.openerp_id
        amount_total = order.amount_total
        # 97.5 is the amount_total if connector takes correctly included
        # tax prices.
        self.assertAlmostEqual(amount_total, 97.5000)

    def test_import_sale_order_with_discount(self):
        """ Import sale order with discounts"""
        self.crete_next_fiscalyear_and_periods()
        backend_id = self.backend_id
        storeview_model = self.env['magento.storeview']
        storeview = storeview_model.search([('backend_id', '=', backend_id),
                                            ('magento_id', '=', '2')])
        storeview.write({'catalog_price_tax_included': True})
        with mock_api(magento_base_responses):
            with mock_urlopen_image():
                import_record(self.session,
                              'magento.sale.order',
                              backend_id, 900000696)
        mag_order_model = self.env['magento.sale.order']
        mag_order = mag_order_model.search([('backend_id', '=', backend_id),
                                            ('magento_id', '=', '900000696')])
        self.assertEqual(len(mag_order), 1)
        order = mag_order.openerp_id
        self.assertAlmostEqual(order.amount_total, 36.9500)

        for line in order.order_line:
            if line.name == 'Item 1':
                self.assertAlmostEqual(line.discount, 11.904)
            elif line.name == 'Item 2':
                self.assertAlmostEqual(line.discount, 11.957)
            else:
                self.fail('encountered unexpected sale '
                          'order line %s' % line.name)


class TestImportMagentoConcurrentSync(SetUpMagentoSynchronized):

    def setUp(self):
        super(TestImportMagentoConcurrentSync, self).setUp()
        self.registry2 = RegistryManager.get(get_db_name())
        self.cr2 = self.registry2.cursor()
        self.env2 = api.Environment(self.cr2, self.env.uid, {})
        backend2 = mock.MagicMock(name='Backend Record')
        backend2._name = 'magento.backend'
        backend2.id = self.backend_id
        self.backend2 = backend2
        self.connector_session2 = ConnectorSession.from_env(self.env2)

        @self.addCleanup
        def reset_cr2():
            # rollback and close the cursor, and reset the environments
            self.env2.reset()
            self.cr2.rollback()
            self.cr2.close()

    def test_concurrent_import(self):
        connector_env = ConnectorEnvironment(
            self.backend,
            self.session,
            'magento.product.category'
        )
        importer = ProductCategoryImporter(connector_env)
        with mock_api(magento_base_responses):
            importer.run(1)

        connector_env2 = ConnectorEnvironment(
            self.backend2,
            self.connector_session2,
            'magento.product.category'
        )
        importer2 = ProductCategoryImporter(connector_env2)
        fields_path = ('openerp.addons.magentoerpconnect'
                       '.unit.import_synchronizer.fields')
        with mock.patch(fields_path):
            with self.assertRaises(RetryableJobError):
                importer2.run(1)


class TestImportDelay(SetUpMagentoSynchronized):
    def test_import_delay(self):
        """ Batch import delay is honoured when importing orders """
        storeview = self.env['magento.storeview'].search(
            [('backend_id', '=', self.backend_id)], limit=1)
        max_job_id = self.env['queue.job'].search(
            [], order='id desc', limit=1).id or 0
        self.env['magento.backend'].browse(
            self.backend_id).batch_import_delay = 35
        storeview.import_orders_from_date = datetime.now() - timedelta(hours=2)
        storeview.import_sale_orders()
        _35_minutes_ago = datetime.now() - timedelta(minutes=35)
        _36_minutes_ago = datetime.now() - timedelta(minutes=36)
        self.assertTrue(
            _36_minutes_ago < Datetime.from_string(
                storeview.import_orders_from_date) < _35_minutes_ago)
        job = self.env['queue.job'].search([('id', '>', max_job_id)])
        self.assertTrue(job)
        _name, args, _kwargs = _unpickle(job.func)
        self.assertTrue(_36_minutes_ago < args[2]['to_date'] < _35_minutes_ago)


class TestNoDuplicateOrderImports(SetUpMagentoSynchronized):
    def test_no_duplicate_orders(self):
        """ No duplicate import jobs are created except for failed imports """
        session = ConnectorSession.from_env(self.env)
        env = get_environment(
            session, 'magento.sale.order', self.backend_id)
        importer = env.get_connector_unit(SaleOrderBatchImport)
        max_job_id = self.env['queue.job'].search(
            [], order='id desc', limit=1).id or 0
        magento_id = 999999
        importer._import_record(magento_id)
        job = self.env['queue.job'].search(
            [('id', '>', max_job_id), ('func_string', 'like', magento_id)])
        self.assertEqual(len(job), 1)

        importer._import_record(magento_id)
        job = self.env['queue.job'].search(
            [('id', '>', max_job_id), ('func_string', 'like', magento_id)])
        self.assertEqual(len(job), 1)

        job.state = 'failed'
        importer._import_record(magento_id)
        job = self.env['queue.job'].search(
            [('id', '>', max_job_id), ('func_string', 'like', magento_id)])
        self.assertEqual(len(job), 2)
