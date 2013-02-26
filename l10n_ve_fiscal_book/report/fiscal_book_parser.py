#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by:       Katherine Zaoral <katherine-zaoral@vauxoo.com>
#    Planified by: Humberto Arocha
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import time
from openerp.report import report_sxw
import openerp.pooler


class fiscal_book_report(report_sxw.rml_parse):

    #~ _description = '''Fiscal Book for Venezuela'''

    def __init__(self, cr, uid, name, context):
        """
        Reference to the current instance.
        """
        super(fiscal_book_report, self).__init__(cr, uid, name, context)
        self._company_id = self.pool.get(
            'res.users').browse(self.cr, self.uid, uid).company_id.id

        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_tax_line': self._get_tax_line,
            'get_amount_withheld': self._get_amount_withheld,
            'get_month': self._get_month,
            'get_ret': self._get_ret,
            'get_tax_line': self._get_tax_line,
        })

        self.cr = cr
        self.context = context
        self.uid = uid

    def _get_partner_addr(self):
        """
        Obtains printable formated partner address
        """
        addr_obj = self.pool.get('res.partner')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        if self._company_id:
            addr = addr_obj.browse(self.cr,self.uid, self._company_id)
            addr_inv = addr.type == 'invoice' and (addr.street or '') + ' ' + \
            (addr.street2 or '') + ' ' + (addr.zip or '') + ' ' + \
            (addr.city or '') + ' ' + \
            (addr.country_id and addr.country_id.name or '')+ ', TELF.:' + \
            (addr.phone or '') or 'NO HAY DIRECCION FISCAL DEFINIDA'
        return addr_inv

    def _get_tax_line(self, fbl_tax):
        name = fbl_tax.ait_id.name
        cont = 0
        if name.find('SDCF')>=0:
            if cont==0:
                return 0
        else:
            cont = cont + 1
        return fbl_tax.ait_id.base_amount

    #~ TODO: This function is not over... im checking, have to test...
    #~ data is a empty list when their are 'awil_ids' check why
    def _get_amount_withheld(self, book_line):
        """
        Return the amount withheld.
        """
        amount = 0.0
        date_end = book_line.fb_id.period_id.date_stop

        awil_obj = self.pool.get('account.wh.iva.line')
        awil_ids = awil_obj.search(self.cr, self.uid, \
            [('invoice_id', '=', book_line.invoice_id.id)])
        if awil_ids:
            data = awil_obj.browse(self.cr, self.uid, awil_ids)            
            data = data[0]

            if data.retention_id:
                if data.retention_id.date_ret < date_end:
                    if inv.type in ['in_refund', 'out_refund']:
                        amount = data.amount_tax_ret*(-1)
                    else:
                        amount = data.amount_tax_ret

        return amount

    #~ TODO: run...
    def _get_ret(self, fbook, book_line):
        """
        Ensure that Withholding date is inside period specified on form.
        """
        d1= fbook.period_id.date_start
        d2= fbook.period_id.date_stop

        #~ TODO: no me parece.. no deberia ser una referencia a account.wh.iva?
        wil_obj = self.pool.get('account.wh.iva.line')
        wil_ids= wil_obj.search(self.cr, self.uid, [
            ('invoice_id', '=', book_line.invoice_id.id)])
        wil_brw = wil_obj.browse(self.cr, self.uid, wil_ids)

        if fbook.type =='purchase':
            return wil_brw and wil_brw[0].retention_id.number or False

        if wil_brw:
            if time.strptime(wil_brw[0].retention_id.date, '%Y-%m-%d') \
            >= time.strptime(d1, '%Y-%m-%d') \
            and time.strptime(wil_brw[0].retention_id.date, '%Y-%m-%d') \
            <= time.strptime(d2, '%Y-%m-%d'):
                return wil_brw[0].retention_id.number
            else:
                return False
        else:
            return False

    def _get_month(self, fb):
        """
        Return an array with the year and month of the fiscal book period.
        """
        months=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
            "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        res = ['',0]
        res[0] = months[time.strptime(fb.period_id.date_start,"%Y-%m-%d")[1]-1]
        res[1] = time.strptime(fb.period_id.date_start,"%Y-%m-%d")[0]
        return res

    def _get_tax_line(self, tax):
        name = tax.name
        cont = 0
        if name.find('SDCF')>=0:
            if cont==0:
                return 0
        else:
            cont = cont + 1
        return tax.base_amount

report_sxw.report_sxw(
    'report.fiscal.book.sale',
    'fiscal.book',
    'l10n_ve_fiscal_book/report/fiscal_book_sale_report.rml',
    parser=fiscal_book_report,
    header=False
)

report_sxw.report_sxw(
    'report.fiscal.book.purchase',
    'fiscal.book',
    'l10n_ve_fiscal_book/report/fiscal_book_purchase_report.rml',
    parser=fiscal_book_report,
    header=False
)
