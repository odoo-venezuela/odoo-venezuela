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
        print "cr %s, uid %s, model %s, context=None %s "%(cr, uid, model, context)
        account_j=self.pool.get('account.journal')
        print "account_j %s" %account_j
        #~ TO_CHECK:
        #~ HAY QUE UTILIZAR EL ID DEL DIARIO CREADO EN EL DATA XML
        #~ Y BUSCARLO EN EL MODELO ir.model.data
        journal_id=account_j.search(cr, uid, [('name','=','DIARIO DE SRC PARA PROVEEDORES')])
        return journal_id[0]


    _defaults = {
    'state': lambda *a: 'draft',
    'type': lambda *a: 'in_invoice',
    'currency_id': lambda self, cr, uid, context: \
        self.pool.get('res.company').browse(cr, uid, uid,
        context=context).currency_id.id,
    'journal_id':lambda self, cr, uid, context: \
        self._diario(cr, uid, uid, context),
     #~ TO_CHECK:
     #~ HAY QUE COLOCAR EL DEFAULT PARA EL company_id
    }

    _sql_constraints = [

    ] 
    
    #~ def _withholdable_tax_(self, cr, uid, ids, context=None):
        #~ if context is None:
            #~ context={}
        #~ account_invo_obj = self.pool.get('account.invoice')
        #~ acc_id = [line.id for line in account_invo_obj.browse(cr, uid, ids, context=context) if line.tax_line for tax in line.tax_line if tax.tax_id.ret ]
        #~ return acc_id
    
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
        
        #~ wh_line_obj = self.pool.get('account.wh.src.line')
        #~ wh_lines = ids and wh_line_obj.search(cr, uid, [('retention_id', '=', ids[0])]) or False
        #~ res_wh_lines = []
        #~ if wh_lines:
            #~ wh_line_obj.unlink(cr, uid, wh_lines)
        #~ 
        #~ inv_ids = inv_obj.search(cr,uid,[('state', '=', 'open'), ('wh_src', '=', False), ('partner_id','=',partner_id)],context=context)
        #~ 
        #~ if inv_ids:
         #~ 
            #~ inv_ids = [i for i in inv_ids if not wh_line_obj.search(cr, uid, [('invoice_id', '=', i)])]
        #~ inv_ids = self._withholdable_tax_(cr, uid, inv_ids, context=None)
        #~ if inv_ids:
            #~ awil_obj = self.pool.get('account.wh.src.line')
            #~ res_wh_lines = [{
                        #~ 'invoice_id':   inv_brw.id,
                        #~ 'name':         inv_brw.name or _('N/A'),
                        #~ 'wh_src_rate':  inv_brw.partner_id.wh_src_rate,
                        #~ } for inv_brw in inv_obj.browse(cr,uid,inv_ids,context=context)]
        
        res = {'value': {
            'account_id': acc_id,
            }
        }

        return res

account_wh_src()

class account_wh_src_line(osv.osv):

    _name = "account.wh.src.line"
    _description = "Social Responsibility Commitment Withholding Line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Local Withholding line Description"),
        'wh_id': fields.many2one('account.wh.src', 'Local withholding', ondelete='cascade', help="Local withholding"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='set null', help="Withholding invoice"),
        'base_amount':fields.float('Amount', digits_compute= dp.get_precision('Withhold')),
        'wh_amount':fields.float('Amount', digits_compute= dp.get_precision('Withhold')),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account Entry"),
        'wh_src_rate':fields.float('Rate', help="Local withholding rate"),
        'concepto_id': fields.integer('Concept', size=3, help="Local withholding concept"),
    }
    _defaults = {

    }
    _sql_constraints = [

    ] 
    

account_wh_src_line()
