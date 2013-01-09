#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#    Planified by: Humberto Arocha & Nhomar Hernandez
#    Audited by: Humberto Arocha           <hbto@vauxoo.com>
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
##############################################################################
from  openerp.osv import orm, fields
from tools.translate import _

class fiscal_book(orm.Model):

    def _get_type(self, cr, uid, context=None):
        context = context or {}
        return context.get('type', 'purchase')

    _description = "Venezuela's Sale & Purchase Fiscal Books"
    _name='fiscal.book'
    _columns={
        'name':fields.char('Description', size=256, required=True),
        'company_id':fields.many2one('res.company','Company',
            help='Company',required=True),
        'period_id':fields.many2one('account.period','Period',
            help="Book's Fiscal Period",required=True),
        'type': fields.selection([('sale','Sale Book'),
            ('purchase','Purchase Book')],
            help='Select Sale for Customers and Purchase for Suppliers',
            string='Book Type', required=True),
        'base_amount':fields.float('Taxable Amount',help='Amount used as Taxing Base'),
        'tax_amount':fields.float('Taxed Amount',help='Taxed Amount on Taxing Base'),
        'fbl_ids':fields.one2many('fiscal.book.lines', 'fb_id', 'Book Lines',
            help='Lines being recorded in a Fiscal Book'),
        'fbt_ids':fields.one2many('fiscal.book.taxes', 'fb_id', 'Tax Lines',
            help='Taxes being recorded in a Fiscal Book'),
        'invoice_ids':fields.one2many('account.invoice', 'fb_id', 'Invoices',
            help='Invoices being recorded in a Fiscal Book'),
        'iwdl_ids':fields.one2many('account.wh.iva.line', 'fb_id', 'Vat Withholdings',
            help='Vat Withholdings being recorded in a Fiscal Book'),
    }

    _defaults = {
        'type': _get_type,
        'company_id': lambda s,c,u,ctx: \
            s.pool.get('res.users').browse(c,u,u,context=ctx).company_id.id,
    }

class fiscal_book_lines(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Lines"
    _name='fiscal.book.lines'
    _rec_name='rank'
    _columns={
        'rank':fields.integer('Line Position', required=True),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        'invoice_id':fields.many2one('fiscal.book','Invoice',
            help='Fiscal Book where this line is related to'),
        'iwdl_id':fields.many2one('account.wh.iva.line','Vat Withholding',
            help='Fiscal Book where this line is related to'),
    }

class fiscal_book_taxes(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Lines"
    _name='fiscal.book.taxes'
    _columns={
        'name':fields.char('Description', size=256, required=True),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        'base_amount':fields.float('Taxable Amount',help='Amount used as Taxing Base'),
        'tax_amount':fields.float('Taxed Amount',help='Taxed Amount on Taxing Base'),
    }
