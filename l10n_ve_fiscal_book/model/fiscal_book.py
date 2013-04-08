#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#              Katherine Zaoral          <katherine.zaoral@vauxoo.com>
#    Planified by: Humberto Arocha & Nhomar Hernandez
#    Audited by: Humberto Arocha           <hbto@vauxoo.com>
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
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp


class fiscal_book(orm.Model):

    def _get_type(self, cr, uid, context=None):
        context = context or {}
        return context.get('type', 'purchase')

    def _get_invoice_ids(self, cr, uid, fb_id, context=None):
        """
        It returns ids from open and paid invoices regarding to the type and
        period of the fiscal book order by date invoiced.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        inv_type = fb_brw.type == 'sale' \
            and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        inv_state = ['paid', 'open']
        #~ pull invoice data
        inv_ids = inv_obj.search(cr, uid,
                                 [('period_id', '=', fb_brw.period_id.id),
                                  ('type', 'in', inv_type),
                                  ('state', 'in', inv_state)],
                                 order='date_invoice asc', context=context)
        return inv_ids

    def _get_issue_invoice_ids(self, cr, uid, fb_id, context=None):
        """
        It returns ids from not open or paid invoices regarding to the type and
        period of the fiscal book order by date invoiced.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        inv_type = fb_brw.type == 'sale' \
            and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        inv_state = ['paid', 'open']
        #~ pull invoice data
        issue_inv_ids = inv_obj.search(cr, uid,
            ['|',
             '&', ('fb_id', '=', fb_brw.id),  ('period_id', '!=', fb_brw.period_id.id),
             '&', '&', ('period_id', '=', fb_brw.period_id.id), ('type', 'in', inv_type),
                       ('state', 'not in', inv_state)],
            order='date_invoice asc', context=context)

        return issue_inv_ids

    def _get_wh_iva_line_ids(self, cr, uid, fb_id, context=None):
        """
        It returns ids from wh iva lines with state 'done' regarding to the
        fiscal book period.
        """
        context = context or {}
        awi_obj = self.pool.get('account.wh.iva')
        awil_obj = self.pool.get('account.wh.iva.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        awil_type = fb_brw.type == 'sale' \
            and ['out_invoice', 'out_refund'] \
            or ['in_invoice', 'in_refund']
        #~ pull wh iva line data
        awil_ids = []
        awi_ids = awi_obj.search(cr, uid,
                                 [('period_id', '=', fb_brw.period_id.id),
                                 ('type', 'in', awil_type),
                                 ('state', '=', 'done')],
                                 context=context)
        for awi_id in awi_ids:
            list_ids = awil_obj.search(cr, uid,
                                       [('retention_id', '=', awi_id)], context=context)
            awil_ids.extend(list_ids)
        return awil_ids or False

    def _get_invoice_iwdl_id(self, cr, uid, fb_id, inv_id, context=None):
        """
        Check if the invoice have wh iva lines asociated and if its check if it
        is at the same period. Return the wh iva line ID or False instead.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
        iwdl_obj = self.pool.get('account.wh.iva.line')
        iwdl_id = False
        if inv_brw.wh_iva_id:
            iwdl_id = iwdl_obj.search(cr, uid,
                                      [('invoice_id', '=', inv_brw.id),
                                       ('fb_id', '=', fb_id)],
                                      context=context)
        return iwdl_id and iwdl_id[0] or False

    #~ TODO: test this method.
    def _get_ordered_orphan_iwdl_ids(self, cr, uid, orphan_iwdl_ids, context=None):
        """
        Returns a list of orphan wh iva lines IDs order by date_ret asc.
        """
        context = context or {}
        awil_obj = self.pool.get('account.wh.iva.line')
        return awil_obj.search(cr, uid, [('id', 'in', (orphan_iwdl_ids))],
                               order='date_ret asc', context=context)

    def _get_book_taxes_ids(self, cr, uid, inv_ids, context=None):
        """
        It returns account invoice taxes IDSs from the fiscal book invoices.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        ait_ids = []
        for inv_brw in inv_obj.browse(cr, uid, inv_ids, context=context):
            ait_ids += [ ait.id for ait in inv_brw.tax_line ]
        return ait_ids
        
    #~ TODO: method not used. please check if it needs to be delete.
    def _get_book_line_id(self, cr, uid, fb_id, inv_id=None, iwdl_id=None,
                         context=None):
        """
        It returns the book line ID associated to the given invoice or a given
        wh iva line, if it dosent have one return False.
        """
        context = context or {}
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        for book_line in fb_brw.fbl_ids:
            if (inv_id and (inv_id is book_line.invoice_id.id)) or \
                (iwdl_id and (iwdl_id is book_line.iwdl_id.id)):
                return book_line.id
        return False

    def _get_orphan_iwdl_ids(self, cr, uid, inv_ids, iwdl_ids, context=None):
        """
        It returns ids from the orphan wh iva lines in the period that have not
        associated invoice, order by date ret
        """
        context = context or {}
        iwdl_obj = self.pool.get('account.wh.iva.line')
        iwdl_brws = iwdl_obj.browse(cr, uid, iwdl_ids, context=context)
        inv_wh_ids = [i.invoice_id.id for i in iwdl_brws]
        orphan_inv_ids = set(inv_wh_ids) - set(inv_ids)
        orphan_inv_ids = list(orphan_inv_ids)
        orphan_iwdl_ids = orphan_inv_ids and iwdl_obj.search(cr, uid, [('invoice_id', 'in', orphan_inv_ids)], context=context) or False
        return orphan_iwdl_ids and self._get_ordered_orphan_iwdl_ids(cr, uid, orphan_iwdl_ids, context=context)

    def clear_book(self, cr, uid, fb_id, context=None):
        """
        It delete all book data information.
        """
        context = context or {}
        #~ clear fields
        self.clear_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        #~ delete data
        self.clear_book_lines(cr, uid, fb_id, context=context)
        self.clear_book_taxes(cr, uid, fb_id, context=context)
        self.clear_book_taxes_summary(cr, uid, fb_id, context=context)
        #~ unrelate data
        self.clear_book_invoices(cr, uid, fb_id, context=context)
        self.clear_book_issue_invoices(cr, uid, fb_id, context=context)
        self.clear_book_iwdl_ids(cr, uid, fb_id, context=context)
        return True

    def clear_book_lines(self, cr, uid, ids, context=None):
        """
        It delete all book lines loaded in the book.
        """
        context = context or {}
        fbl_obj = self.pool.get("fiscal.book.lines")
        for fb_id in ids:
            fbl_brws = self.browse(cr, uid, fb_id, context=context).fbl_ids
            fbl_ids = [ fbl.id for fbl in fbl_brws ]
            fbl_obj.unlink(cr, uid, fbl_ids, context=context)
            self.clear_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        return True

    def clear_book_taxes(self, cr, uid, ids, context=None):
        """
        It delete all book taxes loaded in the book.
        """
        context = context or {}
        fbt_obj = self.pool.get("fiscal.book.taxes")
        for fb_id in ids:
            fbt_brws = self.browse(cr, uid, fb_id, context=context).fbt_ids
            fbt_ids = [ fbt.id for fbt in fbt_brws ]
            fbt_obj.unlink(cr, uid, fbt_ids, context=context)
            self.clear_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        return True

    def clear_book_taxes_summary(self, cr, uid, fb_id, context=None):
        """
        It delete fiscal book taxes summary data for the book.
        """
        context = context or {}
        fbts_obj = self.pool.get('fiscal.book.taxes.summary')
        fbts_ids = fbts_obj.search(cr, uid, [('fb_id', '=', fb_id)],
                                   context=context)
        fbts_obj.unlink(cr, uid, fbts_ids, context=context)
        return True

    def clear_book_taxes_amount_fields(self, cr, uid, fb_id, context=None):
        """
        Clean amount taxes fields in fiscal book.
        """
        context = context or {}
        return self.write(cr, uid, fb_id, {'tax_amount': 0.0, 'base_amount': 0.0}, context=context)

    def clear_book_invoices(self, cr, uid, ids, context=None):
        """
        Unrelate all invoices of the book. And delete fiscal book taxes.
        """
        context = context or {}
        inv_obj = self.pool.get("account.invoice")
        for fb_id in ids:
            self.clear_book_taxes(cr, uid, [fb_id], context=context)
            inv_brws = self.browse(cr, uid, fb_id, context=context).invoice_ids
            inv_ids = [ inv.id for inv in inv_brws ]
            inv_obj.write(cr, uid, inv_ids, {'fb_id': False}, context=context)
        return True

    def clear_book_issue_invoices(self, cr, uid, ids, context=None):
        """
        Unrelate all issue invoices of the book.
        """
        context = context or {}
        inv_obj = self.pool.get("account.invoice")
        for fb_id in ids:
            inv_brws = self.browse(cr, uid, fb_id, context=context).issue_invoice_ids
            inv_ids = [ inv.id for inv in inv_brws ]
            inv_obj.write(cr, uid, inv_ids, {'issue_fb_id': False}, context=context)
        return True

    def clear_book_iwdl_ids(self, cr, uid, ids, context=None):
        """
        Unrelate all wh iva lines of the book.
        """
        context = context or {}
        iwdl_obj = self.pool.get("account.wh.iva.line")
        for fb_id in ids:
            iwdl_brws = self.browse(cr, uid, fb_id, context=context).iwdl_ids
            iwdl_ids = [ iwdl.id for iwdl in iwdl_brws ]
            iwdl_obj.write(cr, uid, iwdl_ids, {'fb_id': False}, context=context)
        return True

    def update_book(self, cr, uid, ids, context=None):
        """
        It Generate and Fill book data with invoices wh iva lines and taxes.
        """
        context = context or {}
        for fb_brw in self.browse(cr, uid, ids, context=context):
            inv_ids = self.update_book_invoices(cr, uid, fb_brw.id, context=context)
            iwdl_ids = self.update_book_wh_iva_lines(cr, uid, fb_brw.id, context=context)
            self.update_book_taxes(cr, uid, fb_brw.id, inv_ids, context=context)
            self.update_book_lines(cr, uid, fb_brw.id, inv_ids, iwdl_ids, context=context)
            fbl_ids = [ fbl.id for fbl in fb_brw.fbl_ids ]
            self.update_book_issue_invoices(cr, uid, fb_brw.id, context=context)
        return True

    def update_book_invoices(self, cr, uid, fb_id, context=None):
        """
        It relate/unrelate the invoices to the fical book.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        #~ Relate invoices
        inv_ids = self._get_invoice_ids(cr, uid, fb_id, context=context)
        inv_obj.write(cr, uid, inv_ids, {'fb_id': fb_id}, context=context)
        #~ update book taxes
        self.update_book_taxes(cr, uid, fb_id, inv_ids, context=context)

        #~ TODO: move this process to the cancel process of the invoice
        #~ Unrelate invoices (period book change, invoice now cancel/draft or
        #~ have change its period)
        all_inv_ids = inv_obj.search(cr, uid, [('fb_id', '=', fb_id)],
                                     context=context)
        for inv_id_to_check in all_inv_ids: 
            if inv_id_to_check not in inv_ids:
                inv_obj.write(cr, uid, inv_id_to_check, {'fb_id': False},
                              context=context)
        return inv_ids

    def update_book_issue_invoices(self, cr, uid, fb_id, context=None):
        """
        It relate the issue invoices to the fiscal book. That criterion is:
            - Invoices of the period in state different form open or paid state.
            - Invoices already related to the book but it have a period change. 
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        issue_inv_ids = self._get_issue_invoice_ids(cr, uid, fb_id, context=context)
        inv_obj.write(cr, uid, issue_inv_ids, {'issue_fb_id': fb_id}, context=context)
        return issue_inv_ids

    #~ TODO: test this method.
    def update_book_wh_iva_lines(self, cr, uid, fb_id, context=None):
        """
        It relate/unrelate the wh iva lines to the fical book.
        """
        context = context or {}
        iwdl_obj = self.pool.get('account.wh.iva.line')
        #~ Relate wh iva lines
        iwdl_ids = self._get_wh_iva_line_ids(cr, uid, fb_id, context=context)
        iwdl_obj.write(cr, uid, iwdl_ids, {'fb_id': fb_id}, context=context)
        #~ Unrelate wh iva lines (period book change, wh iva line have been
        #~ cancel or have change its period)
        all_iwdl_ids = iwdl_obj.search(cr, uid, [('fb_id', '=', fb_id)],
                                       context=context)
        for iwdl_id_to_check in all_iwdl_ids:
            if iwdl_id_to_check not in iwdl_ids:
                iwdl_obj.write(cr, uid, iwdl_id_to_check, {'fb_id': False},
                              context=context)
        return iwdl_ids

    def update_book_taxes(self, cr, uid, fb_id, inv_ids, context=None):
        """
        It relate/unrelate the invoices taxes from the period to the fical book.
        """
        context = context or {}
        fbt_obj = self.pool.get('fiscal.book.taxes')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        ait_ids = self._get_book_taxes_ids(cr, uid, inv_ids, context=context)
        fbt_ids = fbt_obj.search(cr, uid, [('fb_id', '=', fb_id )],
                                 context=context)
        #~ Unrelate taxes
        fbt_obj.unlink(cr, uid, fbt_ids, context=context)
        #~ Relate taxes
        data = map(lambda x: (0, 0, {'ait_id': x}), ait_ids)
        self.write(cr, uid, fb_id, {'fbt_ids' : data}, context=context)
        return True

    def update_book_lines(self, cr, uid, fb_id, inv_ids, iwdl_ids, context=None):
        """
        It updates the fiscal book lines values.
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        iwdl_obj = self.pool.get('account.wh.iva.line')
        fbl_obj = self.pool.get('fiscal.book.lines')
        my_rank = 1
        #~ delete book lines
        fbl_ids = fbl_obj.search(cr, uid, [('fb_id','=',fb_id)], 
                                 context=context)
        fbl_obj.unlink(cr, uid, fbl_ids, context=context)
        #~ add book lines for orphan withholding iva lines
        data = []
        orphan_iwdl_ids = iwdl_ids and self._get_orphan_iwdl_ids(cr, uid, inv_ids, iwdl_ids, context=context) or False
        if orphan_iwdl_ids:
            for iwdl_brw in iwdl_obj.browse(cr, uid, orphan_iwdl_ids, context=context):
                values = {}
                values = {
                    'iwdl_id': iwdl_brw.id,
                    'rank': my_rank,
                    'get_credit_affected': False,
                    'get_date_invoiced': iwdl_brw.date or False,
                    'get_t_doc': 'RET',
                    #~ TODO: override 'get_t_doc' value by creating an function that take care of it.
                    'get_number': iwdl_brw.retention_id.number or False,
                    #~ TODO: check what fields needs to be add that refer to the book line and the wh iva line.
                }
                my_rank = my_rank + 1 
                data.append((0, 0, values))

        #~ add book lines for invoices
        if inv_ids:
            for inv_brw in inv_obj.browse(cr, uid, inv_ids, context=context):
                values = {}
                values = {
                    'invoice_id': inv_brw.id,
                    'rank': my_rank,
                    'get_credit_affected': inv_brw.get_credit_affected or False,
                    'get_date_imported': inv_brw.get_date_imported or False,
                    'get_date_invoiced': inv_brw.get_date_invoiced or False,
                    'get_debit_affected': inv_brw.get_debit_affected or False,
                    'get_doc': inv_brw.get_doc or False,
                    'get_number': inv_brw.get_number or False,
                    'get_parent': inv_brw.get_parent or False,
                    'get_partner_name': inv_brw.get_partner_name or False,
                    'get_partner_vat': inv_brw.get_partner_vat or False,
                    'get_reference': inv_brw.get_reference or False,
                    'get_t_doc': inv_brw.get_t_doc or False,
                    'iwdl_id': self._get_invoice_iwdl_id(cr, uid, fb_id,
                                                         inv_brw.id,
                                                         context=context)
                }
                my_rank = my_rank + 1 
                data.append((0, 0, values))

        if data:
            self.write(cr, uid, fb_id, {'fbl_ids' : data}, context=context)
            self.link_book_lines_and_taxes(cr, uid, fb_id, context=context)

        return True

    #~ TODO: Optimization. This method could be transform in a method for function field fbts tax y base sum. 
    def update_book_taxes_summary(self, cr, uid, fb_id, context=None):
        """
        It update the summaroty of taxes by type for this book.
        """
        context = context or {}
        self.clear_book_taxes_summary(cr, uid, fb_id, context=context)
        tax_types = ['exento', 'sdcf', 'reducido', 'general', 'adicional']
        base_sum = {}.fromkeys(tax_types, 0.0)
        tax_sum  = {}.fromkeys(tax_types, 0.0)
        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                for ait in fbl.invoice_id.tax_line:
                    if ait.tax_id.appl_type:
                        base_sum[ait.tax_id.appl_type] += ait.base_amount
                        tax_sum[ait.tax_id.appl_type] += ait.tax_amount 
        data = [ (0, 0, {'tax_type': ttype, 'base_amount_sum': base_sum[ttype], 'tax_amount_sum': tax_sum[ttype]}) for ttype in tax_types ]
        return data and self.write(cr, uid, fb_id, {'fbts_ids': data}, context=context)

    #~ TODO: test this method (with presice amounts)
    def update_book_taxes_amount_fields(self, cr, uid, fb_id, context=None):
        """
        It update the base_amount and the tax_amount field for fiscal book.
        """
        context = context or {}
        tax_amount = base_amount = 0.0
        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                for ait in fbl.invoice_id.tax_line:
                    if ait.tax_id:
                        base_amount = base_amount + ait.base_amount
                        if ait.tax_id.ret:
                            tax_amount = tax_amount + ait.tax_amount
        return self.write(cr, uid, fb_id, {'tax_amount': tax_amount, 'base_amount': base_amount}, context=context)

    def link_book_lines_and_taxes(self, cr, uid, fb_id, context=None):
        """
        It updates the fiscal book taxes. Link the tax with the corresponding
        book line and update the fields of sum taxes in the book.
        """
        context = context or {}
        fbt_obj = self.pool.get('fiscal.book.taxes')
        fbl_obj = self.pool.get('fiscal.book.lines')
        #~ delete book taxes
        fbt_ids = fbt_obj.search(cr, uid, [('fb_id', '=', fb_id)],
                                 context=context)
        fbt_obj.unlink(cr, uid, fbt_ids, context=context)
        #~ write book taxes
        data = []
        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                ret_tax_amount = sdcf_tax_amount = exent_tax_amount = amount_withheld = 0.0
                for ait in fbl.invoice_id.tax_line:
                    if ait.tax_id:
                        data.append((0, 0, {'fb_id': fb_id, 'fbl_id': fbl.id, 'ait_id': ait.id}))
                        if ait.tax_id.ret:
                            ret_tax_amount = ret_tax_amount + ait.base_amount + ait.tax_amount

                            #~ TODO: check that this logic is ok
                            if ait.invoice_id.type in ['in_refund', 'out_refund']:
                                amount_withheld = amount_withheld + (ait.tax_amount*(-1.0))
                            else:
                                amount_withheld = amount_withheld + ait.tax_amount
                        else:
                            if ait.tax_id.appl_type == 'sdcf':
                                sdcf_tax_amount = sdcf_tax_amount + ait.base_amount
                            if ait.tax_id.appl_type == 'exento':
                                exent_tax_amount = exent_tax_amount + ait.base_amount
                    else:
                        data.append((0,0,{'fb_id': fb_id, 'fbl_id': False, 'ait_id': ait.id}))
                fbl_obj.write(cr, uid, fbl.id, {'get_total': ret_tax_amount}, context=context)
                fbl_obj.write(cr, uid, fbl.id, {'get_v_sdcf': sdcf_tax_amount}, context=context)
                fbl_obj.write(cr, uid, fbl.id, {'get_v_exent': exent_tax_amount}, context=context)
                fbl_obj.write(cr, uid, fbl.id, {'get_withheld': amount_withheld}, context=context)

        if data:
            self.write(cr, uid, fb_id, {'fbt_ids': data}, context=context)
        self.update_book_taxes_summary(cr, uid, fb_id, context=context)
        self.update_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        return True

    def button_update_book_invoices(self, cr, uid, ids, context=None):
        """
        Take the instance of fiscal book and do the update of invoices.
        """
        context = context or {}
        self.update_book_invoices(cr, uid, ids[0], context=context)
        self.update_book_taxes_amount_fields(cr, uid, ids[0], context=context)
        return True

    def button_update_book_issue_invoices(self, cr, uid, ids, context=None):
        """
        Take the instance of fiscal book and do the update of issue invoices.
        """
        context = context or {}
        self.update_book_issue_invoices(cr, uid, ids[0], context=context)
        return True

    def button_update_book_wh_iva_lines(self, cr, uid, ids, context=None):
        """
        Take the instance of fiscal book and do the update of wh iva lines.
        """
        context = context or {}
        self.update_book_wh_iva_lines(cr, uid, ids[0], context=context)
        return True

    def button_update_book_lines(self, cr, uid, ids, context=None):
        """
        Take the instance of fiscal book and do the update book lines.
        """
        context = context or {}
        fb_brw = self.browse(cr, uid, ids[0], context=context)
        inv_ids = [ inv.id for inv in fb_brw.invoice_ids ]
        iwdl_ids = [ iwdl.id for iwdl in fb_brw.iwdl_ids ]
        self.update_book_lines(cr, uid, ids[0], inv_ids, iwdl_ids, context=context)
        return True

    def onchange_period_id(self, cr, uid, ids, context=None):
        """
        It make clear all stuff of book.
        """
        context = context or {}
        self.clear_book(cr, uid, ids, context=context)
        return True

    def _get_partner_addr(self, cr, uid, ids, field_name, arg, context=None):
        '''
        It returns Partner address printable format.
        '''
        context = context or {}
        result = {}
        addr_obj = self.pool.get('res.partner')
        #~ TODO: ASK: what company, fisal.book.company_id? 
        addr = self.pool.get('res.users').browse(cr,uid,uid,context=context).company_id.partner_id
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        if addr:
            addr_inv = addr.type == 'invoice' and (addr.street or '') + ' ' + \
            (addr.street2 or '') + ' ' + (addr.zip or '') + ' ' + \
            (addr.city or '') + ' ' + \
            (addr.country_id and addr.country_id.name or '')+ ', TELF.:' + \
            (addr.phone or '') or 'NO HAY DIRECCION FISCAL DEFINIDA'
        result[ids[0]] = addr_inv
        return result

    def _get_sum_col(self, cr, uid, ids, field_name, arg, context=None):
        '''
        It returns summatory of a fiscal book amount column.
        '''
        context = context or {}
        result = {}
        fbl_obj = self.pool.get('fiscal.book.lines')
        for fb_id in ids:
            col_sum = [ fbl_obj.read(cr, uid, fbl.id, context=context)[field_name] \
                        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids
                        if fbl.invoice_id ]
            result[fb_id] = sum(col_sum)
        return result


    _description = "Venezuela's Sale & Purchase Fiscal Books"
    _name='fiscal.book'
    _inherit = ['mail.thread']
    _columns={
        'name':fields.char('Description', size=256, required=True),
        'company_id':fields.many2one('res.company','Company',
            help='Company',required=True),
        'period_id':fields.many2one('account.period','Period',
            help="Book's Fiscal Period",required=True),
        'state': fields.selection([('draft','Getting Ready'),
            ('open','Approved by Manager'),('done','Seniat Submitted')],
            string='Status', required=True),
        'type': fields.selection([('sale','Sale Book'),
            ('purchase','Purchase Book')],
            help='Select Sale for Customers and Purchase for Suppliers',
            string='Book Type', required=True),
        'base_amount':fields.float('Taxable Amount',help='Amount used as Taxing Base'),
        'tax_amount':fields.float('Taxed Amount',help='Taxed Amount on Taxing Base'),
        'fbl_ids':fields.one2many('fiscal.book.lines', 'fb_id', 'Book Lines',
            help='Lines being recorded in a Fiscal Book'),
        'fbt_ids':fields.one2many('fiscal.book.taxes', 'fb_id', 'Tax Lines',
            help='Taxes being recorded in a Fiscal Book'),
        'fbts_ids':fields.one2many('fiscal.book.taxes.summary', 'fb_id', 'Tax Summary'),
        'invoice_ids':fields.one2many('account.invoice', 'fb_id', 'Invoices',
            help='Invoices being recorded in a Fiscal Book'),
        'issue_invoice_ids':fields.one2many('account.invoice', 'issue_fb_id', 'Issue Invoices',
            help='Invoices that are in pending state. Cancel or Draft'),
        'iwdl_ids':fields.one2many('account.wh.iva.line', 'fb_id', 'Vat Withholdings',
            help='Vat Withholdings being recorded in a Fiscal Book'),
        'abl_ids':fields.one2many('adjustment.book.line', 'fb_id', 'Adjustment Lines',
            help='Adjustment Lines being recorded in a Fiscal Book'),
        'note': fields.text('Note',required=True),

        #~ printable data
        'get_partner_addr': fields.function(_get_partner_addr, type="text",
                                            string='Partner address printable format'),
        'get_total': fields.function(_get_sum_col, type="float",
                                     string='Sum on Total with Iva Column.'),
        'get_v_sdcf': fields.function(_get_sum_col, type="float",
                                      string='Sum on SDCF Column.'),
        'get_v_exent': fields.function(_get_sum_col, type="float",
                                      string='Exempt Column Sum.'),
    }

    _defaults = {
        'state': 'draft',
        'type': _get_type,
        'company_id': lambda s,c,u,ctx: \
            s.pool.get('res.users').browse(c,u,u,context=ctx).company_id.id,
    }

    _sql_constraints = [
        ('period_type_company_uniq', 'unique (period_id,type,company_id)', 
            'The period and type combination must be unique!'),
    ]


class fiscal_book_lines(orm.Model):

    def _get_vat_amount(self, cr, uid, ids, field_name, arg, context=None):
        """
        For a given book line it returns the a vat amount value corresponding.
        (This is a method used in functional fields).
        @param field_name: the name of the field that which value return [get_vat_reduced_base, get_vat_general_base, get_vat_additional_base, get_vat_reduced_tax, get_vat_general_tax,  get_vat_additional_tax].
        """
        context = context or {}
        res = {}.fromkeys(ids, 0.0)
        tax_type = { 'reduced': 'reducido', 'general': 'general',
                     'additional': 'adicional' }
        field_tax, field_amount = field_name[8:].split('_')
        for fbl_id in ids:
            for fbt_brw in self.browse(cr, uid, fbl_id, context=context).fbt_ids:
                if fbt_brw.ait_id.tax_id.appl_type == tax_type[field_tax]:
                    res[fbl_id] += field_amount == 'base' \
                                   and fbt_brw.base_amount \
                                   or fbt_brw.tax_amount
        return res

    _description = "Venezuela's Sale & Purchase Fiscal Book Lines"
    _name='fiscal.book.lines'
    _rec_name='rank'
    _order = 'rank'
    _columns={
        'rank':fields.integer('Line Position', required=True),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        'invoice_id':fields.many2one('account.invoice','Invoice',
            help='Invoice related to this book line.'),
        'iwdl_id':fields.many2one('account.wh.iva.line','Vat Withholding',
            help='Fiscal Book where this line is related to'),
        'get_date_imported': fields.date(string='Imported Date', help=''),
        'get_date_invoiced': fields.date(string='Invoiced Date', help=''),
        'get_t_doc': fields.char(size=128, string='Doc. Type', help=''),
        'get_partner_vat': fields.char(size=128, string='Partner vat', 
            help=''),
        'get_partner_name': fields.char(string='Partner Name', help=''),
        'get_reference': fields.char(string='Invoice number', help=''),
        'get_number': fields.char(string='Control number', help=''),
        'get_doc': fields.char(string='Trans. Type', help=''),
        'get_debit_affected': fields.char(string='Affected Debit Notes', 
            help=''),
        'get_credit_affected': fields.char(string='Affected Credit Notes', 
            help=''),
        'get_parent': fields.char(string='Affected Document', help=''),
        'fbt_ids': fields.one2many('fiscal.book.taxes', 'fbl_id', 
            'Tax Lines',
            help='Tax Lines being recorded in a Fiscal Book'),
        'get_total': fields.float('Total with IVA'),
        'get_v_sdcf': fields.float('SDCF'),
        'get_v_exent': fields.float('Exent'),
        'get_withheld': fields.float('Withheld Amount'),

        'get_vat_reduced_base': fields.function(_get_vat_amount, type="float",
                                string="8% Base", method=True,
                                help="Vat Reduced Base Amount"),
        'get_vat_general_base': fields.function(_get_vat_amount, type="float",
                                string="12% Base", method=True,
                                help="Vat General Base Amount"),
        'get_vat_additional_base': fields.function(_get_vat_amount, type="float",
                                string="22% Base", method=True,
                                help="Vat Generald plus Additional Base Amount"),
        'get_vat_reduced_tax': fields.function(_get_vat_amount, type="float",
                                string="8% Tax", method=True,
                                help="Vat Reduced Tax Amount"),
        'get_vat_general_tax': fields.function(_get_vat_amount, type="float",
                                string="12% Tax", method=True,
                                help="Vat General Tax Amount"),
        'get_vat_additional_tax': fields.function(_get_vat_amount, type="float",
                                string="22% Tax", method=True,
                                help="Vat General plus Additional Tax Amount"),
    }

class fiscal_book_taxes(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Taxes"
    _name='fiscal.book.taxes'
    _rec_name='ait_id'
    _columns={
        'name':fields.related('ait_id', 'name', relation="account.invoice.tax",
                              type="char", string='Description', store=True),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this tax is related to'),
        'fbl_id':fields.many2one('fiscal.book.lines','Fiscal Book Lines',
            help='Fiscal Book Lines where this tax is related to'),
        'base_amount': fields.related('ait_id', 'base_amount',
                                      relation="account.invoice.tax", 
                                      type="float", string='Taxable Amount',
                                      help='Amount used as Taxing Base',
                                      store=True),
        'tax_amount': fields.related('ait_id', 'tax_amount',
                                     relation="account.invoice.tax",
                                     type="float", string='Taxed Amount',
                                     help='Taxed Amount on Taxing Base',
                                     store=True),
        'ait_id': fields.many2one('account.invoice.tax','Tax',
            help='Tax where is related to'),
    }

class fiscal_book_taxes_summary(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Taxes Summary"
    _name='fiscal.book.taxes.summary'

    _columns={
        'fb_id':fields.many2one('fiscal.book','Fiscal Book'),
        'tax_type': fields.selection([('exento', '0% Exento'), 
                                      ('sdcf', 'Not entitled to tax credit'), 
                                      ('general', 'General Aliquot'),
                                      ('reducido', 'Reducted Aliquot'),
                                      ('adicional', 'General Aliquot + Additional')],
                                     'Tax Type'),
        'base_amount_sum': fields.float('Taxable Amount Sum'),
        'tax_amount_sum': fields.float('Taxed Amount Sum'),
        'international': fields.boolean('International'),
    }

class adjustment_book_line(orm.Model):
    
    _name='adjustment.book.line'
    _columns={
        'date_accounting': fields.date('Date Accounting', required=True,
            help="Date accounting for adjustment book"),
        'date_admin': fields.date('Date Administrative',required=True, 
            help="Date administrative for adjustment book"),
        'vat':fields.char('Vat', size=10,required=True,
            help="Vat of partner for adjustment book"),
        'partner':fields.char('Partner', size=256,required=True,
            help="Partner for adjustment book"),
        'invoice_number':fields.char('Invoice Number', size=256,required=True,
            help="Invoice number for adjustment book"),
        'control_number':fields.char('Invoice Control', size=256,required=True,
            help="Invoice control for adjustment book"),        
        'amount':fields.float('Amount Document at Withholding VAT', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Amount document for adjustment book"),
        'type_doc': fields.selection([
            ('F','Invoice'),('ND', 'Debit Note'),('NC', 'Credit Note'),],
            'Document Type', select=True, required=True, 
            help="Type of Document for adjustment book: "\
                    " -Invoice(F),-Debit Note(dn),-Credit Note(cn)"),
        'doc_affected':fields.char('Affected Document', size=256,required=True,
            help="Affected Document for adjustment book"),
        'uncredit_fiscal':fields.float('Sin derecho a Credito Fiscal', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Sin derechoa credito fiscal"),
        'amount_untaxed_n': fields.float('Amount Untaxed', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Amount untaxed for national operations"),
        'percent_with_vat_n': fields.float('% Withholding VAT', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Percent(%) VAT for national operations"),
        'amount_with_vat_n': fields.float('Amount Withholding VAT', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Percent(%) VAT for national operations"),
        'amount_untaxed_i': fields.float('Amount Untaxed', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Amount untaxed for international operations"),
        'percent_with_vat_i': fields.float('% Withholding VAT', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Percent(%) VAT for international operations"),
        'amount_with_vat_i': fields.float('Amount Withholding VAT', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Amount withholding VAT for international operations"),
        'amount_with_vat': fields.float('Amount Withholding VAT Total', 
            digits_compute=dp.get_precision('Account'),required=True,
            help="Amount withheld VAT total"),
        'voucher': fields.char('Voucher Withholding VAT', size=256,
            required=True,help="Voucher Withholding VAT"),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
    }
    _rec_rame = 'partner'
    
