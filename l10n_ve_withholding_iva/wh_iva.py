#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
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

from osv import osv, fields
import time
from tools.translate import _
import decimal_precision as dp


class account_wh_iva(osv.osv):
    def _amount_ret_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for retention in self.browse(cr, uid, ids, context):
            res[retention.id] = {
                'amount_base_ret': 0.0,
                'total_tax_ret': 0.0
            }
            #cambiar por los campos no calculados
            for line in retention.wh_lines:
                res[retention.id]['total_tax_ret'] += line.amount_tax_ret
                res[retention.id]['amount_base_ret'] += line.base_ret

        return res
        
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'iva_sale', 'in_invoice': 'iva_purchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'iva_purchase'))], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_currency(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]
    
    _name = "account.wh.iva"
    _description = "Withholding Vat"
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly',False)]}, required=True, help="Description of withholding"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Withholding reference"),
        'number': fields.char('Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Withholding number"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ],'Type', readonly=True, help="Withholding type"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'State', readonly=True, help="Withholding State"),
        'date_ret': fields.date('Accounting date', readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the current date"),
        'date': fields.date('Voucher Date', readonly=True, states={'draft':[('readonly',False)]}, help="Date"),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the period of the validation(Withholding date) date."),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The pay account used for this withholding."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Withholding customer/supplier"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal entry"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'wh_lines': fields.one2many('account.wh.iva.line', 'retention_id', 'Withholding vat lines', readonly=True, states={'draft':[('readonly',False)]}, help="Withholding vat lines"),
        'tot_amount_base_wh': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount without tax"),
        'tot_amount_tax_wh': fields.float('Amount wh. tax vat', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withholding tax vat"),
        'amount_base_ret': fields.function(_amount_ret_all, method=True, digits_compute= dp.get_precision('Withhold'), string='Compute amount', multi='all', help="Compute amount without tax"),
        'total_tax_ret': fields.function(_amount_ret_all, method=True, digits_compute= dp.get_precision('Withhold'), string='Compute amount wh. tax vat', multi='all', help="compute amount withholding tax vat"),
        
    } 
    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('account.wh.iva').wh_iva_seq_get(cr, uid, context),
        'type': _get_type,
        'state': lambda *a: 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,

    }

    def _check_partner(self, cr, uid, ids, context={}):
        agt = False
        obj = self.browse(cr, uid, ids[0])
        if obj.type in ('out_invoice', 'out_refund') and obj.partner_id.wh_iva_agent:
            agt = True
        if obj.type in ('in_invoice', 'in_refund') and obj.company_id.partner_id.wh_iva_agent:
            agt = True
        return agt

    _constraints = [
        (_check_partner, 'Error ! The partner must be withholding vat agent .', ['partner_id']),
    ]

    _sql_constraints = [
      ('ret_num_uniq', 'unique (number)', 'number must be unique !')
    ] 


    def wh_iva_seq_get(self, cr, uid, context=None):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='account.wh.iva' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_wh_iva ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.iva.%s' % obj_ret.type)
                cr.execute('UPDATE account_wh_iva SET number=%s ' \
                        'WHERE id=%s', (number, id))
        return True
    
    def action_date_ret(self,cr,uid,ids,context=None):
        for wh in self.browse(cr, uid, ids, context):
            wh.date_ret or self.write(cr, uid, [wh.id], {'date_ret':time.strftime('%Y-%m-%d')})
        return True


    def action_move_create(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        if context is None: context = {}

        for ret in self.browse(cr, uid, ids, context):
            for line in ret.wh_lines:
                if line.move_id or line.invoice_id.wh_iva:
                    raise osv.except_osv(_('Invoice already withhold !'),\
                    _("You must omit the follow invoice '%s' !") %\
                    (line.invoice_id.name,))
                    return False

            acc_id = ret.account_id.id

            period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
            if ret.wh_lines:
                for line in ret.wh_lines:
                    writeoff_account_id,writeoff_journal_id = False, False
                    amount = line.amount_tax_ret
                    if line.invoice_id.type in ['in_invoice','in_refund']:
                        name = 'COMP. RET. IVA ' + ret.number + ' Doc. '+ (line.invoice_id.reference or '')
                    else:
                        name = 'COMP. RET. IVA ' + ret.number + ' Doc. '+ (str(int(line.invoice_id.number)) or '')
                    
                    context.update({'vat_wh':True})
                    ret_move = inv_obj.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, ret.date_ret, name,line.tax_line, context)
                    # make the withholding line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'wh_lines':lines, 'period_id':period_id})
        return True


    def onchange_partner_id(self, cr, uid, ids, type, partner_id):
        acc_id = False
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
            else:
                acc_id = p.property_account_payable.id

        self._update_check(cr, uid, ids, partner_id)
        result = {'value': {
            'account_id': acc_id}
        }

        return result

    def _update_check(self, cr, uid, ids, partner_id, context={}):
        if ids:
            ret = self.browse(cr, uid, ids[0])
            inv_str = ''
            for line in ret.wh_lines:
                if line.invoice_id.partner_id.id != partner_id:
                    inv_str+= line.invoice_id.name and '%s'% '\n'+line.invoice_id.name or ''

            if inv_str:
                raise osv.except_osv('Incorrect Invoices !',"The following invoices are not the selected partner: %s " % (inv_str,))

        return True

    def _new_check(self, cr, uid, values, context={}):
        lst_inv = []

        if 'wh_lines' in values and values['wh_lines']:
            if 'partner_id' in values and values['partner_id']:
                for l in values['wh_lines']:
                    if 'invoice_id' in l[2] and l[2]['invoice_id']:
                        lst_inv.append(l[2]['invoice_id'])

        if lst_inv:
            invoices = self.pool.get('account.invoice').browse(cr, uid, lst_inv)
            inv_str = ''
            for inv in invoices:
                if inv.partner_id.id != values['partner_id']:
                    inv_str+= '%s'% '\n'+inv.name        

            if inv_str:
                raise osv.except_osv('Incorrect Invoices !',"The following invoices are not the selected partner: %s " % (inv_str,))

        return True


    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if not context:
            context={}
        ret = self.browse(cr, uid, ids[0])
        if update_check:
            if 'partner_id' in vals and vals['partner_id']:
                self._update_check(cr, uid, ids, vals['partner_id'], context)
            else:
                self._update_check(cr, uid, ids, ret.partner_id.id, context)

        return super(account_wh_iva, self).write(cr, uid, ids, vals, context=context)


    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        if check:
            self._new_check(cr, uid, vals, context)
            
        code = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.iva')
        vals['code'] = code
        return super(account_wh_iva, self).create(cr, uid, vals, context)


    def compute_amount_wh(self, cr, uid, ids, context=None):
        res = {}
        if context is None:
            context = {}        
        for retention in self.browse(cr, uid, ids, context):
            res[retention.id] = {
                'tot_amount_base_wh': 0.0,
                'tot_amount_tax_wh': 0.0
            }            
            for line in retention.wh_lines:
                res[retention.id]['tot_amount_base_wh'] += line.amount_base_wh
                res[retention.id]['tot_amount_tax_wh'] += line.amount_tax_wh
        self.write(cr, uid, [retention.id], res[retention.id])        
        return True
    
account_wh_iva()



class account_wh_iva_line(osv.osv):
    def _compute_tax_lines(self, cr, uid, ids, name, args, context=None):
        result = {}
        for ret_line in self.browse(cr, uid, ids, context):
            lines = []
            if ret_line.invoice_id:
                ids_tline = ret_line.invoice_id.tax_line
                lines = map(lambda x: x.id, ids_tline)
            result[ret_line.id] = lines
        return result

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ret_line in self.browse(cr, uid, ids, context):
            res[ret_line.id] = {
                'amount_tax_ret': 0.0,
                'base_ret': 0.0
            }
            for line in ret_line.invoice_id.tax_line:
                res[ret_line.id]['amount_tax_ret'] += line.amount_ret
                res[ret_line.id]['base_ret'] += line.base_ret

        return res

    def check_a_retention(self, cr, uid, ids, context=None):
        amount = 0.0
        for tax_line in self.browse(cr,uid, ids[0]).tax_line:
            amount+= tax_line.amount
        wh_vat_line=self.browse(cr, uid, ids, context)[0]
        if wh_vat_line.amount_base_wh > amount:
            raise osv.except_osv(_('Amount Error'),_('the amount is greater than the tax'))
        return True


    _name = "account.wh.iva.line"
    _description = "Withholding vat line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Withholding line Description"),
        'retention_id': fields.many2one('account.wh.iva', 'Withholding vat', ondelete='cascade', help="Withholding vat"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='set null', help="Withholding invoice"),
        'tax_line': fields.function(_compute_tax_lines, method=True, relation='account.invoice.tax', type="one2many", string='Taxes', help="Invoice taxes"),
        'amount_tax_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Wh. tax amount', multi='all', help="Withholding tax amount"),
        'base_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Wh. amount', multi='all', help="Withholding without tax amount"),
