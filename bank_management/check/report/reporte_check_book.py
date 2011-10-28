#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Angelica Barrios          <angelicaisabelb@gmail.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>             
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
import time
from report import report_sxw
import pooler
from tools.translate import _

class rep_check_book(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
        super(rep_check_book, self).__init__(cr, uid, name, context) 
        self.suma_asigner = 0.00 
        self.suma_done = 0.00   
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_beneficiario':self._get_beneficiario,
            'get_close_date':self._get_close_date,
            'get_date_check':self._get_date_check,
            'get_amount_check':self._get_amount_check,
            'get_amount_asignado': self._get_amount_asignado,
            'get_amount_done':self._get_amount_done,
            'get_anulados':self._get_anulados,
            'get_estado':self._get_estado,
            'get_cancel':self._get_cancel,
            'get_company':self._get_company,
            'get_rif':self._get_rif,
        })
             
    def _get_estado(self,state):
        estado = {
            'draft': _('Draft'),
            'review': _('Review'),
            'active': _('Active'),
            'hibernate': _('Hibernate'),
            'cancel': _('Cancel'),
            'assigned': _('Assigned'),
            'done': _('Done')
        
        }
        return estado[state]

    def _get_cancel(self, cheque):
        res=""
        can = {
            'print': _('Print Error'),
            'perdida':_('Loss or misplacement'),
            'dan_fis': _('Physical damage'),
            'pago':_('Payment is not made'),
            'caduco':_('Expired'),
            'devuelto':_('Returned check')
        }
        self_check_book=self.pool.get('check.note')
        data=self_check_book.browse(self.cr,self.uid, cheque)
        if data.cancel_check_note:
            if data.cancel_check_note=='otros':
                res=data.notes
                return res
            #fue otra de las razones
            res = can[data.cancel_check_note]
        return res

    def _get_partner_addr(self, idp=None):
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '---')
        return addr_inv 

    def _get_beneficiario(self, idp):
        res=" - "
        check = self.pool.get('check.note') 
        check_note = check.browse(self.cr,self.uid, idp)
        if check_note.state=="assigned" or check_note.state=="done":
            if check_note.account_voucher_id.payee_id: #si hay beneficiario
                res=check_note.account_voucher_id.payee_id.name
            else: #el partner
                res=check_note.account_voucher_id.voucher_pay_support_id.partner_id.name
        
        return res

    def _get_close_date(self, fecha,state):
        if len(fecha)==10:
            return fecha 
                
        chk_state = {
            'draft': _('Draft Check book'),
            'review': _('Review Check book'),
            'active': _('Active Check book'),
            'hibernate': _('Hibernate Check book'),
            'cancel': _('Cancel Check book'),
            'done': _('Done Check book')
        }
        return chk_state[state]


    def _get_date_check(self, idp):
        res=" - "
        check = self.pool.get('check.note') 
        voucher_pay_support = self.pool.get('voucher.pay.support') 
        voucher_ids = voucher_pay_support.search(self.cr,self.uid,[('check_note_id','=',idp)])
        if voucher_ids:
            obj_v_p_s = voucher_pay_support.browse(self.cr,self.uid, voucher_ids[0])
            res=obj_v_p_s.date 

        return res


    def _get_anulados(self, idp):
        check = self.pool.get('check.note') 
        voucher_ids = check.search(self.cr,self.uid,[('check_book_id','=',idp), ('state','=','cancel')])

        return len(voucher_ids)


    def _get_amount_check(self, idp):
        res=" - "
        check = self.pool.get('check.note') 
        obj_check = check.browse(self.cr,self.uid, idp)
        voucher_pay_support = self.pool.get('voucher.pay.support') 
        voucher_ids = voucher_pay_support.search(self.cr,self.uid,[('check_note_id','=',idp)])
        if voucher_ids:
            obj_v_p_s = voucher_pay_support.browse(self.cr,self.uid, voucher_ids[0])
            res=obj_v_p_s.amount
            if obj_check.state=="assigned":
                self.suma_asigner+=obj_v_p_s.amount
            if obj_check.state=="done":
                self.suma_done+= obj_v_p_s.amount

            return res
        else:
            return res

    def _get_amount_asignado(self):
        return self.suma_asigner
     
    def _get_amount_done(self):
        return self.suma_done


    def _get_company(self):
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        return user.company_id.partner_id.name

    def _get_rif(self):
        r = _('Without Vat')
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        rif=user.company_id.partner_id.vat or '' 
        r='%s-%s'%(rif[2:3],rif[3:-1])
        return r

report_sxw.report_sxw(
    'report.chk.book',
    'check.book',
    'addons/check_book/report/reporte_check_book.rml',
    parser=rep_check_book,
)
