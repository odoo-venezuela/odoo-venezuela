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

from openerp.osv import fields, osv
from openerp.tools.translate import _
class account_invoice(osv.osv):

    def _get_journal(self, cr, uid, context=None):
        """ Return the journal which is 
        used in the current user's company, otherwise
        it does not exist, return false
        """
        
        if context is None:
            context = {}
        journal_type_inv = context.get('journal_type', 'sale')
        
        if journal_type_inv in ('sale_debit', 'purchase_debit'):
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            company_id = context.get('company_id', user.company_id.id)
            journal_obj = self.pool.get('account.journal')
            res = journal_obj.search(cr, uid, [('type', '=',journal_type_inv),
                                               ('company_id', '=', company_id)],
                                                    limit=1)
            return res and res[0] or False
        else:
            return super(account_invoice, self)._get_journal(cr, uid, context=context)
    
    def _unique_invoice_per_partner(self, cr, uid, ids, context=None):
        """ Return false when it is found 
        that the bill is not out_invoice or out_refund,
        and it is not unique to the partner.
        """
        
        if context is None: context={}
        inv_brw = self.browse(cr, uid, ids, context=context)
        ids_ivo = []
        for inv in inv_brw:
            ids_ivo.append(inv.id)
            if inv.type in ('out_invoice','out_refund'):
                return True
            inv_ids = inv.nro_ctrl is not '' and inv.nro_ctrl is not False and inv.supplier_invoice_number is not False and self.search(cr,uid,
                        ['|',('nro_ctrl','=',inv.nro_ctrl and inv.nro_ctrl.strip() ),('supplier_invoice_number','=',inv.supplier_invoice_number and inv.supplier_invoice_number.strip()),
                        ('type','=',inv.type),
                        ('partner_id','=',inv.partner_id.id)],
                        context=context) or []
            if [True for i in inv_ids if i not in ids_ivo ] and inv_ids:
                return False
        return True

    def _get_loc_req(self, cr, uid, context=None):
        """Get if a field is required or not by a Localization
        @param uid: Integer value of the user
        """
        context = context or {}
        res = True
        ru_brw = self.pool.get('res.users').browse(cr,uid,uid,context=context)
        rc_obj = self.pool.get('res.company')
        rc_brw = rc_obj.browse(cr, uid, ru_brw.company_id.id, context=context)
        
        if rc_brw.country_id and rc_brw.country_id.code == 'VE' and rc_brw.printer_fiscal:
            res = False
        return res

    _inherit = 'account.invoice'
    _columns = {
        'nro_ctrl': fields.char('Control Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Number used to manage pre-printed invoices, by law you will need to put here this number to be able to declarate on Fiscal reports correctly."),
        'sin_cred': fields.boolean('Tax Exempt', readonly=False, help="Set it true if the invoice is VAT excempt"),
        'parent_id':fields.many2one('account.invoice', 'Parent Invoice', readonly=True, states={'draft':[('readonly',False)]}, help='When this field has information, this invoice is a credit note or debit note. This field is used to reference to the invoice that originated this credit note or debit note. if you are in a refund document, this field must be loaded, if you are in a out_invoice document plus this data filled it means this is a debit note'),
        'child_ids':fields.one2many('account.invoice', 'parent_id', 'Debit and Credit Notes', readonly=True, states={'draft':[('readonly',False)]}, help='This field is to know when it applyies what Credit Notes and Debit Notes are related to it'),
        'date_document': fields.date("Document Date", help="Administrative date, generally is the date printed on invoice, this date is used to show in the Purchase Fiscal book", select=True),
        'invoice_printer' : fields.char('Fiscal printer invoice number', size=64, required=False,help="Fiscal printer invoice number, is the number of the invoice on the fiscal printer"),
        #TODO": maybe it must be a many2one to declared FiscalPrinter when FiscalV is ready
        'fiscal_printer' : fields.char('Fiscal printer number', size=64, required=False,help="Fiscal printer number, generally is the id number of the printer."),
        'loc_req':fields.boolean('Required by Localization', help='This fields is for technical use'),
        'z_report': fields.char(string='Report Z', size=64, help=""),
    }

    _defaults ={
        'loc_req': _get_loc_req
        }


    _constraints = [
          (_unique_invoice_per_partner, _('The Document you have been entering for this Partner has already been recorded'),['Control Number (nro_ctrl)','Reference (reference)']),
         ]

    def copy(self, cr, uid, id, default={}, context=None):
        """ Allows you to duplicate a record,
        child_ids, nro_ctrl and reference fields are
        cleaned, because they must be unique
        """
        if context is None:
            context = {}
        default.update({
            'child_ids':[],
            'nro_ctrl':None,
            'supplier_invoice_number':None, 
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        if vals.get('type') in ('out_invoice','out_refund') and \
            vals.get('date_invoice') and not vals.get('date_document'):
            vals['date_document']=vals['date_invoice']
        return super(account_invoice, self).write(cr, uid, ids, vals,
                                                    context=context)

account_invoice()


class account_invoice_tax(osv.osv):
    _inherit = 'account.invoice.tax'
    _columns = {
        'tax_id': fields.many2one('account.tax', 'Tax', required=False, ondelete='set null', 
        help="Tax relation to original tax, to be able to take off all data from invoices."),
    }

account_invoice_tax()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
