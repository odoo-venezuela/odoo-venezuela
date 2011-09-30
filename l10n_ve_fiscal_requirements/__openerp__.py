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
    - Invoice Control Number
    - Tax-except
    - Required address invoice
    - Unique address invoice.
    - VAT verification for Venezuela rules.
    - Damaged invoices justification.
    ---------------------------------------------------------------------------
    For damaged invoices, you must go to the company and, under the configuration section,
    create the corresponding journal and account.

    ------------------------TECH INFO-------------------------------------------
    CHANGELOG:
       - For the migration to the l10n_ve on OpenERP:
         - Changed the Invoice Ref label to Control Number
         - Integrated the l10n_ve_nro_ctrl module functionality on this one
         - Since the concept_id field is added by the l10n_ve_islr_withholding, an
           error es rised if it's not installed and it is necesary to withhold
         - If you need to withhold ISLR, you must install the module mentioned abofe

    FURTHER DEVELOPMENT:
       - Find a way to decouple this module and l10n_ve_islr_withholding
    """,
    'init_xml': [],
    "depends" : ["base", "base_vat", "purchase", "stock", "account"],
    'update_xml': [
        'view/stock_view.xml',
        'view/account_invoice_view.xml',
        'view/res_company_view.xml',
        'wizard/wizard_invoice_nro_ctrl_view.xml'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
