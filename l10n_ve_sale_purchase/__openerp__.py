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
    'name' : 'ISLR Sale and Purchase Functionalities',
    'version' : '0.2',
    'author' : 'Vauxoo',
    'description' : '''
        Due to the Dependendy reduction on the l10n_ve_islr_withholding module, it was necesary to incorporate
        the functionalities wich has to do with the eliminated dependencies on another module. That's what this one
        was created for.
    ''',
    'category' : '',
    'website' : 'http://openerp.com',
    'depends' : ['sale', 'purchase', 'stock', 'l10n_ve_islr_withholding'],
    'update_xml' : [
        'view/product_view.xml',
        'view/stock_view.xml',
        'view/purchase_view.xml',
        'view/sale_order_view.xml',
    ],
    'demo' : [],
    'active' : False,
    'installable': True,
}
