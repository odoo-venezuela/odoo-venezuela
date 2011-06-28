#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Angelica Barrios          <angélicaisabelb@gmail.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
#    Planified by: Nhomar Hernande
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
################################################################################

###  
### res_company --> account_management ver si se puede eliminar esta dependencia ####
### retencion_iva, base_vat_ve  ver si se puede eliminar esta dependencia

{
    "name" : "Bank Management",
    "version" : "0.1",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """
    Proporciona los formatos para los cheques venezolanos
    """,
    'init_xml': [],
    "depends" : ["base", "account", "account_voucher"],
    'update_xml': [
        'bank_management_data.xml',
        'bank/bank_view.xml',        
        'bank/res_bank_entity_view.xml',
        'check/check_book_report.xml',
        'check/check_book_view.xml',
        'check/check_note_view.xml',
        'check/check_book_request_sequence.xml',        
        'check/wizard/check_report_general.xml',
        'check/wizard/cancel_wizard.xml',
        'check/wizard/voucher_pay_support_wizard_pay_order.xml',        
#        'check/generate_lines_payment_wizard.xml',
        'check/check_book_request_view.xml',
        'check/data/res.bank.xml',
        'check/res_bank_balance.xml',
        'check/voucher_pay_support_view.xml',
        'check/menu_vouche_view.xml',
        'check/pay_order_view.xml',
        'check/pay_order_contrapartida.xml',
        'check/pay_order_line_view.xml',
        'check/account_voucher_journal_view.xml'
        'security/ir.model.access.csv',
        'bank/data/banesco_data.xml',
        'bank/data/bicentenario_data.xml',
        'bank/data/caribe_bank_data.xml',
        'bank/data/exterior_bank_data.xml',
        'bank/data/fondo_comun_bank_data.xml',
        'bank/data/industrial_data.xml',
        'bank/data/mercantil_bank_data.xml',
        'bank/data/venezuela_bank_data.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
