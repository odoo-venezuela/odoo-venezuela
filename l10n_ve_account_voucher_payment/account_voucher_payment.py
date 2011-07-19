#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
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
    
    _columns={
        'invoice_id' : fields.many2one('account.invoice','Invoice'),
        'partner_id' : fields.many2one('res.partner','Partner'),
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

        res = {'value' : {'amount':inv_residual,}}
        return res

account_voucher_line()


class account_voucher(osv.osv):
    
    _inherit='account.voucher'
    
    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        account_journal_obj = self.pool.get('account.journal')
        account_id = account_journal_obj.browse(cr,uid,journal_id,context).default_credit_account_id.id
        res = {'value' : {'account_id':account_id}}
        
        return res
    
account_voucher()
    


#~ class account_voucher(osv.osv):
#~ 
    #~ _name='account.voucher.payment'
#~ 
    #~ def _get_period(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ if context.get('period_id', False):
            #~ return context.get('period_id')
        #~ periods = self.pool.get('account.period').find(cr, uid)
        #~ return periods and periods[0] or False
#~ 
    #~ def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        #~ if not ids: return {}
        #~ res = {}
        #~ debit = credit = 0.0
        #~ for voucher in self.browse(cr, uid, ids, context=context):
            #~ for l in voucher.line_dr_ids:
                #~ debit += l.amount
            #~ for l in voucher.line_cr_ids:
                #~ credit += l.amount
            #~ res[voucher.id] =  abs(voucher.amount - abs(credit - debit))
        #~ return res
        #~ 
    #~ def _get_narration(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ return context.get('narration', False)
        #~ 
    #~ def _get_reference(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ return context.get('reference', False)
#~ 
    #~ def _get_currency(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ journal_pool = self.pool.get('account.journal')
        #~ journal_id = context.get('journal_id', False)
        #~ if journal_id:
            #~ journal = journal_pool.browse(cr, uid, journal_id, context=context)
#~ #            currency_id = journal.company_id.currency_id.id
            #~ if journal.currency:
                #~ return journal.currency.id
        #~ return False
#~ 
    #~ def _get_journal(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ journal_pool = self.pool.get('account.journal')
        #~ invoice_pool = self.pool.get('account.invoice')
        #~ if context.get('invoice_id', False):
            #~ currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
            #~ journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id)], limit=1)
            #~ return journal_id and journal_id[0] or False
        #~ if context.get('journal_id', False):
            #~ return context.get('journal_id')
        #~ if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            #~ return context.get('search_default_journal_id')
#~ 
        #~ ttype = context.get('type', 'bank')
        #~ if ttype in ('payment', 'receipt'):
            #~ ttype = 'bank'
        #~ res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
        #~ return res and res[0] or False
#~ 
    #~ def _get_amount(self, cr, uid, context=None):
        #~ if context is None:
            #~ context= {}
        #~ return context.get('amount', 0.0)
#~ 
    #~ def _get_type(self, cr, uid, context=None):
        #~ if context is None:
            #~ context = {}
        #~ return context.get('type', False)
#~ 
    #~ def _get_tax(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ journal_pool = self.pool.get('account.journal')
        #~ journal_id = context.get('journal_id', False)
        #~ if not journal_id:
            #~ ttype = context.get('type', 'bank')
            #~ res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
            #~ if not res:
                #~ return False
            #~ journal_id = res[0]
#~ 
        #~ if not journal_id:
            #~ return False
        #~ journal = journal_pool.browse(cr, uid, journal_id, context=context)
        #~ account_id = journal.default_credit_account_id or journal.default_debit_account_id
        #~ if account_id and account_id.tax_ids:
            #~ tax_id = account_id.tax_ids[0].id
            #~ return tax_id
        #~ return False
#~ 
    #~ _columns = {
        #~ 'type':fields.selection([
            #~ ('sale','Sale'),
            #~ ('purchase','Purchase'),
            #~ ('payment','Payment'),
            #~ ('receipt','Receipt'),
        #~ ],'Default Type', readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'name':fields.char('Memo', size=256, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'date':fields.date('Date', readonly=True, select=True, states={'draft':[('readonly',False)]}, help="Effective date for accounting entries"),
        #~ 'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'account_id':fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'line_ids':fields.one2many('account.voucher.line','voucher_id','Voucher Lines', readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'line_cr_ids':fields.one2many('account.voucher.line','voucher_id','Credits',
            #~ domain=[('type','=','cr')], context={'default_type':'cr'}, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'line_dr_ids':fields.one2many('account.voucher.line','voucher_id','Debits',
            #~ domain=[('type','=','dr')], context={'default_type':'dr'}, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'narration':fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'currency_id':fields.many2one('res.currency', 'Currency', readonly=True, states={'draft':[('readonly',False)]}),
#~ #        'currency_id': fields.related('journal_id','currency', type='many2one', relation='res.currency', string='Currency', store=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'state':fields.selection(
            #~ [('draft','Draft'),
             #~ ('proforma','Pro-forma'),
             #~ ('posted','Posted'),
             #~ ('cancel','Cancelled')
            #~ ], 'State', readonly=True, size=32,
            #~ help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Voucher. \
                        #~ \n* The \'Pro-forma\' when voucher is in Pro-forma state,voucher does not have an voucher number. \
                        #~ \n* The \'Posted\' state is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        #~ \n* The \'Cancelled\' state is used when user cancel voucher.'),
        #~ 'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'reference': fields.char('Ref #', size=64, readonly=True, states={'draft':[('readonly',False)]}, help="Transaction reference number."),
        #~ 'number': fields.char('Number', size=32, readonly=True,),
        #~ 'move_id':fields.many2one('account.move', 'Account Entry'),
        #~ 'move_ids': fields.related('move_id','line_id', type='one2many', relation='account.move.line', string='Journal Items', readonly=True),
        #~ 'audit': fields.related('move_id','to_check', type='boolean', relation='account.move', string='Audit Complete ?'),
        #~ 'pay_now':fields.selection([
            #~ ('pay_now','Pay Directly'),
            #~ ('pay_later','Pay Later or Group Funds'),
        #~ ],'Payment', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'tax_id':fields.many2one('account.tax', 'Tax', readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'pre_line':fields.boolean('Previous Payments ?', required=False),
        #~ 'date_due': fields.date('Due Date', readonly=True, select=True, states={'draft':[('readonly',False)]}),
        #~ 'payment_option':fields.selection([
                                           #~ ('without_writeoff', 'Keep Open'),
                                           #~ ('with_writeoff', 'Reconcile with Write-Off'),
                                           #~ ], 'Payment Difference', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        #~ 'writeoff_acc_id': fields.many2one('account.account', 'Write-Off account', readonly=True, states={'draft': [('readonly', False)]}),
        #~ 'comment': fields.char('Write-Off Comment', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        #~ 'analytic_id': fields.many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]}),
        #~ 'writeoff_amount': fields.function(_get_writeoff_amount, method=True, string='Write-Off Amount', type='float', readonly=True),
    #~ }
    #~ _defaults = {
        #~ 'period_id': _get_period,
        #~ 'journal_id':_get_journal,
        #~ 'currency_id': _get_currency,
        #~ 'reference': _get_reference,
        #~ 'narration':_get_narration,
        #~ 'amount': _get_amount,
        #~ 'type':_get_type,
        #~ 'state': 'draft',
        #~ 'pay_now': 'pay_later',
        #~ 'name': '',
        #~ 'date': lambda *a: time.strftime('%Y-%m-%d'),
        #~ 'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=c),
        #~ 'tax_id': _get_tax,
        #~ 'payment_option': 'without_writeoff',
        #~ 'comment': _('Write-Off'),
    #~ }
#~ 
#~ account_voucher()






