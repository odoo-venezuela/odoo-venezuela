# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _


class account_voucher(osv.osv):
    _inherit='account.voucher'



    def _get_company_currency(self, cr, uid, voucher_id, context=None):
        '''
        Get the currency of the actual company.

        :param voucher_id: Id of the voucher what i want to obtain company currency.
        :return: currency id of the company of the voucher
        :rtype: int
        '''
        return self.pool.get('account.voucher').browse(cr,uid,voucher_id,context).journal_id.company_id.currency_id.id

    def _get_current_currency(self, cr, uid, voucher_id, context=None):
        '''
        Get the currency of the voucher.

        :param voucher_id: Id of the voucher what i want to obtain current currency.
        :return: currency id of the voucher
        :rtype: int
        '''
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        return voucher.currency_id.id or self._get_company_currency(cr,uid,voucher.id,context)


    def _sel_context(self, cr, uid, voucher_id,context=None):
        """
        Select the context to use accordingly if it needs to be multicurrency or not.

        :param voucher_id: Id of the actual voucher
        :return: The returned context will be the same as given in parameter if the voucher currency is the same
                 than the company currency, otherwise it's a copy of the parameter with an extra key 'date' containing
                 the date of the voucher.
        :rtype: dict
        """
        company_currency = self._get_company_currency(cr, uid, voucher_id, context)
        current_currency = self._get_current_currency(cr, uid, voucher_id, context)
        if current_currency <> company_currency:
            context_multi_currency = context.copy()
            voucher_brw = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
            context_multi_currency.update({'date': voucher_brw.date})
            return context_multi_currency
        return context


    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        move_obj = self.pool.get('account.move')
        seq_obj = self.pool.get('ir.sequence')
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher_brw.number:
            name = voucher_brw.number
        elif voucher_brw.journal_id.sequence_id:
            name = seq_obj.get_id(cr, uid, voucher_brw.journal_id.sequence_id.id)
        else:
            raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))
        if not voucher_brw.reference:
            ref = name.replace('/','')
        else:
            ref = voucher_brw.reference

        move = {
            'name': name,
            'journal_id': voucher_brw.journal_id.id,
            'narration': voucher_brw.narration,
            'date': voucher_brw.date,
            'ref': ref,
            'period_id': voucher_brw.period_id and voucher_brw.period_id.id or False
        }
        move_id = move_obj.create(cr, uid, move)
        return move


    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        '''
        Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        # TODO: is there any other alternative then the voucher type ??
        # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
        if voucher_brw.type in ('purchase', 'payment'):
            credit = currency_obj.compute(cr, uid, current_currency, company_currency, voucher_brw.amount, context=context)
        elif voucher_brw.type in ('sale', 'receipt'):
            debit = currency_obj.compute(cr, uid, current_currency, company_currency, voucher_brw.amount, context=context)
        if debit < 0:
            credit = -debit
            debit = 0.0
        if credit < 0:
            debit = -credit
            credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
            'name': voucher_brw.name or '/',
            'debit': debit,
            'credit': credit,
            'account_id': voucher_brw.account_id.id,
            'move_id': move_id,
            'journal_id': voucher_brw.journal_id.id,
            'period_id': voucher_brw.period_id.id,
            'partner_id': voucher_brw.partner_id.id,
            'currency_id': company_currency <> current_currency and  current_currency or False,
            'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
            'date': voucher_brw.date,
            'date_maturity': voucher_brw.date_due
        }
        return move_line


    def voucher_move_line_get_item(self, cr, uid, voucher, line, move_id, company_currency, current_currency):
        return {
            'journal_id': voucher.journal_id.id,
            'period_id': voucher.period_id.id,
            'name': line.name and line.name or '/',
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': voucher.partner_id.id,
            'currency_id': company_currency <> current_currency and current_currency or False,
            'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
            'quantity': 1,
            'credit': 0.0,
            'debit': 0.0,
            'date': voucher.date
        }


    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(int, list of int)
        '''
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tot_line = line_total
        rec_lst_ids = []

        if context is None:
            context = {}

        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        for line in voucher_brw.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.amount:
                continue
            #we check if the voucher line is fully paid or not and create a move line to balance the payment and initial invoice if needed
            if line.amount == line.amount_unreconciled:
                amount = line.move_line_id.amount_residual #residual amount in company currency
            else:
                amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.untax_amount or line.amount, context=context)
            move_line = self.voucher_move_line_get_item(cr, uid, voucher_brw, line, move_id, company_currency, current_currency)
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher_brw.tax_id and voucher_brw.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher_brw.tax_id.id,
                })
            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))
            sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
            move_line['amount_currency'] = company_currency <> current_currency and sign * line.amount or 0.0
            voucher_line = move_line_obj.create(cr, uid, move_line)
            if line.move_line_id.id:
                rec_ids = [voucher_line, line.move_line_id.id]
                rec_lst_ids.append(rec_ids)

        return (tot_line, rec_lst_ids)

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        '''
        Set a dict to be use to create the writeoff move line.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param line_total: Amount remaining to be allocated on lines.
        :param move_id: Id of account move where this line will be added.
        :param name: Description of account move line.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        move_line = {}

        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        inv_currency_id = voucher_brw.currency_id or voucher_brw.journal_id.currency or voucher_brw.journal_id.company_id.currency_id

        if not currency_obj.is_zero(cr, uid, inv_currency_id, line_total):
            diff = line_total
            account_id = False
            if voucher_brw.payment_option == 'with_writeoff':
                account_id = voucher_brw.writeoff_acc_id.id
            elif voucher_brw.type in ('sale', 'receipt'):
                account_id = voucher_brw.partner_id.property_account_receivable.id
            else:
                account_id = voucher_brw.partner_id.property_account_payable.id
            move_line = {
                'name': name,
                'account_id': account_id,
                'move_id': move_id,
                'partner_id': voucher_brw.partner_id.id,
                'date': voucher_brw.date,
                'credit': diff > 0 and diff or 0.0,
                'debit': diff < 0 and -diff or 0.0,
                #'amount_currency': company_currency <> current_currency and currency_obj.compute(cr, uid, company_currency, current_currency, diff * -1, context=context) or 0.0,
                #'currency_id': company_currency <> current_currency and current_currency or False,
            }

        return move_line


    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        currency_pool = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            context = self._sel_context(cr, uid, voucher.id, context)
            #Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            #create the first line manually
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
            mov_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            rec_list_ids = []
            line_total = mov_line_brw.debit - mov_line_brw.credit
            if voucher.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context)
            elif voucher.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context)

            #create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
            #create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                ml_writeoff_id = move_line_pool.create(cr, uid, ml_writeoff, context)
            #We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            move_pool.post(cr, uid, [move_id], context={})
            #reconcile move line
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids)
        return True



account_voucher()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
