#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Israel Fermín Montilla  <israel@openerp.com.ve>          
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
    'name' : 'Registration and Import Management',
    'version' : '0.1',
    'author' : 'Vauxoo',
    'description' : '''
    
    This module adds functionality to the billing module allows to register documendos import and manage them.

    No new menus will be created with the installation of this module, you will find three new fields at the hearing
    in the form of bills. These fields are:

    Boolean Determines if the invoice is import a spreadsheet that is called Import Spreadsheet and in turn displays
    a new tab to complete the import log

    Relational field to the invoice that is directly related to the import document and is called Invoice Affected

    And a char field where it will be placed the number of the import document, this field has the name Number
    
    Also added to the company in view of the configuration pestañana relationship to products, to determine which 
    products will be calculated by company when generating the book buying and selling
    
    ''',
    
    'category' : '',
    'website' : 'http://openerp.com',
    'depends' : ['account'],
    'update_xml' : [
        'view/invoice_view.xml',
        'view/res_company_view.xml',
    ],
    'demo' : [],
    'active' : False,
    'installable': True,
}
