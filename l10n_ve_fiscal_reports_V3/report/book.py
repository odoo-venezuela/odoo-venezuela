#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#    Planified by: Nhomar Hernandez
#############################################################################
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
##############################################################################

'''
Fiscal Report For Venezuela
'''

import time
from report import report_sxw
import pooler

class sal_book(report_sxw.rml_parse):
    '''
    Generates sales book
    '''

    def __init__(self, cr, uid, name, context):
        '''
        Reference to the current instance
        '''
        super(sal_book, self).__init__(cr, uid, name, context)    
        self._company_id = self.pool.get('res.users').browse(self.cr,self.uid,uid).company_id.id

        self.localcontext.update({
            'time': time,
            'get_data':self._get_data,
            'get_partner_addr': self._get_partner_addr,
            'get_p_country': self._get_p_country,
            'get_rif': self._get_rif,
            'get_month':self._get_month,
            'get_ret':self._get_ret,
            'get_data_adjustment': self._get_data_adjustment,
            'validation': self._validation,
            'get_data_wh': self._get_data_wh,
            'get_amount_withheld': self._get_amount_withheld,
            'get_date_wh': self._get_date_wh,
#            'get_v_sdcf': self._get_v_sdcf,
            'get_v_exent': self._get_v_exent,
            'get_tax_line': self._get_tax_line,
            'get_total_wh': self._get_total_wh,
            'get_total_iva': self._get_total_iva,
            'get_amount_untaxed_tax': self._get_amount_untaxed_tax,
#            'get_taxes': self._get_taxes,
            'get_wh_actual': self._get_wh_actual,
            'get_id': self._get_id,
#            'get_papel_anulado': self._get_papel_anulado,
        })

    def _get_partner_addr(self):
        '''
        Obtains the address of partner
        '''
        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr, self.uid, [('partner_id', '=', self._company_id), 
                                                     ('type', '=', 'invoice')])
        if addr_ids:
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+ \
                        (addr.zip or '')+ ' '+(addr.city or '')+ ' '+  \
                        (addr.country_id and addr.country_id.name or '')+  \
                        ', TELF.:'+(addr.phone or '')
        return addr_inv

    def _get_book_type(self,form):
        book_type=None
        book_type='fiscal.reports.sale'
        if form['type']=='purchase':
            book_type='fiscal.reports.purchase'
        
        return book_type

    def _get_p_country(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        a_id = 1000
        a_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if a_ids:
            a = addr_obj.browse(self.cr,self.uid, a_ids[0])
            a_id = a.country_id.id
        return a_id 

    def _get_book_type_wh(self, form):
        book_type=None
        book_type='fiscal.reports.whs'
        if form['type']=='purchase':
            book_type='fiscal.reports.whp'
        return book_type
        
    def _get_data(self, form):
        book_type=self._get_book_type(form)
        res = []
        fr_obj = self.pool.get('account.invoice')
        criteria = [('date_invoice', '<=', form['date_end']), 
                                ('date_invoice', '>=', form['date_start']),
                                ('state', 'in',[ 'done', 'paid', 'open']),
                                ('import_spreadsheet', '=', False),
                                ('company_id', '=', self._company_id)]
        if form['type'] == 'sale':
            criteria.append(('type', 'in', ['out_refund', 'out_invoice']))
        elif form['type'] == 'purchase':
            criteria.append(('type', 'in', ['in_refund', 'in_invoice']))
            
        fr_ids = fr_obj.search(self.cr, self.uid, 
                               criteria, order='date_invoice,nro_ctrl,number')
        if len(fr_ids)>0:
            res = fr_obj.browse(self.cr, self.uid, fr_ids)
            self._invs_ids = fr_ids
            self._data = res
        else:
            self._invs_ids = []
            self._data = []
        return res
        
    def _get_data_wh(self,form):
#        data=[]
#        d1=form['date_start']
#        d2=form['date_end']
#        fr_obj = self.pool.get('fiscal.reports.whs')
#        fr_ids = fr_obj.search(self.cr,self.uid,
#                                  [ ('ar_date_ret', '<=', d2), 
#                                    ('ar_date_ret', '>=',d1),
#                                    ('ar_date_document','<=',d1),
#                                    ('ai_company', '=', self._company_id)], order='ar_date_ret')
#        data = fr_obj.browse(self.cr,self.uid, fr_ids)


        data=[]
        d1=form['date_start']
        d2=form['date_end']
        fr_obj = self.pool.get('account.wh.iva')
        fr_ids = fr_obj.search(self.cr,self.uid,
                                  [ ('date_ret', '<=', d2), 
                                    ('date_ret', '>=',d1),
                                    ('date','<=',d1),
                                    ('state', '=', 'done'),
                                    ('wh_lines.invoice_id.type', 'in', ['out_invoice', 'out_refund']),
                                    ('wh_lines.invoice_id.company_id.id', '=', self._company_id)], order='ar_date_ret')
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data
        
    def _get_rif(self, vat=''):
        '''
        Get R.I.F.
        '''
        if not vat:
            return []
        return vat[2:].replace(' ', '')

    def _get_month(self, form):
        '''
        return year and month
        '''
        months=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        res = ['',0]
        res[0] = months[time.strptime(form['date_start'],"%Y-%m-%d")[1]-1]
        res[1] = time.strptime(form['date_start'],"%Y-%m-%d")[0]
        return res

    def _get_ret(self, form, inv_id):
        '''
            Ensure that Withholding date is inside period specified on form.
        '''
        d1=form['date_start']
        d2=form['date_end']
        wil_obj = self.pool.get('account.wh.iva.line')
        wil_ids= wil_obj.search(self.cr,self.uid,[('invoice_id', '=', inv_id)])
        wil_brw = wil_obj.browse(self.cr, self.uid, wil_ids)

        if form['type']=='purchase':
            return wil_brw[0].retention_id.number
            
        if wil_brw:
            if time.strptime(wil_brw[0].retention_id.date, '%Y-%m-%d') >= time.strptime(d1, '%Y-%m-%d') \
            and time.strptime(wil_brw[0].retention_id.date, '%Y-%m-%d') <=  time.strptime(d2, '%Y-%m-%d'):
                return wil_brw[0].retention_id.number
            else:
                return False
        else:
            return False

    def _get_date_wh(self,form, l):
        if l.ar_date_document> form['date_end']:
            return False
        return True

    def _get_data_adjustment(self,form):

        type_doc = 'sale'
        if form['type']=='purchase':
            type_doc = 'purchase'
        adjust_obj = self.pool.get('adjustment.book')
        adjust_line_obj = self.pool.get('adjustment.book.line')
        period_obj=self.pool.get('account.period')
        data=[]
        data_line=[]
        period_ids = period_obj.search(self.cr,self.uid,[('date_start','<=',form['date_start']),('date_stop','>=',form['date_end']), ('company_id', '=', self._company_id)])
        
        if len(period_ids)>0:
            fr_ids = adjust_obj.search(self.cr,self.uid,[('period_id', 'in',period_ids),('type','=',type_doc)])
            if len(fr_ids)>0:
                adj_ids = adjust_line_obj.search(self.cr,self.uid,[('adjustment_id','=',fr_ids[0])],order='date_admin')
                data = adjust_obj.browse(self.cr,self.uid, fr_ids)
                data_line = adjust_line_obj.browse(self.cr,self.uid, adj_ids)
        return (data,data_line)

    def _validation(self,form):
        type_doc = 'sale'
        if form['type']=='purchase':
            type_doc = 'purchase'
        period_obj=self.pool.get('account.period')
        adjust_obj = self.pool.get('adjustment.book')
        period_ids = period_obj.search(self.cr,self.uid,[('date_start','<=',form['date_start']),('date_stop','>=',form['date_end']), ('company_id', '=', self._company_id)])
        if len(period_ids)<=0:
            return False
        fr_ids = adjust_obj.search(self.cr,self.uid,[('period_id','in',period_ids),('type','=',type_doc)])
        if len(fr_ids)<=0:
            return False
        return True

    def _get_amount_withheld(self, form, inv):
        wil_obj = self.pool.get('account.wh.iva.line')
        wil_ids = wil_obj.search(self.cr, self.uid, [('invoice_id', '=', inv.id)])
        amount = 0.0
        if wil_ids:
            data = wil_obj.browse(self.cr, self.uid, wil_ids)[0]
            if data.retention_id:
                if data.retention_id.date_ret < form['date_end']:
                    if inv.type in ['in_refund', 'out_refund']:
                        amount = data.amount_tax_ret*(-1)
                    else:
                        amount = data.amount_tax_ret
                
#            get_date_wh(data['form'],l) 
#                and (get_ret(data['form'], l.id) 
#                    and (formatLang(((l.type in ['in_refund', 'out_refund']) 
#                        and (self.get_amount_withheld(l.ar_line_id.id)*(-1)) 
#                        or get_amount_withheld(l.ar_line_id.id)))) 
#                    or '') 
#                or ''
        return amount

    def _get_total_wh(self,form,actual=None):
        total=0
        for inv in self._data:
            amount = self._get_amount_withheld(form, inv)
            if amount:
                total+= amount
        return total

    def _get_total_iva(self,form):
        '''
        Return Amount Total of each invoice at Withholding Vat
        '''
        total = 0.0
        for i in self._data:
            if i.type in ['out_refund']:
                total += i.get_total*(-1.0)
            else:
                total += i.get_total
        return total

    def _get_amount_untaxed_tax(self, form, percent, nationality='', exempt=None):
        '''
        Return Amount Untaxed and Amount Tax, accorded percent of withholding vat
        '''
        amount_untaxed=0.0
        amount_tax=0.0

        for d in self._data:
            for tax in d.tax_line:
                if percent in tax.name:
                    if exempt is not None:
                        if d.partner_id.vat_subjected==exempt:
                            amount_untaxed+= self._get_amount_untaxed_tax2(d.type,tax)[0]
                            amount_tax+= self._get_amount_untaxed_tax2(d.type,tax)[1]
                    else:
                        if nationality == 'nacional' and not d.get_is_imported:
                            amount_untaxed+= self._get_amount_untaxed_tax2(d.type,tax)[0]
                            amount_tax+= self._get_amount_untaxed_tax2(d.type,tax)[1]
                        elif nationality == 'internacional' and d.get_is_imported:
                            amount_untaxed+= self._get_amount_untaxed_tax2(d.type,tax)[0]
                            amount_tax+= self._get_amount_untaxed_tax2(d.type,tax)[1]
                        elif nationality == 'all' or not nationality:
                            amount_untaxed+= self._get_amount_untaxed_tax2(d.type,tax)[0]
                            amount_tax+= self._get_amount_untaxed_tax2(d.type,tax)[1]
        return (amount_untaxed, amount_tax)

    def _get_wh_actual(self,form):
        total=0
        data=[]
        book_type= self._get_book_type_wh(form)
        fr_obj = self.pool.get('account.wh.iva')
        
#        fr_ids = fr_obj.search(self.cr,self.uid,
#                               [('date_ret', '<=', form['date_end']),
#                                ('date_ret', '>=', form['date_start']),
#                                ('wh_lines.invoice_id.date_invoice','>=',form['date_start']),
#                                ('wh_lines.invoice_id.date_invoice','<=',form['date_end']),
#                                ('wh_lines.invoice_id.company_id.id', '=', self._company_id)])
        fr_ids = fr_obj.search(self.cr,self.uid,
                               [('date_ret', '<=', form['date_end']),
                                ('date_ret', '>=', form['date_start']),
                                ('wh_lines.invoice_id.id','in',self._invs_ids)])
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        for wh in data:
            for wh_line in wh.wh_lines:
                if wh_line.invoice_id.type in ['in_refund', 'out_refund']:
                    total+= wh_line.amount_tax_ret * (-1)
                else:
                    total+= wh_line.amount_tax_ret
        return total

    def _get_id(self,form,idh,type=None):
        x=1
        ids =None
        
        if form['type']=='sale':
            ids = self._get_data_wh(form)
        if form['type']=='sale' and type:
            x+=len(ids)
        if type=='book':
            ids = self._get_data(form)

        for a in ids:
            if a.id != idh:
                x+=1
            else:
                return x
    
    def _get_tax_line(self,s):
        name = s.name
        cont = 0
        if name.find('SDCF')>=0:
            if cont==0:
                return 0
        else:
            cont = cont + 1
        return s.base_amount
    
    def _get_v_exent(self,l):
        amount = 0.0
        if not l:
            return 0.0
        for tax in l.tax_line:
            name=tax.name
            if name.find('EXENTO')>=0:
                amount = tax.base+amount
                if l.type in ['in_refund', 'out_refund']:
                    amount = amount * (-1)
        return (amount)

    def _get_amount_untaxed_tax2(self,type,tax):
        amount_untaxed=0.0
        amount_tax=0.0
        if type in ['in_refund', 'out_refund']:
            amount_untaxed= tax.base * (-1)
            amount_tax= tax.amount * (-1)
        else:
            amount_untaxed= tax.base
            amount_tax= tax.amount
        return [amount_untaxed,amount_tax]

report_sxw.report_sxw(
    'report.fiscal.reports.sale.sale_seniat_v3',
    'account.invoice',
    'addons/l10n_ve_fiscal_reports_V3/report/sales_book.rml',
    parser=sal_book,
    header=False
)      

report_sxw.report_sxw(
    'report.fiscal.reports.purchase.purchase_seniat_v3',
    'account.invoice',
    'addons/l10n_ve_fiscal_reports_V3/report/purchases_book.rml',
    parser=sal_book,
    header=False
)      

