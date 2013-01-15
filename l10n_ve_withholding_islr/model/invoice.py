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
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
import netsvc

class account_invoice_line(osv.osv):
    '''
    It adds a field that determines if a line has been retained or not
    '''
    _inherit = "account.invoice.line"
    _columns = {
        'apply_wh': fields.boolean('Withheld',help="Indicates whether a line has been retained or not, to accumulate the amount to withhold next month, according to the lines that have not been retained."),
        'concept_id': fields.many2one('islr.wh.concept','Withholding  Concept',help="Concept of Income Withholding asociate this rate",required=False),
    }
    _defaults = {
        'apply_wh': lambda *a: False,
    }

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id     =False, context=None, company_id=None):
        '''
        Onchange to show the concept of retention associated with the product at once in the line of the bill
        '''
        if context is None:
            context = {}
        data = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id     =False, context=None, company_id=None)
        if product:
            pro = self.pool.get('product.product').browse(cr, uid, product, context=context)
            data[data.keys()[1]]['concept_id'] = pro.concept_id.id
        return data
        
    
    def create(self, cr, uid, vals, context=None):
        
        if context is None :
            context = {}
        
        if context.get('new_key',False):

            vals.update({'wh_xml_id':False,
                         'apply_wh': False,
                
            })
        
        return super(account_invoice_line, self).create(cr, uid, vals, context=context)
    

account_invoice_line()


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    _columns = {
        'status': fields.selection([
            ('pro','Processed withholding, xml Line generated'),
            ('no_pro','Withholding no processed'),
            ('tasa','Not exceed the rate,xml Line generated'),
            ],'Status',readonly=True,
            help=' * The \'Processed withholding, xml Line generated\' state is used when a user is a withhold income is processed. \
            \n* The \'Withholding no processed\' state is when user create a invoice and withhold income is no processed. \
            \n* The \'Not exceed the rate,xml Line generated\' state is used when user create invoice,a invoice no exceed the minimun rate.'),
    }
    _defaults = {
        'status': lambda *a: "no_pro",
    }
## BEGIN OF REWRITING ISLR

    def check_invoice_type(self, cr, uid, ids, context=None):
        '''
        This method check if the given invoice record is from a supplier
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_brw = self.browse(cr, uid, ids[0],context=context)
        return inv_brw.type in ('in_invoice', 'in_refund')

    def check_withholdable_concept(self, cr, uid, ids, context=None):
        '''
        Check if the given invoice record is ISLR Withholdable 
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        return iwdi_obj._get_concepts(cr, uid, ids, context=context)

    def _create_doc_invoices(self,cr,uid,ids,islr_wh_doc_id,context=None):
        '''
        This method link the invoices to be withheld 
        with the withholding document.
        '''
        #TODO: CHECK IF THIS METHOD SHOULD BE HERE OR IN THE ISLR WH DOC
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        iwhdi_ids=[] 
        for inv_id in ids:
            iwhdi_ids.append(doc_inv_obj.create(cr,uid,
                {'invoice_id':inv_id,'islr_wh_doc_id':islr_wh_doc_id}))
        return iwhdi_ids

    def _create_islr_wh_doc(self,cr,uid,ids,context=None):
        '''
        Funcion para crear en el modelo islr_wh_doc
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        
        doc_line_obj = self.pool.get('islr.wh.doc.line')
        wh_doc_obj = self.pool.get('islr.wh.doc')
        inv_obj =self.pool.get('account.invoice.line')
        rate_obj = self.pool.get('islr.rates')
        
        row = self.browse(cr,uid,ids[0],context=context)
        context['type']=row.type
        wh_ret_code = wh_doc_obj.retencion_seq_get(cr, uid)
        
        if wh_ret_code:
            islr_wh_doc_id = wh_doc_obj.create(cr,uid,
            {'name': wh_ret_code,
            'partner_id': row.partner_id.id,
            'period_id': row.period_id.id,
            'account_id': row.account_id.id,
            'type': row.type,
            'journal_id': wh_doc_obj._get_journal(cr,uid,context=context),})
            self._create_doc_invoices(cr,uid,row.id,islr_wh_doc_id)
            
            self.pool.get('islr.wh.doc').compute_amount_wh(cr, uid,
                    [islr_wh_doc_id], context=context )
            if row.company_id.automatic_income_wh is True:
                self.pool.get('islr.wh.doc').write(cr, uid, islr_wh_doc_id,
                        {'automatic_income_wh':True}, context=context)
        else:
            raise osv.except_osv(_('Invalid action !'),_("No se ha encontrado el numero de secuencia!"))

        self.write(cr,uid,ids,{'islr_wh_doc_id':islr_wh_doc_id,'islr_wh_doc_name':wh_ret_code})

        #wf_service = netsvc.LocalService("workflow")
        #wf_service.trg_validate(uid, 'islr.wh.doc', islr_wh_doc_id, 'button_confirm', cr)
        return islr_wh_doc_id
## END OF REWRITING ISLR

    def copy(self, cr, uid, id, default=None, context=None):
        
        if default is None:
            default = {}
        
        if context is None :
            context = {}
            
        default = default.copy()
        default.update({'islr_wh_doc':0,
                        'status': 'no_pro',
        })
        
        context.update({'new_key':True})
        
        return super(account_invoice, self).copy(cr, uid, id, default, context)


    def _refund_cleanup_lines(self, cr, uid, lines):
        data = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        list = []
        for x,y,res in data:
            if 'concept_id' in res:
                res['concept_id'] = res.get('concept_id', False) and res['concept_id']
            if 'apply_wh' in res:
                res['apply_wh'] = False
            if 'wh_xml_id' in res:
                res['wh_xml_id'] = 0
            list.append((x,y,res))
        return list

    def validate_wh_income_done(self, cr, uid, ids, context=None):
        """
        Method that check if wh income is validated in invoice refund.
        @params: ids: list of invoices.
        return: True: the wh income is validated.
                False: the wh income is not validated.
        """
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice', 'out_refund') and not inv.islr_wh_doc_id:
                rislr = True
            else:
                rislr = not inv.islr_wh_doc_id and True or inv.islr_wh_doc_id.state in ('done') and True or False
                if not rislr:
                    raise osv.except_osv(_('Error !'), \
                                     _('The Document you are trying to refund has a income withholding "%s" which is not yet validated!' % inv.islr_wh_doc_id.code ))
                    return False
        return True

account_invoice()
