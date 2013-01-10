#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
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
from  openerp.osv import orm, fields
from tools.translate import _
import decimal_precision as dp

class fiscal_book(orm.Model):

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        context = context or {}
        res = {}
        for adj in self.browse(cr,uid,ids,context):
            res[adj.id] = {
                'amount_total': 0.0,
                'amount_untaxed_n_total' : 0.0,
                'amount_with_vat_n_total': 0.0,
                'amount_untaxed_i_total' : 0.0,
                'amount_with_vat_i_total': 0.0,
                'uncredit_fiscal_total'  : 0.0,
                'amount_with_vat_total'  : 0.0,
                'amount_base_total'  : 0.0,
                'amount_percent_total'  : 0.0,
            }
            for line in adj.abl_ids:
                res[adj.id]['amount_total'] += line.amount
                res[adj.id]['amount_untaxed_n_total'] += line.amount_untaxed_n
                res[adj.id]['amount_with_vat_n_total'] += line.amount_with_vat_n
                res[adj.id]['amount_untaxed_i_total'] += line.amount_untaxed_i
                res[adj.id]['amount_with_vat_i_total'] += line.amount_with_vat_i
                res[adj.id]['uncredit_fiscal_total'] += line.uncredit_fiscal
                res[adj.id]['amount_with_vat_total'] += line.amount_with_vat
            res[adj.id]['amount_base_total'] += adj.vat_general_i+ \
                    adj.vat_general_add_i+adj.vat_reduced_i+adj.vat_general_n+\
                    adj.vat_general_add_n+adj.vat_reduced_n+adj.adjustment+ \
                    adj.no_grav+adj.sale_export
            res[adj.id]['amount_percent_total'] += adj.vat_general_icf+ \
                    adj.vat_general_add_icf+adj.vat_reduced_icf+ \
                    adj.vat_general_ncf + adj.vat_general_add_ncf + \
                    adj.vat_reduced_ncf+adj.adjustment_cf+adj.sale_export_cf
        return res

    def _get_type(self, cr, uid, context=None):
        context = context or {}
        return context.get('type', 'purchase')

    _description = "Venezuela's Sale & Purchase Fiscal Books"
    _name='fiscal.book'
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
        'invoice_ids':fields.one2many('account.invoice', 'fb_id', 'Invoices',
            help='Invoices being recorded in a Fiscal Book'),
        'iwdl_ids':fields.one2many('account.wh.iva.line', 'fb_id', 'Vat Withholdings',
            help='Vat Withholdings being recorded in a Fiscal Book'),
        'abl_ids':fields.one2many('adjustment.book.line', 'fb_id', 'Adjustment Lines',
            help='Adjustment Lines being recorded in a Fiscal Book'),
        'note': fields.text('Note',required=True),
        'amount_total':fields.function(_get_amount_total,multi='all',method=True, 
            digits_compute=dp.get_precision('Account'),
            string='Amount Total Withholding VAT',readonly=True,
            help="Amount Total for adjustment book of invoice"),
        'amount_untaxed_n_total':fields.function(_get_amount_total,multi='all',
            method=True, digits_compute=dp.get_precision('Account'),
            string='Amount Untaxed National',readonly=True,
            help="Amount Total Untaxed for adjustment book of nacional operations"),
        'amount_with_vat_n_total':fields.function(_get_amount_total,multi='all',
            method=True, digits_compute=dp.get_precision('Account'),
            string='Amount Withheld National',readonly=True,
            help="Amount Total Withheld for adjustment book of national operations"),
        'amount_untaxed_i_total':fields.function(_get_amount_total,multi='all',
            method=True, digits_compute=dp.get_precision('Account'),
            string='Amount Untaxed International',readonly=True,
            help="Amount Total Untaxed for adjustment book of internacional operations"),
        'amount_with_vat_i_total':fields.function(_get_amount_total,multi='all',
            method=True, digits_compute=dp.get_precision('Account'),
            string='Amount Withheld International',readonly=True,
            help="Amount Total Withheld for adjustment book of international operations"),
        'uncredit_fiscal_total':fields.function(_get_amount_total,multi='all',
            method=True, digits_compute=dp.get_precision('Account'),
            string='Sin derecho a credito fiscal',readonly=True,
            help="Sin derecho a credito fiscal"),
        'amount_with_vat_total':fields.function(_get_amount_total,multi='all',
            method=True, digits_compute=dp.get_precision('Account'),
            string='Amount Withholding VAT Total',readonly=True,
            help="Amount Total Withholding VAT for adjustment book"),
        'no_grav': fields.float('Compras/Ventas no Gravadas y/o SDCF',  
                digits_compute=dp.get_precision('Account'),
                help="Compras/Ventas no gravadas y/o sin derecho a credito "\
                        "fiscal/ Ventas Internas no grabadas"),
        'vat_general_i': fields.float('Alicuota general',  
                digits_compute=dp.get_precision('Account'), 
                help="Importaciones gravadas por alicuota general"),
        'vat_general_add_i':fields.float('Alicuota general + Alicuota adicional',  
                digits_compute=dp.get_precision('Account'),
                help="Importaciones gravadas por alicuota general mas alicuota adicional"),
        'vat_reduced_i': fields.float('Alicuota Reducida',  
                digits_compute=dp.get_precision('Account'),
                help="Importaciones gravadas por alicuota reducida"),
        'vat_general_n': fields.float('Alicuota general',  
                digits_compute=dp.get_precision('Account'),
                help="Compras gravadas por alicuota general/Ventas internas "\
                        "gravadas por alicuota general"),
        'vat_general_add_n': fields.float('Alicuota general + Alicuota adicional',  
                digits_compute=dp.get_precision('Account'),
                help="Compras/Ventas internas gravadas por alicuota general "\
                        "mas alicuota adicional"),
        'vat_reduced_n': fields.float('Alicuota Reducida',  
                digits_compute=dp.get_precision('Account'),
                help="Compras/Ventas Internas gravadas por alicuota reducida"),
        'adjustment': fields.float('Ajustes',  
                digits_compute=dp.get_precision('Account'),
                help="Ajustes a los creditos/debitos fiscales de los periodos anteriores"),
        'vat_general_icf': fields.float('Alicuota general',  
                digits_compute=dp.get_precision('Account'), 
                help="Importaciones gravadas por alicuota general"),
        'vat_general_add_icf': fields.float('Alicuota general + Alicuota adicional',  
                digits_compute=dp.get_precision('Account'),
                help="Importaciones gravadas por alicuota general mas alicuota adicional"),
        'vat_reduced_icf': fields.float('Alicuota Reducida',  
                digits_compute=dp.get_precision('Account'),
                help="Importaciones gravadas por alicuota reducida"),
        'vat_general_ncf': fields.float('Alicuota general',  
                digits_compute=dp.get_precision('Account'),
                help="Compras gravadas por alicuota general/Ventas internas "\
                        "gravadas por alicuota general"),
        'vat_general_add_ncf': fields.float('Alicuota general + Alicuota adicional',  
                digits_compute=dp.get_precision('Account'),
                help="Compras/Ventas internas gravadas por alicuota general "\
                        "mas alicuota adicional"),
        'vat_reduced_ncf': fields.float('Alicuota Reducida',  
                digits_compute=dp.get_precision('Account'),
                help="Compras/Ventas Internas gravadas por alicuota reducida"),
        'adjustment_cf': fields.float('Ajustes',  
                digits_compute=dp.get_precision('Account'),
                help="Ajustes a los creditos/debitos fiscales de los periodos anteriores"),
        'amount_base_total':fields.function(_get_amount_total,multi='all',
                method=True, digits_compute=dp.get_precision('Account'),
                string='Total Base Imponible',readonly=True,
                help="TOTAL COMPRAS DEL PERIODO/TOTAL VENTAS PARA EFECTOS DE DETERMINACION"),
        'amount_percent_total':fields.function(_get_amount_total,multi='all',
                method=True, digits_compute=dp.get_precision('Account'),
                string='Total % Fiscal',readonly=True,help="TOTALCREDITOS FISCALES "\
                "DEL PERIODO/TOTAL DEBITOS FISCALES PARA EFECTOS DE DETERMINACION"),
        'sale_export':fields.float('Ventas de Exportacion',  
                digits_compute=dp.get_precision('Account'),
                help="Ventas de Exportacion"),
        'sale_export_cf':fields.float('Ventas de Exportacion',  
                digits_compute=dp.get_precision('Account'),
                help="Ventas de Exportacion"),
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

    _description = "Venezuela's Sale & Purchase Fiscal Book Lines"
    _name='fiscal.book.lines'
    _rec_name='rank'
    _columns={
        'rank':fields.integer('Line Position', required=True),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        'invoice_id':fields.many2one('fiscal.book','Invoice',
            help='Fiscal Book where this line is related to'),
        'iwdl_id':fields.many2one('account.wh.iva.line','Vat Withholding',
            help='Fiscal Book where this line is related to'),
        'get_date_imported':fields.related('invoice_id','get_date_imported',
            string='Imported Date',help=''),
        'get_date_invoiced':fields.related('invoice_id','get_date_invoiced',
            string='Invoiced Date',help=''),
        'get_t_doc':fields.related('invoice_id','get_t_doc',
            string='Doc. Type',help=''),
        'get_partner_vat':fields.related('invoice_id','get_partner_vat',
            string='Partner vat',help=''),
        'get_partner_name':fields.related('invoice_id','get_partner_name',
            string='Partner Name',help=''),
        'get_reference':fields.related('invoice_id','get_reference',
            string='Invoice number',help=''),
        'get_number':fields.related('invoice_id','get_number',
            string='Control number',help=''),
        'get_doc':fields.related('invoice_id','get_doc',
            string='Trans. Type',help=''),
        'get_debit_affected':fields.related('invoice_id','get_debit_affected',
            string='Affected Debit Notes',help=''),
        'get_credit_affected':fields.related('invoice_id','get_credit_affected',
            string='Affected Credit Notes',help=''),
        'get_parent':fields.related('invoice_id','get_parent',
            string='Affected Document',help=''),
    }

class fiscal_book_taxes(orm.Model):

    _description = "Venezuela's Sale & Purchase Fiscal Book Lines"
    _name='fiscal.book.taxes'
    _columns={
        'name':fields.char('Description', size=256, required=True),
        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        'base_amount':fields.float('Taxable Amount',help='Amount used as Taxing Base'),
        'tax_amount':fields.float('Taxed Amount',help='Taxed Amount on Taxing Base'),
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
    
