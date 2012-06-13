#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Javier Duran <javier@vauxoo.com>          
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
from tools import config
from tools.translate import _
import decimal_precision as dp


class account_wh_munici(osv.osv):
    

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'mun_sale', 'in_invoice': 'mun_purchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'mun_purchase'))], limit=1)
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

    _name = "account.wh.munici"
    _description = "Local Withholding"
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
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', readonly=True, help="Estado del Comprobante"),
        'date_ret': fields.date('Withholding date', readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the current date"),
        'date': fields.date('Date', readonly=True, states={'draft':[('readonly',False)]}, help="Date"),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the period of the validation(Withholding date) date."),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The pay account used for this withholding."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Withholding customer/supplier"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal entry"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'munici_line_ids': fields.one2many('account.wh.munici.line', 'retention_id', 'Local withholding lines', readonly=True, states={'draft':[('readonly',False)]}, help="Invoices to will be made local withholdings"),
        'amount': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withheld"),
        'move_id':fields.many2one('account.move', 'Account Entry'),


    } 
    _defaults = {
        'type': _get_type,
        'state': lambda *a: 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,

    }

    _sql_constraints = [
      ('ret_num_uniq', 'unique (number)', 'number must be unique !')
    ] 

    def action_confirm(self, cr, uid, ids, context={}):
        obj=self.pool.get('account.wh.munici').browse(cr,uid,ids)
        total=0
        for i in obj[0].munici_line_ids:
            if i.amount >= i.invoice_id.check_total*0.15:
                raise osv.except_osv(_('Invalid action !'), _("The line containing the document '%s' looks as if the amount withheld was wrong please check.!") % (i.invoice_id.reference))
            total+=i.amount
        self.write(cr,uid,ids,{'amount':total})
        return True


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_wh_munici ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.muni.%s' % obj_ret.type)
                cr.execute('UPDATE account_wh_munici SET number=%s ' \
                        'WHERE id=%s', (number, id))


        return True


    def action_done(self, cr, uid, ids, context={}):
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids)
        return True


    def action_move_create(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        if context is None: context = {}
        context.update({'muni_wh':True})
        for ret in self.browse(cr, uid, ids):
            for line in ret.munici_line_ids:
                if line.move_id or line.invoice_id.wh_local:
                    raise osv.except_osv(_('Invoice already withhold !'),_("You must omit the follow invoice '%s' !") % (line.invoice_id.name,))
                    return False

            acc_id = ret.partner_id.property_wh_munici_payable.id
            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})

            period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                else:
                    raise osv.except_osv(_('Warning !'), _("No se encontro un periodo fiscal para esta fecha: '%s' por favor verificar.!") % (ret.date_ret or time.strftime('%Y-%m-%d')))
            if ret.munici_line_ids:
                for line in ret.munici_line_ids:
                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount
                    name = 'COMP. RET. MUN ' + ret.number
                    ret_move = inv_obj.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, ret.date_ret, name,line,context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'munici_line_ids':lines, 'period_id':period_id})
                    inv_obj.write(cr, uid, [line.invoice_id.id], {'wh_muni_id':ret.id})
        return True


    def onchange_partner_id(self, cr, uid, ids, type, partner_id):
        acc_id = False
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_wh_munici_receivable.id
            else:
                acc_id = p.property_wh_munici_payable.id

        self._update_check(cr, uid, ids, partner_id)
        result = {'value': {
            'account_id': acc_id}
        }

        return result


    def _update_check(self, cr, uid, ids, partner_id, context={}):
        if ids:
            ret = self.browse(cr, uid, ids[0])
            inv_str = ''
            for line in ret.munici_line_ids:
                if line.invoice_id.partner_id.id != partner_id:
                    inv_str+= '%s'% '\n'+line.invoice_id.name

            if inv_str:
                raise osv.except_osv('Incorrect Invoices !',"The following invoices are not the selected partner: %s " % (inv_str,))

        return True

    def _new_check(self, cr, uid, values, context={}):
        lst_inv = []

        if 'munici_line_ids' in values and values['munici_line_ids']:
            if 'partner_id' in values and values['partner_id']:
                for l in values['munici_line_ids']:
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

        return super(account_wh_munici, self).write(cr, uid, ids, vals, context=context)


    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        if check:
            self._new_check(cr, uid, vals, context)

        return super(account_wh_munici, self).create(cr, uid, vals, context)

account_wh_munici()



class account_wh_munici_line(osv.osv):

    def default_get(self, cr, uid, fields, context={}):
        data = super(account_wh_munici_line, self).default_get(cr, uid, fields, context)
        self.munici_context = context
        return data
#TODO
#necesito crear el campo y tener la forma de calcular el monto del impuesto
#munici retenido en la factura


    _name = "account.wh.munici.line"
    _description = "Local Withholding Line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Local Withholding line Description"),
        'retention_id': fields.many2one('account.wh.munici', 'Local withholding', ondelete='cascade', help="Local withholding"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='set null', help="Withholding invoice"),
        'amount':fields.float('Amount', digits_compute= dp.get_precision('Withhold')),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account Entry"),
        'wh_loc_rate':fields.float('Rate', help="Local withholding rate"),
        'concepto_id': fields.integer('Concept', size=3, help="Local withholding concept"),


    }
    _defaults = {
        'concepto_id': lambda *a: 1,
        
    }
    _sql_constraints = [
        ('munici_fact_uniq', 'unique (invoice_id)', 'The invoice has already assigned in local withholding, you cannot assigned it twice!')
    ] 


    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context={}):
        lines = []

        if  hasattr(self, 'munici_context') and ('lines' in self.munici_context):
            lines = [x[2] for x in self.munici_context['lines']]
        if not invoice_id:
            return {'value':{'amount':0.0}}
        else:
            ok = True
            res = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context)
            cr.execute('select retention_id from account_wh_munici_line where invoice_id=%s', (invoice_id,))
            ret_ids = cr.fetchone()
            ok = ok and bool(ret_ids)
            if ok:
                ret = self.pool.get('account.wh.munici').browse(cr, uid, ret_ids[0], context)
                raise osv.except_osv('Assigned Invoice !',"The invoice has already assigned in local withholding code: '%s' !" % (ret.code,))
            
            total = res.amount_total
            return {'value' : {'amount':total}} 


account_wh_munici_line()
