# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
import time
from tools import config


class account_retencion_islr(osv.osv):

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale', 'in_refund': 'purchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'purchase'))], limit=1)
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

    _name = "account.retencion.islr"
    _description = "Comprobante de Retencion de ISLR"
    _columns = {
        'name': fields.char('Descripcion', size=64, select=True,readonly=True, states={'draft':[('readonly',False)]}, help="Descripcion del Comprobante"),
        'code': fields.char('Codigo', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Referencia del Comprobante"),
        'number': fields.char('Numero de Retencion', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Nro. del Comprobante"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Tipo', readonly=True, select=True, help="Tipo del Comprobante"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', select=True, readonly=True, help="Estado del Comprobante"),
        'date_ret': fields.date('Fecha Comprobante', readonly=True, help="Mantener en blanco para usar la fecha actual"),
        'date': fields.date('Fecha', readonly=True, states={'draft':[('readonly',False)]}, help="Fecha de emision"),
        'period_id': fields.many2one('account.period', 'Periodo', domain=[('state','<>','done')], readonly=True, help="Mantener en blanco para usar el periodo fiscal correspondiente a la fecha del comprobante"),
        'account_id': fields.many2one('account.account', 'Cuenta', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Cuenta donde se cargaran los montos retenidos del I.V.A."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Proveedor o Cliente al cual se retiene o te retiene"),
        'currency_id': fields.many2one('res.currency', 'Moneda', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Moneda enla cual se realiza la operacion"),
        'journal_id': fields.many2one('account.journal', 'Diario', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Diario donde se registran los asientos"),
        'company_id': fields.many2one('res.company', 'Compania', required=True, help="Compania"),
        'islr_line_ids': fields.one2many('account.retencion.islr.line', 'retention_id', 'Lineas de Retencion', readonly=True, states={'draft':[('readonly',False)]}, help="Facturas a la cual se realizarán las retenciones"),
        'amount':fields.float('Amount', readonly=True),
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

    ] 



    def action_confirm(self, cr, uid, ids, context={}):
        obj=self.pool.get('account.retencion.islr').browse(cr,uid,ids)
        total=0
        for i in obj[0].islr_line_ids:
            total+=i.amount
        self.write(cr,uid,ids,{'amount':total})
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_retencion_islr ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.retencion_islr.%s' % obj_ret.type)
                cr.execute('UPDATE account_retencion_islr SET number=%s ' \
                        'WHERE id=%s', (number, id))


        return True


    def action_done(self, cr, uid, ids, context={}):
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids)
        self.write(cr, uid, ids, {'state':'done'})
        return True


    def action_move_create(self, cr, uid, ids, *args):
        inv_obj = self.pool.get('account.invoice')
        context = {}

        for ret in self.browse(cr, uid, ids):

            acc_id = ret.account_id.id
            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})

            period_id = ret.period_id and ret.period_id.id or False
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]

            if ret.islr_line_ids:
                for line in ret.islr_line_ids:
                    journal_id = line.invoice_id.journal_id.id
                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount
                    ret_move = self.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'islr_line_ids':lines, 'period_id':period_id})
#                    inv_obj.write(cr, uid, line.invoice_id.id, {'retention':True}, context=context)
    

        return True



    def ret_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context=None, name=''):
        inv_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        assert len(ids)==1, "Can only pay one invoice at a time"
        invoice = inv_obj.browse(cr, uid, ids[0])
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
        #take the choosen date
        if 'date_p' in context and context['date_p']:
            date=context['date_p']
        else:
            date=time.strftime('%Y-%m-%d')
        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
        }

        if not name:
            name = invoice.invoice_line and invoice.invoice_line[0].name or invoice.number
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
        if (not round(total,int(config['price_accuracy']))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return {'move_id': move_id}


    def onchange_partner_id(self, cr, uid, ids, type, partner_id):
        acc_id = False        
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_retencion_islr_receivable.id
            else:
                acc_id = p.property_retencion_islr_payable.id


        result = {'value': {
            'account_id': acc_id}
        }

        return result


account_retencion_islr()



class account_retencion_islr_line(osv.osv):

    def default_get(self, cr, uid, fields, context={}):
        data = super(account_retencion_islr_line, self).default_get(cr, uid, fields, context)
        self.islr_context = context
        return data
#TODO
#necesito crear el campo y tener la forma de calcular el monto del impuesto
#islr retenido en la factura


    _name = "account.retencion.islr.line"
    _description = "Linea de Retencion"
    _columns = {
        'name': fields.char('Descripcion', size=64, required=True, help="Descripcion de la linea del comprobante"),
        'retention_id': fields.many2one('account.retencion.islr', 'Comprobante', ondelete='cascade', select=True, help="Comprobante"),
        'invoice_id': fields.many2one('account.invoice', 'Factura', required=True, ondelete='set null', select=True, help="Factura a retener"),
        'amount':fields.float('Amount'),
        'move_id': fields.many2one('account.move', 'Movimiento Contable', readonly=True, help="Asiento Contable"),
#        'retencion_islr':fields.float('Retencion por 100'),
#        'monto_fijo':fields.float('Adedum'),


    }

    _sql_constraints = [
        ('islr_fact_uniq', 'unique (invoice_id)', 'La factura debe ser unica !')
    ] 


    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context={}):
        lines = []

        if  hasattr(self, 'islr_context') and ('lines' in self.islr_context):
            lines = [x[2] for x in self.islr_context['lines']]
        if not invoice_id:
            return {'value':{'amount':0.0}}
        else:
            invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context)
            total = invoice_obj.amount_total
            return {'value' : {'amount':total}} 


account_retencion_islr_line()
