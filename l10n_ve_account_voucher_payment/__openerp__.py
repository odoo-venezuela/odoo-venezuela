#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              María Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
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
    "name" : "Invoice Payment/Receipt by Vouchers.",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "Generic Modules/Indian Accounting",
    "website": "http://wiki.openerp.org.ve/",
    "description": '''
                    This module includes :
                    * It reconcile the invoice (supplier, customer) while paying through Accounting Vouchers
                    A Voucher, is defined like some document that involve a banking transaction.
                    the Objective, is, one time the credit and collection people load some payment on the system, every voucher
                    Loaded on system should be reconcilied with a bank statment by Accounting people.
                   ''',
    "depends" : [   "base",
                    "account",
                    "account_voucher",
                ],
    "init_xml" : [],
    "update_xml" : [
            "security/account_voucher_group.xml",
            "account_voucher_payment_view.xml",
            "account_view.xml",
    ],
    "active": False,
    "installable": True
}
