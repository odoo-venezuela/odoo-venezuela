# -*- coding: utf-8 -*-
##############################################################################
#
#    
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

import time
from osv import fields, osv
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
        'wh_iva': fields.function(_retenida, method=True, string='Withhold', type='boolean',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, None, 50),
                'account.move.line': (_get_inv_from_line, None, 50),
                'account.move.reconcile': (_get_inv_from_reconcile, None, 50),
            }, help="The account moves of the invoice have been retention with account moves of the payment(s)."),    
        'wh_iva_rate': fields.float('Wh rate', digits_compute= dp.get_precision('Withhold'), readonly=True, states={'draft':[('readonly',False)]}, help="Withholding vat rate"),
        'wh_iva_id': fields.many2one('account.wh.iva', 'Wh. Vat', readonly=True, help="Withholding vat."),        
    }


    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
            date_invoice=False, payment_term=False, partner_bank_id=False):

        data = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
            date_invoice, payment_term, partner_bank_id)
        if partner_id:
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            data[data.keys()[0]]['wh_iva_rate'] =  part.wh_iva_rate
        return data


    def create(self, cr, uid, vals, context={}):
        partner_id = vals.get('partner_id',False)
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid,partner_id)
            vals['wh_iva_rate'] = partner.wh_iva_rate
        return super(account_invoice, self).create(cr, uid, vals, context)
    
    
    def test_retenida(self, cr, uid, ids, *args):     
        type2journal = {'out_invoice': 'iva_sale', 'in_invoice': 'iva_purchase', 'out_refund': 'iva_sale', 'in_refund': 'iva_purchase'}
        type_inv = self.browse(cr, uid, ids[0]).type
        type_journal = type2journal.get(type_inv, 'iva_purchase')      
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


    def ret_payment_get(self, cr, uid, ids, *args):
        for invoice in self.browse(cr, uid, ids):
            moves = self.move_line_id_payment_get(cr, uid, [invoice.id])
            src = []
            lines = []
            for m in self.pool.get('account.move.line').browse(cr, uid, moves):
                temp_lines = []#Added temp list to avoid duplicate records
                if m.reconcile_id:
                    temp_lines = map(lambda x: x.id, m.reconcile_id.line_id)
                elif m.reconcile_partial_id:
                    temp_lines = map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
                lines += [x for x in temp_lines if x not in lines]
                src.append(m.id)
                
            lines = filter(lambda x: x not in src, lines)

        return lines


    def wh_iva_line_create(self, cr, uid, inv):
        return (0, False, {
            'name': inv.name or inv.number,
            'invoice_id': inv.id,
        })
    

    def action_wh_iva_create(self, cr, uid, ids, *args):
        wh_iva_obj = self.pool.get('account.wh.iva')        
        for inv in self.browse(cr, uid, ids):
            if inv.wh_iva_id:
                raise osv.except_osv('Invalid Action !', 'Withhold Invoice !')
            ret_line = []
            if inv.type in ('out_invoice', 'out_refund'):
                acc_id = inv.partner_id.property_wh_iva_receivable.id
                wh_type = 'out_invoice'
            else:
                acc_id = inv.partner_id.property_wh_iva_payable.id
                wh_type = 'in_invoice'
            
            ret_line.append(self.wh_iva_line_create(cr, uid, inv))
            ret_iva = {
                'name':wh_iva_obj.wh_iva_seq_get(cr, uid),
                'type': wh_type,
                'account_id': acc_id,
                'partner_id': inv.partner_id.id,
                'retention_line':ret_line
            }
            ret_id = wh_iva_obj.create(cr, uid, ret_iva)
            self.write(cr, uid, [inv.id], {'wh_iva_id':ret_id})
        return True
    
            
    def button_reset_taxes_ret(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        ait_obj = self.pool.get('account.invoice.tax')
        for id in ids:
            amount_tax_ret = {}
            amount_tax_ret = ait_obj.compute_amount_ret(cr, uid, id, context)
            for ait_id in amount_tax_ret.keys():
                ait_obj.write(cr, uid, ait_id, amount_tax_ret[ait_id])

        return True



    def ret_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, date, name, context=None):
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        assert len(ids)==1, "Can only pay one invoice at a time"
        invoice = self.browse(cr, uid, ids[0])
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False,
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False,
        }

        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        move = {'ref': invoice.number, 'line_id': lines, 'journal_id': pay_journal_id, 'period_id': period_id, 'date': date}
        move_id = self.pool.get('account.move').create(cr, uid, move, context=context)

        self.pool.get('account.move').post(cr, uid, [move_id])

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute('select id from account_move_line where move_id in ('+str(move_id)+','+str(invoice.move_id.id)+')')
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()) )
        for l in lines+invoice.payment_ids:
            if l.account_id.id==src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)
        if (not round(total,self.pool.get('decimal.precision').precision_get(cr, uid, 'Withhold'))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return {'move_id': move_id}
    

    def button_reset_taxes(self, cr, uid, ids, context=None):
        super(account_invoice, self).button_reset_taxes(cr, uid, ids, context)
        self.button_reset_taxes_ret(cr, uid, ids, context)
        
        return True


    def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
        if not inv.tax_line:
            for tax in compute_taxes.values():
                ait_obj.create(cr, uid, tax)
        else:
            tax_key = []
            for tax in inv.tax_line:
                if tax.manual:
                    continue
#                key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id)
                #### group by tax id  ####
                key = (tax.tax_id.id)
                tax_key.append(key)
                if not key in compute_taxes:
                    raise osv.except_osv(_('Warning !'), _('Global taxes defined, but are not in invoice lines !'))
                base = compute_taxes[key]['base']
                if abs(base - tax.base) > inv.company_id.currency_id.rounding:
                    raise osv.except_osv(_('Warning !'), _('Tax base different !\nClick on compute to update tax base'))
            for key in compute_taxes:
                if not key in tax_key:
                    raise osv.except_osv(_('Warning !'), _('Taxes missing !'))    
account_invoice()




class account_invoice_tax(osv.osv):
    _inherit = 'account.invoice.tax'
    _columns = {
        'amount_ret': fields.float('Withholding amount', digits_compute= dp.get_precision('Withhold'), help="Withholding vat amount"),
        'base_ret': fields.float('Amount', digits_compute= dp.get_precision('Withhold'), help="Amount without tax"),    
        'tax_id': fields.many2one('account.tax', 'Tax', required=True, ondelete='set null', help="Tax"),        
    }
    
    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id)['taxes']:
                val={}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['quantity']
                ####  add tax id  ####
                val['tax_id'] = tax['id']                

                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id

#                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                #### group by tax id  ####
                key = (val['tax_id'])                
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped


    def compute_amount_ret(self, cr, uid, invoice_id, context={}):
        res = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context)
        
        for ait in inv.tax_line:
            amount_ret = 0.0
            if ait.tax_id.ret:
                amount_ret = inv.wh_iva_rate and ait.tax_amount*inv.wh_iva_rate/100.0 or 0.00
            res[ait.id] = {'amount_ret': amount_ret, 'base_ret': ait.base_amount}
        return res
        
account_invoice_tax()
