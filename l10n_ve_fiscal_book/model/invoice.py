#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
################ Credits ######################################################
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#                    Katherine Zsoral <katherine.zaoral@vauxoo.com>
#    Planified by: Nhomar Hernandez
###############################################################################
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
###############################################################################
from openerp.osv import osv, fields


class inherited_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                 help='Fiscal Book where this line is \
                                 related to'),
        'issue_fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                       help='Fiscal Book where this invoice \
                                       needs to be add'),
    }

inherited_invoice()
