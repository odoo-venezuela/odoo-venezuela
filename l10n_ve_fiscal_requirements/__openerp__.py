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
    "description": """Venezuelan Tax Laws Requirements:
    - Invoice Control Number.
    - Tax-except concept
    - Required address invoice.
    - Unique address invoice.
    - VAT verification for Venezuela rules.
    - Damaged "free forms" justification.
    - Tax Units configuration.
    ---------------------------------------------------------------------------
    For damaged invoices (Free form formats), you must go to the company and, under the configuration section,
    create the corresponding journal and account.

    If you install this module with invoice data on the database, the concept_id will be 
    Empty for all those invoices, so, when you try to modify them you have to add a value on
    that field

    This module should also install a menu item under the accounting configuration menu.
    ------------------------TECH INFO-------------------------------------------
    CHANGELOG:
       - For the migration to the l10n_ve on OpenERP:
         - Added the functionality to configure Tax Units, for this, it was necesary make this module depend on
           account_accountant, to make visible de accounting configuration menu.
         - Added the functionality to change the control number on an invoice (free form format)
         - Changed the Invoice Ref label to Control Number
         - Integrated the l10n_ve_nro_ctrl module functionality on this one
         - Since the concept_id field is added by the l10n_ve_islr_withholding, an
           error es rised if it's not installed and it is necesary to withhold
         - If you need to withhold ISLR, you must install the module mentioned abofe

    """,
    'init_xml': [
        'data/l10n_ut_data.xml',
    ],
    "depends" : ["base_vat", "account", "account_accountant"],
    'update_xml': [
        'security/ir.model.access.csv',
        'view/account_invoice_view.xml',
        'view/res_company_view.xml',
        'view/l10n_ut_view.xml',
        'wizard/wizard_invoice_nro_ctrl_view.xml',
        'wizard/wizard_nro_ctrl_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
