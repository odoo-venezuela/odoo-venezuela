# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This module was developen by Vauxoo Team:
#    Coded by: javier@vauxoo.com
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
{
    "name" : "Fiscal requirements Venezuelan laws",
    "version" : "0.5",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """Requirements Venezuelan tax laws:
    - Invoice reference
    - Tax-except
    - Required address invoice
    - Unique address invoice.
    - VAT verification for Venezuela rules.
    """,
    'init_xml': [],
    "depends" : ["base", "purchase", "stock", "account"],
    'update_xml': [
        'stock_view.xml',
        'account_invoice_view.xml'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
