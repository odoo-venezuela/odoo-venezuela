#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>     
#    Planified by: Humberto Arocha / Nhomar Hernandez
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

import time
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _retenida(self, cr, uid, ids, name, args, context):
        res = {}
        if context is None:
            context = {}
        for id in ids:
            res[id] = self.test_retenida(cr, uid, [id])
        return res
    
    def _get_inv_from_line(self, cr, uid, ids, context={}):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _get_inv_from_reconcile(self, cr, uid, ids, context={}):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True
        
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids
    
    _columns = {
        'wh_src': fields.boolean('Social Responsibility Commitment Withheld'),
        'wh_src_rate': fields.float('SRC Wh rate', digits_compute= dp.get_precision('Withhold'), readonly=True, states={'draft':[('readonly',False)]}, help="Social Responsibility Commitment Withholding Rate"),
        'wh_src_id': fields.many2one('account.wh.src', 'Wh. SRC Doc.', readonly=True, help="Social Responsibility Commitment Withholding Document"),        
    }
    _defaults={
        'wh_src': False,
    }

    def _get_move_lines(self, cr, uid, ids, to_wh, period_id, 
                            pay_journal_id, writeoff_acc_id, 
                            writeoff_period_id, writeoff_journal_id, date, 
                            name, context=None):
        if context is None: context = {}
        res = super(account_invoice,self)._get_move_lines(cr, uid, ids, to_wh, period_id, 
                            pay_journal_id, writeoff_acc_id, 
                            writeoff_period_id, writeoff_journal_id, date, 
                            name, context=context)
        if context.get('src_wh',False):
            invoice = self.browse(cr, uid, ids[0])
            
            types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
            direction = types[invoice.type]

            for tax_brw in to_wh:
                if types[invoice.type]==1:
                    acc = tax_brw.wh_id.company_id.wh_src_collected_account_id and tax_brw.wh_id.company_id.wh_src_collected_account_id.id or False
                else:
                    acc = tax_brw.wh_id.company_id.wh_src_paid_account_id and tax_brw.wh_id.company_id.wh_src_paid_account_id.id or False
                if not acc:
                    raise osv.except_osv(_('Missing Account in Tax!'),_("Tax [%s] has missing account. Please, fill the missing fields") % (tax_brw.wh_id.company_id.name,))
                res.append((0,0,{
                    'debit': direction * tax_brw.wh_amount<0 and - direction * tax_brw.wh_amount,
                    'credit': direction * tax_brw.wh_amount>0 and direction * tax_brw.wh_amount,
                    'account_id': acc,
                    'partner_id': invoice.partner_id.id,
                    'ref':invoice.number,
                    'date': date,
                    'currency_id': False,
                    'name':name
                }))
        
        return res

account_invoice()
