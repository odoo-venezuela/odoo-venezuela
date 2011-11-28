#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-20011S Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv
from osv import fields
from tools.translate import _
import time
import datetime
import decimal_precision as dp


class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    name = 'acc.voucher.line.multi.partner'


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



    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, invoice_id, context=None):
        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
#        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        invoice_pool = self.pool.get('account.invoice')
#        partner_brw = partner_pool.browse(cr,uid,partner_id,context=context)
        journal_brw = journal_pool.browse(cr, uid, journal_id, context=context)
        default = {}
        default.setdefault('value',{})

        currency_id = currency_id or journal_brw.company_id.currency_id.id

        if not partner_id:
            return default

        default['value']['partner_id'] = partner_id

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0


        if not invoice_id:
            return default

        default['value']['invoice_id'] = invoice_id
        invoice_brw = invoice_pool.browse(cr, uid, invoice_id, context=context)
        ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id), ('move_id', '=', invoice_brw.move_id.id)], context=context)
        moves = move_line_pool.browse(cr, uid, ids, context=context)


        company_currency = journal_brw.company_id.currency_id.id
        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue

            if line.currency_id and currency_id==line.currency_id.id:
                total_credit += line.amount_currency <0 and -line.amount_currency or 0.0
                total_debit += line.amount_currency >0 and line.amount_currency or 0.0
            else:
                total_credit += currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or 0.0)
                total_debit += currency_pool.compute(cr, uid, company_currency, currency_id, line.debit or 0.0)

        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue

            if line.currency_id and currency_id==line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))

            #original_amount = line.credit or line.debit or 0.0
            #amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
            default['value'].update({
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,

            })

            if line.credit:
                amount = min(amount_unreconciled, total_debit)
                default['value']['amount'] = amount
                total_debit -= amount
            else:
                amount = min(amount_unreconciled, total_credit)
                default['value']['amount'] = amount
                total_credit -= amount

#            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
#                default['value']['pre_line'] = 1
#            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
#                default['value']['pre_line'] = 1
#            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)

        return default


account_voucher_line()


class account_voucher(osv.osv):
    _inherit='account.voucher'
    name='account.voucher.multi.partner'

    _columns={
        'multi_partner':fields.boolean('Several Supplier or Customer ?', required=False, help="Check this box if there are twice or more supplier or customer for this voucher"),
    }



    def onchange_journal_multi_partner(self, cr, uid, ids, journal_id, context=None):
        vals = {'value': {}}
        if not journal_id:
            return vals
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)

#        vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)

        currency_id = False #journal.company_id.currency_id.id
        if journal.currency:
            currency_id = journal.currency.id
        vals['value'].update({'currency_id':currency_id})

        # TODO: Debo averiguar cual es la cuenta del voucher, ¿Asumo siempre la del diario?
#        account_id = False
#        if journal.type in ('sale','sale_refund'):
#            account_id = partner.property_account_receivable.id
#        elif journal.type in ('purchase', 'purchase_refund','expense'):
#            account_id = partner.property_account_payable.id
#        else:
#            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
        account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
        vals['value']['account_id'] = account_id
        return vals

    def onchange_date_multi_partner(self, cr, uid, ids, journal_id, date, context=None):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        period_pool = self.pool.get('account.period')
        res = self.onchange_journal_multi_partner(cr, uid, ids, journal_id, context=context)
        pids = period_pool.search(cr, uid, [('date_start', '<=', date), ('date_stop', '>=', date)])
        if pids:
            if not 'value' in res:
                res['value'] = {}
            res['value'].update({'period_id':pids[0]})
        return res

    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        data = super(account_voucher, self).first_move_line_get(cr, uid, voucher_id, move_id, company_currency, current_currency, context)
        data.update({'partner_id':False})
        return data


    def voucher_move_line_get_item(self, cr, uid, voucher, line, move_id, company_currency, current_currency):
        data = super(account_voucher, self).voucher_move_line_get_item(cr, uid, voucher, line, move_id, company_currency, current_currency)
        data.update({'partner_id':line.partner_id.id})
        return data


    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher_brw.multi_partner:
            #TODO hacer cuenta contable de ajuste en la compañía y evaluar un monto mínimo para realizar el asiento de ajuste
            return {}
        return super(account_voucher, self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context)


    def check_amount_total(self, cr, uid, ids, context=None):
        for voucher_brw in self.browse(cr, uid, ids,context):
            amount = 0.0
            for line in voucher_brw.line_ids:
                amount+= line.amount
            if amount != voucher_brw.amount and voucher_brw.multi_partner or amount == 0.0:
                raise osv.except_osv(_('Invalid action !'), _('Cannot validate Voucher(s) with bad total !'))
        return True

    def proforma_voucher(self, cr, uid, ids, context=None):
        self.check_amount_total(cr, uid, ids, context=context)
        return super(account_voucher, self).proforma_voucher(cr, uid, ids, context)

account_voucher()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
