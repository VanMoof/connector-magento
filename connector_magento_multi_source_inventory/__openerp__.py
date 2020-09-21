# © 2018 Vanmoof BV (<https://www.vanmoof.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Vanmoof Update Magento Stock',
    'version': '12.0.1.0.0',
    'author': 'Vanmoof B.V.',
    'category': 'Warehouse Management',
    'website': 'https://www.vanmoof.com',
    'depends': [
        'connector_magento',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/magento_source.xml',
    ],
    'installable': True,
}
