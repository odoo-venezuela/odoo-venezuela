# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This module was developen by Vauxoo Team:
#    Coded by: javier@vauxoo.com
#
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
    "name" : "Withholding vat Venezuelan laws",
    "version" : "0.6",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """Management withholding vat for Venezuelan tax laws
    """,
    'init_xml': [],
    "depends" : ["l10n_ve_withholding"],
    'update_xml': [
        'security/wh_iva_security.xml',
        'security/ir.model.access.csv',
        'res_company_view.xml',    
        'account_invoice_view.xml',
        'account_view.xml',
        'partner_view.xml',        
        'wh_iva_view.xml',
        "wh_iva_sequence.xml",
        "wh_iva_workflow.xml",
        "account_workflow.xml",        
        "l10n_ve_withholding_iva_installer.xml",
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
