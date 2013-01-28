#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Javier Duran <jduran@corvus.com.ve>           
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

import time
from osv import fields, osv



class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def _get_move_lines(self, cr, uid, ids, to_wh, period_id, 
                            pay_journal_id, writeoff_acc_id, 
                            writeoff_period_id, writeoff_journal_id, date, 
                            name, context=None):
        if context is None: context = {}
        res = super(account_invoice,self)._get_move_lines(cr, uid, ids, to_wh, period_id, 
                            pay_journal_id, writeoff_acc_id, 
                            writeoff_period_id, writeoff_journal_id, date, 
                            name, context=context)
        if context.get('muni_wh',False):
            invoice = self.browse(cr, uid, ids[0])
            types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
            direction = types[invoice.type]
            res.append((0,0,{
                'debit': direction * to_wh.amount<0 and - direction * to_wh.amount,
                'credit': direction * to_wh.amount>0 and direction * to_wh.amount,
                'partner_id': invoice.partner_id.id,
                'ref':invoice.number,
                'date': date,
                'currency_id': False,
                'name':name,
                'account_id': to_wh.retention_id.account_id.id,
            }))
        return res


    def _retenida_munici(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            res[id] = self.test_retenida_muni(cr, uid, [id], 'retmun')
        return res


    def test_retenida_muni(self, cr, uid, ids, *args):     
        type2journal = {'out_invoice': 'mun_sale', 'in_invoice': 'mun_purchase', 'out_refund': 'mun_sale', 'in_refund': 'mun_purchase'}
        type_inv = self.browse(cr, uid, ids[0]).type
        type_journal = type2journal.get(type_inv, 'mun_purchase')      
        res = self.ret_payment_get(cr, uid, ids)
        if not res:
            return False
        ok = True

        cr.execute('select \
                l.id \
            from account_move_line l \
                inner join account_journal j on (j.id=l.journal_id) \
            where l.id in ('+','.join(map(str,res))+') and j.type='+ '\''+type_journal+'\'')
        ok = ok and  bool(cr.fetchone())
        return ok


    def _get_inv_munici_from_line(self, cr, uid, ids, context={}):
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

    def _get_inv_munici_from_reconcile(self, cr, uid, ids, context={}):
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
        'wh_local': fields.function(_retenida_munici, method=True, string='Local Withholding', type='boolean',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, None, 50),
                'account.move.line': (_get_inv_munici_from_line, None, 50),
                'account.move.reconcile': (_get_inv_munici_from_reconcile, None, 50),
            },
            help="The account moves of the invoice have been withheld with account moves of the payment(s)."),
        'wh_muni_id': fields.many2one('account.wh.munici', 'Wh. Municipality', readonly=True, help="Withholding muni."), 

    }
    




account_invoice()




