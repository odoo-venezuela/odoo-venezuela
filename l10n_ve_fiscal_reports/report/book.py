# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

'''
Fiscal Report For Venezuela
'''

import time
from report import report_sxw
from osv import osv
import pooler

class pur_sal_book(report_sxw.rml_parse):
    '''
    Book generates purchase and sale
    '''

    def __init__(self, cr, uid, name, context):
        '''
        Reference to the current instance
        '''
        super(pur_sal_book, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_alicuota': self._get_alicuota,
            'get_rif': self._get_rif,
            'get_data':self._get_data,
            'get_month':self._get_month,
            'get_dates':self._get_dates,
        })

    def _get_partner_addr(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv 


    def _get_alicuota(self, tnom=None):
        '''
        Get Aliquot
        '''
        if not tnom:
            return []

        tax_obj = self.pool.get('account.tax')
        tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])[0]
        tax = tax_obj.browse(self.cr,self.uid, tax_ids)

        return tax.amount*100


    def _get_rif(self, vat=''):
        '''
        Get R.I.F.
        '''
        if not vat:
            return []
        return vat[2:].replace(' ', '')


    def _get_data(self,form):
        '''
        Get Data
        '''
        d1=form['date_start']
        d2=form['date_end']
        data=[]
        book_type='fiscal.reports.purchase'

        fr_obj = self.pool.get(book_type)
        fr_ids = fr_obj.search(self.cr,self.uid,[('ai_date_invoice', '<=', d2), ('ai_date_invoice', '>=', d1)])
        data = fr_obj.browse(self.cr,self.uid, fr_ids)
        return data

    def _get_month(self, form):
        '''
        Get Month
        '''
        months=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        res = months[time.strptime(form['date_start'],"%Y-%m-%d")[1]-1]
        return res
        
    def _get_dates(self, form):
        '''
        Get Dates
        '''
        res=[]
        res.append(form['date_start'])
        res.append(form['date_end'])
        return res
      
report_sxw.report_sxw(
    'report.fiscal.reports.purchase.purchase_seniat',
    'fiscal.reports.purchase',
    'addons/l10n_ve_fiscal_reports/report/book_seniat.rml',
    parser=pur_sal_book,
    header=False
)      
