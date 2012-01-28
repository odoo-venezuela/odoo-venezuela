#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>     
#    Planified by: Humberto Arocha / Nhomar Hernandez
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


class account_wh_src(osv.osv):

    _name = "account.wh.src"
    _description = "Social Responsibility Commitment Withholding"
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly',False)]}, required=True, help="Description of withholding"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Withholding reference"),
        'number': fields.char('Number', size=32, states={'draft':[('readonly',False)]}, help="Withholding number"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ],'Type', readonly=False, help="Withholding type"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'Estado', readonly=True, help="Estado del Comprobante"),
        'date_ret': fields.date('Withholding date', readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the current date"),
        'date': fields.date('Date', readonly=True, states={'draft':[('readonly',False)]}, help="Date"),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','!=','done')], readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the period of the validation(Withholding date) date."),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The pay account used for this withholding."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Withholding customer/supplier"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal entry"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'line_ids': fields.one2many('account.wh.src.line', 'wh_id', 'Local withholding lines', readonly=True, states={'draft':[('readonly',False)]}, help="Facturas a la cual se realizarán las retenciones"),
        'wh_amount': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withheld"),
        'move_id':fields.many2one('account.move', 'Account Entry'),


    } 
    
    def _diario(self, cr, uid, model, context=None):
        if context is None:
            context={}
        ir_model_data = self.pool.get('ir.model.data')
        journal_purchase=ir_model_data.search(cr, uid, [('model','=','account.journal'),('module','=','l10n_ve_withholding_src'),('name','=','withholding_scr_purchase_journal')])
        journal_sale=ir_model_data.search(cr, uid, [('model','=','account.journal'),('module','=','l10n_ve_withholding_src'),('name','=','withholding_src_sale_journal')])
        ir_model_purchase_brw=ir_model_data.browse(cr, uid, journal_purchase, context=context)
        ir_model_sale_brw=ir_model_data.browse(cr, uid, journal_sale, context=context)
        print 'ir_model_purchase_brw %s' %ir_model_purchase_brw
        print 'ir_model_sale_brw %s' %ir_model_sale_brw
        if context.get('type') == 'in_invoice':
            return ir_model_purchase_brw[0].res_id
        else:
            return ir_model_sale_brw[0].res_id


    _defaults = {
    'state': lambda *a: 'draft',
    'currency_id': lambda self, cr, uid, context: \
        self.pool.get('res.company').browse(cr, uid, uid,
        context=context).currency_id.id,
    'journal_id':lambda self, cr, uid, context: \
        self._diario(cr, uid, uid, context),
    'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,

    }

    _sql_constraints = [

    ] 
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,context=None):
        if context is None: context = {}    
        acc_id = False
        res = {}
        inv_obj = self.pool.get('account.invoice')
        
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable and p.property_account_receivable.id or False
            else:
                acc_id = p.property_account_payable and p.property_account_payable.id or False
        res = {'value': {
            'account_id': acc_id,
            }
        }

        return res
        

    def action_date_ret(self,cr,uid,ids,context=None):
        for wh in self.browse(cr, uid, ids, context):
            wh.date_ret or self.write(cr, uid, [wh.id], {'date_ret':time.strftime('%Y-%m-%d')})
        return True

    def action_confirm(self, cr, uid, ids, context={}):
        return True
        
    def action_done(self, cr, uid, ids, context={}):
        return True

    def action_cancel(self,cr,uid,ids,context={}):
        return True
        
    def copy(self,cr,uid,id,default,context=None):
        raise osv.except_osv('Procedimiento invalido!',"No puede duplicar lineas")
        return True
        
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv('Procedimiento invalido!',"No puede eliminar lineas")
        return True



    def action_move_create(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        if context is None: context = {}
        
        context.update({'src_wh':True})
        
        ret = self.browse(cr, uid, ids[0], context)
        #~ TO_CHECK
        #~ VALIDACION PARA VERIFICAR SI LA FACTURA YA ESTA RETENIDA
        #~ for line in ret.line_ids:
            #~ if line.move_id or line.invoice_id.wh_iva:
                #~ raise osv.except_osv(_('Invoice already withhold !'),\
                #~ _("You must omit the follow invoice '%s' !") %\
                #~ (line.invoice_id.name,))

        acc_id = ret.account_id.id

        period_id = ret.period_id and ret.period_id.id or False
        journal_id = ret.journal_id.id
        if not period_id:
            per_obj = self.pool.get('account.period')
            period_id = per_obj.find(cr, uid,ret.date_ret or time.strftime('%Y-%m-%d'))
            period_id = per_obj.search(cr,uid,[('id','in',period_id),('special','=',False)])
            if not period_id:
                raise osv.except_osv(_('Missing Periods!'),\
                _("There are not Periods created for the pointed day: %s!") %\
                (ret.date_ret or time.strftime('%Y-%m-%d')))
            period_id = period_id[0]
        if period_id:
            if ret.line_ids:
                for line in ret.line_ids:
                    writeoff_account_id,writeoff_journal_id = False, False
                    amount = line.wh_amount
                    if line.invoice_id.type in ['in_invoice','in_refund']:
                        name = 'COMP. RET. CRS ' + ret.number + ' Doc. '+ (line.invoice_id.reference or '')
                    else:
                        name = 'COMP. RET. CRS ' + ret.number + ' Doc. '+ (line.invoice_id.number or '')
                    ret_move = inv_obj.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, ret.date_ret, name,[line], context)
                    # make the withholding line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'line_ids':lines, 'period_id':period_id})

                    if rl and line.invoice_id.type in ['out_invoice','out_refund']:
                        inv_obj.write(cr,uid,[line.invoice_id.id],{'wh_iva_id':ret.id})
            else:
                return False
        return True

    def action_number(self, cr, uid, ids, *args):
        print "entreeeee"
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_wh_src ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.src.%s' % obj_ret.type)
                cr.execute('UPDATE account_wh_src SET number=%s ' \
                        'WHERE id=%s', (number, id))
        return True
account_wh_src()

class account_wh_src_line(osv.osv):

    _name = "account.wh.src.line"
    _description = "Social Responsibility Commitment Withholding Line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Local Withholding line Description"),
        'wh_id': fields.many2one('account.wh.src', 'Local withholding', ondelete='cascade', help="Local withholding"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='set null', help="Withholding invoice"),
        'base_amount':fields.float('Base Amount', digits_compute= dp.get_precision('Base Amount to be Withheld')),
        'wh_amount':fields.float('Withheld Amount', digits_compute= dp.get_precision('Withhold')),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account Entry"),
        'wh_src_rate':fields.float('Withholding Rate', help="Withholding rate"),
    }
    _defaults = {

    }
    _sql_constraints = [

    ] 
    
    def onchange_invoice_id(self, cr, uid, ids, type, invoice_id,context=None):
        if context is None: context = {}    
        res = {}
        inv_obj = self.pool.get('account.invoice')
        
        if invoice_id:
            p = inv_obj.browse(cr, uid, invoice_id).amount_untaxed
        res = {'value': {
            'base_amount': p,
            }
        }

        return res
        
account_wh_src_line()