#        'retention_rate': fields.function(_retention_rate, method=True, string='Wh. rate', type='float', help="Withholding rate"),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account entry"),
        'amount_base_wh': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount without tax"),        
        'amount_tax_wh': fields.float('Amount wh. tax vat', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withholding tax vat"),        

    }

    _sql_constraints = [
      ('ret_fact_uniq', 'unique (invoice_id)', 'The invoice has already assigned in withholding vat, you cannot assigned it twice!')
    ] 

    def invoice_id_change(self, cr, uid, ids, invoice, context=None):
        if context is None:
            context = {}
        if not invoice:
            return {}
        result = {}
        lst=[]
        domain = {}
        ok = True
        res = self.pool.get('account.invoice').browse(cr, uid, invoice, context=context)
        cr.execute('select retention_id from account_wh_iva_line where invoice_id=%s', (invoice,))
        ret_ids = cr.fetchone()
        ok = ok and bool(ret_ids)
        if ok:
            ret = self.pool.get('account.wh.iva').browse(cr, uid, ret_ids[0], context)
            raise osv.except_osv('Assigned Invoice !',"The invoice has already assigned in withholding vat code: '%s' !" % (ret.code,))

        result['name'] = res.name


        return {'value':result, 'domain':domain}

account_wh_iva_line()
