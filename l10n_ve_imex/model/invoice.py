# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Vauxoo C.A. (http://openerp.com.ve/)
#    All Rights Reserved
############# Credits #########################################################
#    Coded by:  Juan Marzquez (Tecvemar, c.a.) <jmarquez@tecvemar.com.ve>
#               Katherine Zaoral               <katherine.zaoral@vauxoo.com>
#    Planified by:
#                Juan Marquez                  <jmarquez@tecvemar.com.ve>
#                Humberto Arocha               <hbto@vauxoo.com>
#    Audited by: Humberto Arocha               <hbto@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'customs_form_id': fields.many2one(
            'customs.form', 'Customs form', change_default=True,
            required=False, readonly=True,
            states={'draft': [('readonly', False)]}, ondelete='restrict',
            domain=[('state', '=', ('draft'))],
            help="The related form 86 for this import invoice (only draft)"),
        'imex_tax_line': fields.one2many(
            'account.invoice.tax', 'imex_inv_id', 'Vat lines', readonly=True,
            attrs="{'readonly':[('vat_detail','=',True)], \
            'required':[('vat_detail','=',True)]}",),
        'expedient':fields.boolean('Dossier', readonly=True,
                                   states={'draft':[('readonly',False)]},
                                   help="If it is true, it means this is a \
                                   landindg form, you will need to load this \
                                   format as an purchase invoice to declarate \
                                   on Book"),
    }

    def on_change_customs_form_id(self, cr, uid, ids, customs_form_id, context=None):
        context = context or {}
        res = {}
        if customs_form_id:
            imp = self.pool.get('customs.form').browse(cr, uid,
                                                         customs_form_id,
                                                         context=context)
            res = {'value': {'num_import_form': imp.name,
                             'import_invo': imp.date_liq}}
        return res

    def test_open(self, cr, uid, ids, *args):
        so_brw = self.browse(cr, uid, ids, context={})
        for item in so_brw:
            if item.customs_form_id and \
                    item.customs_form_id.state in ('draft', 'cancel'):
                raise osv.except_osv(_('Error!'), _(
                    'Can\'t validate a invoice while the form 86 state\'s is \
                    cancel or draft (%s).\nPlease validate the form 86 first.')
                    % item.customs_form_id.name)
        return super(account_invoice, self).test_open(cr, uid, ids, args)

class inheried_account_invoice_tax(osv.osv):

    _inherit = 'account.invoice.tax'

    _columns = {
        'cfl_id': fields.many2one('customs.form.line',
                                                'Vat line',
                                                 ondelete='cascade'),
        'imex_inv_id': fields.many2one('account.invoice', 'Imex Invoice',
                                       ondelete='cascade', select=True),
        'partner_id': fields.related('imex_inv_id', 'partner_id',
                                     type='many2one', relation='res.partner',
                                     string='Supplier'),
        'supplier_invoice_number': fields.related('imex_inv_id', 'supplier_invoice_number', type='char',
                                    string='Invoice ref', size=64, store=False,
                                    readonly=True),
    }

    _defaults = {
    }

    #~ _sql_constraints = [
        #~ ('base_gt_zero', 'CHECK (base>0)',
         #~ 'The base amount must be > 0!'),
        #~ ('amount_zero', 'CHECK (amount>=0)',
         #~ 'The tax amount must be >= 0!'),
    #~ ]

    #~ def on_change_cfl_id(self, cr, uid, ids,
        #~                                cfl_id):
        #~ '''
        #~ Create a domain to filter invoice_id for invoices listed in
        #~ customs_form.invoice_ids only
        #~ http://help.openerp.com/question/11180/how-to-create-a-domain-for-
        #~ field-in-parentparent-model/
        #~ '''
        #~ res = {}
        #~ if cfl_id:
            #~ line_obj = self.pool.get('customs.form.line')
            #~ invoices = [i.id for i in line_obj.browse(
                #~ cr, uid, cfl_id).customs_form_id.invoice_ids]
            #~ res = {'domain': {'invoice_id': [('id','in',invoices)]}}
        #~ return res

    def on_change_amount(self, cr, uid, ids, tax_id, base_amount, tax_amount,
                         context=None):
        """ To autocompute base or tax, only for percent based taxes. """
        context = context or {}
        res = {}
        if tax_id:
            obj_vat = self.pool.get('account.tax')
            vat = obj_vat.browse(cr, uid, tax_id, context=context)
            if vat.type == 'percent':
                if base_amount == 0 and tax_amount > 0:
                    base_amount = round(tax_amount / vat.amount, 2)
                    res = {'value': {'base_amount': base_amount,
                                     'base': base_amount,
                                     'amount': tax_amount}}

                if base_amount > 0 and tax_amount == 0:
                    res = {'value': {'base_amount': 0.0,
                                   'base': 0.0,
                                   'amount': tax_amount}}

        return res

    def on_change_invoice_id(self, cr, uid, ids, invoice_id, context=None):
        context = context or {}
        res = {}
        if invoice_id:
            obj_inv = self.pool.get('account.invoice')
            inv = obj_inv.browse(cr, uid, invoice_id, context=context)
            res = {'value': {'partner_id': inv.partner_id.id,
                             'supplier_invoice_number': inv.supplier_invoice_number}}
        return res

    def on_change_tax_id(self, cr, uid, ids, tax_id, context=None):
        context = context or {}
        res = {}
        if tax_id:
            at_obj = self.pool.get('account.tax')
            tax_brw = at_obj.browse(cr, uid, tax_id, context=context)
            if tax_brw:
                res = {'value': {'account_id': tax_brw.account_collected_id.id,
                                 'name': tax_brw.name}}
        else:
            res = {'value': {'account_id': False, 'name': False}}
        return res
