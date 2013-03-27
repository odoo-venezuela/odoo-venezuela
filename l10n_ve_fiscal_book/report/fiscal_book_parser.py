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
            'get_tax_line': self._get_tax_line,
            'get_month': self._get_month,
            'get_tax_line': self._get_tax_line,
        })

        self.cr = cr
        self.context = context
        self.uid = uid

    def _get_tax_line(self, fbl_tax):
        name = fbl_tax.ait_id.name
        cont = 0
        if name.find('SDCF')>=0:
            if cont==0:
                return 0
        else:
            cont = cont + 1
        return fbl_tax.ait_id.base_amount

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
