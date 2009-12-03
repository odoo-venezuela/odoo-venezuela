# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
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


class account_retention(osv.osv):
    def _amount_ret_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for retention in self.browse(cr, uid, ids, context):
            res[retention.id] = {
                'amount_base_ret': 0.0,
                'total_tax_ret': 0.0
            }
            for line in retention.retention_line:
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

    _name = "account.retention"
    _description = "Comprobante de Retencion"
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
        'retention_line': fields.one2many('account.retention.line', 'retention_id', 'Lineas de Retencion', readonly=True, states={'draft':[('readonly',False)]}, help="Facturas a la cual se realizarán las retenciones"),
        'amount_base_ret': fields.function(_amount_ret_all, method=True, digits=(16,4), string='Total Base Ret.', multi='all', help="Total de la base retenida"),
        'total_tax_ret': fields.function(_amount_ret_all, method=True, digits=(16,4), string='Total Imp. Ret.', multi='all', help="Total del impuesto Retenido"),


    } 
    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('account.retention').retencion_seq_get(cr, uid, context),
        'type': _get_type,
        'state': lambda *a: 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,

    }

    _sql_constraints = [
      ('ret_num_uniq', 'unique (code)', 'The Code must be unique !')
    ] 


    def retencion_seq_get(self, cr, uid, context=None):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='account.retention' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False


    def retencion_compra_seq_get(self, cr, uid, context=None):
        if context is None:
            context={}

        tipo = context.get('type', 'in_invoice')
        pool_seq=self.pool.get('ir.sequence')
        cr.execute(("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='account.retention.%s' and active=True") % (tipo, ))
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False


    def create(self, cr, uid, vals, context=None):
        code = self.pool.get('ir.sequence').get(cr, uid, 'account.retention')
        vals['code'] = code
        return super(account_retention,self).create(cr, uid, vals, context)



    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_retention ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.retention.%s' % obj_ret.type)
                cr.execute('UPDATE account_retention SET number=%s ' \
                        'WHERE id=%s', (number, id))


        return True


    

    def action_move_create(self, cr, uid, ids, *args):
        inv_obj = self.pool.get('account.invoice')
        context = {}

        for ret in self.browse(cr, uid, ids):
            for line in ret.retention_line:
                if line.move_id or line.invoice_id.retention:
                    raise osv.except_osv(_('Factura Ya Retenida !'),_("Debe Omitir la siguiente factura '%s' !") % (line.invoice_id.name,))
                    return False

            acc_id = ret.account_id.id
            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})

            period_id = ret.period_id and ret.period_id.id or False
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]

            if ret.retention_line:
                for line in ret.retention_line:
                    journal_id = line.invoice_id.journal_id.id
                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount_tax_ret
                    ret_move = self.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'retention_line':lines, 'period_id':period_id})
                    inv_obj.write(cr, uid, line.invoice_id.id, {'retention':True}, context=context)
    

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
                acc_id = p.property_retention_receivable.id
            else:
                acc_id = p.property_retention_payable.id


        result = {'value': {
            'account_id': acc_id}
        }

        return result


account_retention()



class account_retention_line(osv.osv):
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

    def _retention_rate(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ret_line in self.browse(cr, uid, ids, context=context):
            if ret_line.invoice_id:
                res[ret_line.id] = ret_line.invoice_id.p_ret
            else:
                res[ret_line.id] = 0.0
        return res


    _name = "account.retention.line"
    _description = "Linea de Retencion"
    _columns = {
        'name': fields.char('Descripcion', size=64, required=True, help="Descripcion de la linea del comprobante"),
        'retention_id': fields.many2one('account.retention', 'Comprobante', ondelete='cascade', select=True, help="Comprobante"),
        'invoice_id': fields.many2one('account.invoice', 'Factura', required=True, ondelete='set null', select=True, help="Factura a retener"),
        'tax_line': fields.function(_compute_tax_lines, method=True, relation='account.invoice.tax', type="one2many", string='Impuestos', help="Impuestos de la factura"),
        'amount_tax_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Monto Retenido', multi='all', help="Total impuesto retenido de la factura"),
        'base_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Base Retenida', multi='all', help="Base retenida de la factura"),
        'retention_rate': fields.function(_retention_rate, method=True, string='Retencion Por 100', type='float', help="Porcentaje de Retencion ha aplicar a la factura"),
        'move_id': fields.many2one('account.move', 'Movimiento Contable', readonly=True, help="Asiento Contable"),


    }



    def invoice_id_change(self, cr, uid, ids, invoice, context=None):
        if context is None:
            context = {}
        if not invoice:
            return {}
        result = {}
        lst=[]
        res = self.pool.get('account.invoice').browse(cr, uid, invoice, context=context)
#        for tax in res.tax_line:
#            lst.append({'tax_amount': tax.tax_amount, 'name': tax.name, 'base_amount': tax.base_amount, 'amount': #tax.amount, 'base': tax.base, 'id': tax.id})
#            lst.append(tax.id)
#        result['tax_line'] = lst
#        print 'resultadooooo: ',result
        result['name'] = res.name

        domain = {}
        return {'value':result, 'domain':domain}

account_retention_line()
