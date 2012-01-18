#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name" : "Venezuelan Account Chart (Aimed at Commercial Trades)",
    "version" : "0.2",
    "author" : "Tiny & Vauxoo",
    "category" : "Localisation/Account Charts",
    "description": 
'''
This Module load a generic format for manage medium and big business.
You will need accounting knowledge to understad some concepts.
''',
    
    "init_xml": ['data/account_tax_code.xml',
                 'data/account_user_types.xml',
                 'data/account_chart.xml',
                 'data/account_account.xml',
                 'data/account_tax.xml',],

    "depends" : ["account",
                 "account_chart"],
    "demo_xml" : [],
    "update_xml" : [
                    'view/account_view.xml',
                    'wizard/l10n_chart_ve_wizard.xml'],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
