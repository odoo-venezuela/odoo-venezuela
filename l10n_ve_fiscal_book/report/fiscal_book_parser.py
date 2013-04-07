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

    _tax_types = ['8%', '12%', '22%']
    _taxes_cols_list = [
        'base-imponible',
        '%iva',
        'monto-impuesto',
    ]

    _purchase_cols_list = [
        'linea',
        'fecha-doc',
        'fecha-importada',
        't-doc',
        'rif',
        'razon-social',
        'comprobante',
        'planilla-importacion',
        'expediente-importacion',
        'numero-facutra',
        'numero-control',
        't-trans',
        'nota-de-debito-afectada',
        'nota-de-credito-afectada',
        'documento-afectado',
        #~ IMPORTACIONES
            'total-con-iva',
            'sdcf',
            'exento',
            #~ '_vat-reduced',
                'base-imponible',
                '%iva',
                'monto-impuesto',
            #~ '_vat-general',
                'base-imponible',
                '%iva',
                'monto-impuesto',
            #~ '_vat-additional',
                'base-imponible',
                '%iva',
                'monto-impuesto',
        #~ COMPRAS INTERNAS
            'total-con-iva',
            'sdcf',
            'exento',
            #~ '_vat-reduced',
                'base-imponible',
                '%iva',
                'monto-impuesto',
            #~ '_vat-general',
                'base-imponible',
                '%iva',
                'monto-impuesto',
            #~ '_vat-additional',
                'base-imponible',
                '%iva',
                'monto-impuesto',
     'retencion-iva',
    ]

    _purchase_macro_cols_list = [
        'generic-cols',
        'IMPORTACIONES',
        'COMPRAS INTERNAS',
        'last-cols',
    ]

    _cols = {
        'linea': {
            'name': 'Linea',
            'width': 15.0,
            'value': lambda fbl: fbl.rank,
            'help': '' },
        'fecha-doc': {
            'name': 'Fecha Doc.',
            'width': 23.0,
            'value': lambda fbl: fbl.get_date_invoiced,
            'help': '' },
        'fecha-importada': {
            'name': 'Fecha Importada',
            'width': 23.0,
            'value': lambda fbl: fbl.get_date_imported,
            'help': '' },
        't-doc': {
            'name': 'T. Doc.',
            'width': 15.0,
            'value': lambda fbl: fbl.get_t_doc,
            'help': '' },
        'rif': {
            'name': 'RIF',
            'width': 25.0,
            'value': lambda fbl: fbl.get_partner_vat,
            'help': '' },
        'razon-social': {
            'name': 'Razon Social',
            'width': 160.0,
            'value': lambda fbl: fbl.get_partner_name,
            'help': '' },
        'comprobante': {
            'name': 'Comprobante',
            'width': 40.0,
            'value': lambda fbl: (fbl.invoice_id and fbl.iwdl_id) and fbl.iwdl_id.retention_id.number or "NONE",
            #~ TODO: Make the new condition 'invoices will be print with their retetions if the retention and invoice date are the same'
            'help': '' },
        'planilla-importacion': {
            'name': 'Planilla de Importación',
            'width': 30.0,
            'value': lambda fbl: fbl.invoice_id.get_import_form,
            'help': '' },
        'expediente-importacion': {
            'name': 'Expediente de Importacion',
            'width': 36.0,
            'value': lambda fbl: fbl.invoice_id.import_spreadsheet_name,
            'help': '' },
        'numero-facutra': {
            'name': 'Número de Facutra',
            'width': 36.0,
            'value': lambda fbl: fbl.get_reference,
            'help': '' },
        'numero-control': {
            'name': 'Número Control',
            'width': 36.0,
            'value': lambda fbl: fbl.get_number,
            'help': '' },
        't-trans': {
            'name': 'T. Trans.',
            'width': 18.0,
            'value': lambda fbl: fbl.invoice_id.get_papel_anulado,
            'help': '' },
        'nota-de-debito-afectada': {
            'name': 'Nota de Debito Afectada',
            'width': 33.0,
            'value': lambda fbl: fbl.get_debit_affected,
            'help': '' },
        'nota-de-credito-afectada': {
            'name': 'Nota de Credito Afectada',
            'width': 33.0,
            'value': lambda fbl: fbl.get_credit_affected,
            'help': '' },
        'documento-afectado': {
            'name': 'Documento Afectado',
            'width': 33.0,
            'value': lambda fbl: fbl.get_parent,
            'help': '' },
        'total-con-iva': {
            'name': 'Total con Iva',
            'width': 37.0,
            'value': lambda fbl: fbl.invoice_id.get_is_imported and fbl.get_total or 0.0,
            'help': '' },
        'sdcf': {
            'name': 'SDCF',
            'width': 29.0,
            'value': lambda fbl: fbl.invoice_id.get_is_imported and fbl.get_v_sdcf or 0.0,
            'help': '' },
        'exento': {
            'name': 'Exento',
            'width': 29.0,
            'value': lambda fbl: fbl.invoice_id.get_is_imported and fbl.get_v_exent or 0.0,
            'help': '' },
        #~ taxes columns
        'base-imponible': {
            'name': 'Base Imponible',
            'width': 35.0,
            'value': lambda fbl: fbl.invoice_id.get_is_imported and my_tax.base_amount or 0.0,
            'help': '' },
        '%iva': {
            'name': '% IVA',
            'width': 15.0,
            'value': lambda fbl: fbl.invoice_id.get_is_imported and round(my_tax.tax_amount/(my_tax.base_amount and my_tax.base_amount or 1)*100.0) or 0.0,
            'help': '' },
        'monto-impuesto': {
            'name': 'Monto Impuesto',
            'width': 35.0,
            'value': lambda fbl: fbl.invoice_id.get_is_imported and my_tax.tax_amount or 0.0,
            'help': '' },
        'retencion-iva': {
            'name': 'Retencion IVA',
            'width': 40.0,
            'value': lambda fbl: fbl.get_withheld,
            'help': '' },
        #~ INNER TAX DATA
        '_vat-reduced': {
            'width': lambda self: self._get_tax_table_width(),
            'value': lambda fbl: 'Reduced VAT (8%)',
            'help': '' },
        '_vat-general': {
            'width': lambda self: self._get_tax_table_width(),
            'value': lambda fbl: 'General VAT (12%)',
            'help': '' },
        '_vat-additional': {
            'width': lambda self: self._get_tax_table_width(),
            'value': lambda fbl: 'Additional VAT (22%)',
            'help': '' },
    }

    def __init__(self, cr, uid, name, context):
        """ Initialization of the current instance."""
        super(fiscal_book_report, self).__init__(cr, uid, name, context)
        self._company_id = self.pool.get(
            'res.users').browse(self.cr, self.uid, uid).company_id.id

        self.localcontext.update({
            'time': time,
            'get_month': self._get_month,

            'get_attr_col_widths': self._get_attr_col_widths,
            'get_num_of_cols': self._get_num_of_cols,
            'get_col_name': self._get_col_name,
            'get_col_value': self._get_col_value,
            'get_col_width': self._get_col_width,

            #~ TODO: use this function after the bug for repeatIn arg3 is solve.
            'get_cols': self._get_cols,
        })

        self.cr = cr
        self.context = context
        self.uid = uid

        print '\n-----------------------------'
        print 'Number of columns', self._get_num_of_cols(),' + 1 at first'
        print 'Table width', self._get_table_width()
        print 'Colums widths'
        print [ self._get_col_width(col_name) for col_name in self._purchase_cols_list ]
        print '-----------------------------\n'

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

    def _get_attr_col_widths(self, context=None):
        """ It return string value for the blocktable colWidhts parameter."""
        context = context or {}
        res = '1.0, '
        for col_name in self._purchase_cols_list:
            res = res + str(self._get_col_width(col_name)) + ', '
        return  res[:-2]
        
    def _get_num_of_cols(self, context=None):
        """ It return the number of columns to display."""
        context = context or {}
        return len(self._purchase_cols_list)

    def _get_cols(self, context=None):
        """ It returns the list of ordered column names."""
        context = context or {}
        return self._purchase_cols_list

    def _get_col_name(self, col_number, context=None):
        """ It returns the column name related to col_number.
        @oaram col_number: position of the column in the _purchase_cols_list
        """
        context = context or {}
        return self._cols[self._purchase_cols_list[col_number-1]]['name']

    def _get_col_value(self, col_number, fbl_obj, context=None):
        """ It returns the column value related to col_number for the given
        fiscal book line.
        @oaram col_number: position of the column in the _purchase_cols_list
        @oaram fbl_obj: fiscal.book.line object
        """
        context = context or {}
        return self._cols[self._purchase_cols_list[col_number-1]]['value'](fbl_obj)

    def _get_col_width(self, col_name, context=None):
        """ It returns the column with related to col_number.
        @oaram col_number: position of the column in the _purchase_cols_list
        """
        context = context or {}
        return (col_name[0] == '_') \
                and self._cols[col_name]['width'](self) \
                or self._cols[col_name]['width']

    def _get_table_width(self, context=None):
        """ It returns the fiscal book table width."""
        context = context or {}
        return sum( [ self._get_col_width(col_name)
                      for col_name in self._purchase_cols_list ] )

    def _get_tax_table_width(self, context=None):
        """ It returns the tax columns group width."""
        context = context or {}
        return sum( [ self._get_col_width(col_name) \
                      for col_name in self._taxes_cols_list ] )

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
