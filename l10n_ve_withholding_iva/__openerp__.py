#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by:  Javier Duran              <javier@nvauxoo.com>
#               Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#               Nhomar Hernandez          <nhomar@vauxoo.com>
#               Humberto Arocha           <hbto@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
{
    "name" : "Management withholding vat based in the Venezuelan tax laws",
    "version" : "1.0",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """Management withholding vat based in the Venezuelan tax laws.

 - Create from invoice voucher withholding vat, to validate invoice.
 - Generate new tag in the view of partner for  add information basic of withholdings vat.
 - Generate file .txt required by Venezuelan law, based in the withholdings vat made during period defined for users.
 - Generate voucher of withholding vat based in the Venezuelan tax laws. 

**Recommendations:**

 - If you want to be able to print the vat withholding report correctly, It is recomended to define the size of the logo of the company in 886 x 236 pixeles.
""",
    'init_xml': [],
    "depends" : ["l10n_ve_withholding"],
    'update_xml': [
        'security/wh_iva_security.xml',
        'security/ir.model.access.csv',
        'report/withholding_vat_report.xml',
        'wizard/wizard_retention_view.xml',
        'view/generate_txt_view.xml',
        'view/account_invoice_view.xml',
        'view/account_view.xml',
        'view/partner_view.xml',
        'view/res_company_view.xml',
        'view/wh_iva_view.xml',
        "data/l10n_ve_withholding_data.xml",
        'report/txt_wh_report.xml',
        "workflow/wh_iva_workflow.xml",
        "workflow/wh_action_server.xml",        
    ],
    'demo_xml': ["demo/l10n_ve_withholding_iva_demo.xml"],
    'test': [
            'test/iva_purchase.yml',
            'test/iva_purchase_wh.yml',
            'test/iva_purchase_nret1.yml',
            'test/iva_purchase_nret2.yml',
            'test/iva_purchase_nret3.yml',
            'test/iva_sale.yml',
            'test/iva_sale_wh.yml',
            'test/iva_test_invoice.yml',
            'test/iva_test_wh.yml',
            'test/iva_test_wh_2.yml',
            'test/iva_test_wh_3.yml',
            'test/iva_test_wh_4.yml',
        ],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
