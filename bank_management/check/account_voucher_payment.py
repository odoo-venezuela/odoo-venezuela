#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@vauxoo.com
#############################################################################
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
import decimal_precision as dp


class account_voucher_line(osv.osv):
    _inherit= "account.voucher.line"


    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        currency_pool = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id.id
            move_line = line.move_line_id or False

            if not move_line:
                res[line.id] = 0.0

            if move_line:
                res[line.id] = currency_pool.compute(cr, uid, move_line.currency_id and move_line.currency_id.id or company_currency, voucher_currency, abs(move_line.amount_residual_currency), context=ctx) - line.amount

        return res

    _columns={
        'invoice_id' : fields.many2one('account.invoice','Invoice'),
        'partner_id' : fields.many2one('res.partner','Partner'),
        'amount_residual': fields.function(_amount_residual, method=True, digits_compute=dp.get_precision('Account'), string='Residual Amount', type='float', store=True),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_brw = partner_obj.browse(cr,uid,partner_id,context)
        
        account_id = partner_brw.property_account_payable.id
        account_balance = partner_brw.property_account_payable.balance
   
        res = {'value' : {'account_id':account_id,'amount':abs(account_balance),}}
        return res

    def onchange_invoice_id(self, cr, uid, ids, inv_id, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_brw = invoice_obj.browse(cr,uid,inv_id,context)
        inv_residual = invoice_brw.residual
        aml = self.move_line_id_payment_get(cr, uid, [inv_id])
        res = {'value' : {'amount':inv_residual,'move_line_id':aml[0]}}
        return res

account_voucher_line()


class account_voucher(osv.osv):
    _inherit='account.voucher'

    _columns={
        'one_partner':fields.boolean('One Supplier or Customer ?', required=False, help="Check this box if there only one supplier or customer for this voucher"),
    }

    def onchange_journal_id(self, cr, uid, ids, journal_id, type,context=None):

        account_journal_obj = self.pool.get('account.journal')
        account_brw=account_journal_obj.browse(cr,uid,journal_id,context)
        account_id = account_brw.default_debit_account_id.id
        
        if type=='payment':
            account_id = account_brw.default_credit_account_id.id
            
        res = {'value' : {'account_id':account_id}}
        return res

    def onchange_payment_options(self,cr,uid,ids,payment_option,context=None):

        account_pay_brw = self.browse(cr, uid, ids, context=None)
        account_journal_obj = self.pool.get('account.journal')
        amount=0
        amount_total=0
        writeoff_acc_id=0
        if payment_option== 'with_writeoff':
            for acc_voucher in account_pay_brw:
                for line in acc_voucher.line_ids:
                    amount_total= line.amount + amount_total
                amount = acc_voucher.amount - amount_total
                writeoff_acc_id=account_journal_obj.browse(cr,uid,acc_voucher.journal_id.id,context).default_payment_credit_account_id.id
                if amount >= 0:
                    writeoff_acc_id=account_journal_obj.browse(cr,uid,acc_voucher.journal_id.id,context).default_payment_debit_account_id.id
        
        res = {'value' : {'writeoff_acc_id':writeoff_acc_id}}
        return res


    def validate_amount(self,cr,uid,ids,context=None):
        
        account_pay_brw = self.browse(cr, uid, ids, context=None)
        amount_total=0
        
        for acc_voucher in account_pay_brw:
            if acc_voucher.payment_option== 'without_writeoff':
                for line in acc_voucher.line_ids:
                    amount_total= line.amount + amount_total
            if not amount_total == acc_voucher.amount:
                raise osv.except_osv(_('Bad Total !'),_("Please verify the Amount of Payment !\n The Paid Amount no match the computed total"))
        
        return True

    def proforma_voucher(self, cr, uid, ids, context=None):
        #~ self.action_move_line_create(cr, uid, ids, context=context)
        self.validate_amount(cr,uid,ids,context=context)
        return True




    def add_data(self, cr, uid, ids, parm, datas, context):
        move_line_pool = self.pool.get('account.move.line')
        aml_lst = []
        aml_cr_lst = []
        aml_dr_lst = []
        data = datas.copy()
        if data and data[data.keys()[0]].get('line_ids',False):
            for aml in data[data.keys()[0]]['line_ids']:
                if aml.get('move_line_id',False):
                    aml_brw = move_line_pool.browse(cr, uid, aml['move_line_id'], context=context)
                    aml.update({'invoice_id':aml_brw.invoice.id, 'partner_id':parm['partner_id']})
                    aml_lst.append(aml)
                    if aml['type'] == 'cr':
                        aml_cr_lst.append(aml)
                    else:
                        aml_dr_lst.append(aml)

            data[data.keys()[0]].update({'line_ids':aml_lst,'line_cr_ids':aml_cr_lst,'line_dr_ids':aml_dr_lst})
        print 'data: despues: ',data
        return data

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        data = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id,
            journal_id, price, currency_id, ttype, date, context)
        param = {
            'partner_id':partner_id,
            'journal_id':journal_id,
            'price':price,
            'currency_id':currency_id,
            'ttype':ttype,
            'date':date
        }
        res = self.add_data(cr, uid, ids, param, data, context)

        return res




account_voucher()
