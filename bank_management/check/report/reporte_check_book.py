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
#              Javier Duran              <javier.duran@netquatro.com>             
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
import time
from report import report_sxw
from osv import osv
import pooler

class rep_check_book(report_sxw.rml_parse):
 
    def __init__(self, cr, uid, name, context):
        super(rep_check_book, self).__init__(cr, uid, name, context) 
        self.suma_asigner = 0.00 
        self.suma_done = 0.00   
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_beneficiario':self.get_beneficiario,
            'get_close_date':self.get_close_date,
            'get_date_check':self.get_date_check,
            'get_amount_check':self.get_amount_check,
            'get_amount_asignado': self.get_amount_asignado ,
            'get_amount_done':self.get_amount_done,
            'get_state':self.get_state,
            'get_anulados':self.get_anulados,
            'get_estado':self.get_estado,
            'get_cancel':self.get_cancel,
        })
             
    def get_estado(self,state):
        res=""
        if state=="draft":
            res="Borrador"
        if state=="review":
            res="Revicion"
        if state=="active":
            res="Activo"
        if state=="hibernate":
            res="Hibernacion"
        if state=="cancel":
            res="Cancelado"
        if state=="assigned":
            res="Asignado"
        if state=="done":
            res="Cobrado"
        return res

    def get_cancel(self, cheque):
        res=""
        self_check_book=self.pool.get('check.note')
        data=self_check_book.browse(self.cr,self.uid, cheque)
        if data.cancel_check_note:
            if data.cancel_check_note=='otros':
                res=data.notes
                return res
            else: #fue otra de las razones
                if data.cancel_check_note=="print":
                    res="Error de Impresion"
                if data.cancel_check_note=="perdida":
                    res="Perdida o extravio"
                if data.cancel_check_note=="dan_fis":
                    res="Dano fisico"
                if data.cancel_check_note=="pago":
                    res="Pago no realizado"
                if data.cancel_check_note=="caduco":
                    res="Caduco"
                if data.cancel_check_note=="devuelto":
                    res="Cheque Devuelto"
                return res
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

    def get_beneficiario(self, idp):
        res=" - "
        check = self.pool.get('check.note') 
        check_note = check.browse(self.cr,self.uid, idp)
        if check_note.state=="assigned" or check_note.state=="done":
            if check_note.account_voucher_id.payee_id: #si hay beneficiario
                addr_obj = self.pool.get('res.partner.address') 
                addr = addr_obj.browse(self.cr,self.uid, check_note.account_voucher_id.payee_id.id)
                res=addr.name
            else: #el partner
                res=check_note.account_voucher_id.voucher_pay_support_id.partner_id.name
            return res
        else:
            return res

    def get_close_date(self, fecha,state):
        if state=="draft":
            res="Chequera en Borrador"
        if state=="review":
            res="Chequera en Revicion"
        if state=="active":
            res="Chequera Activa"
        if state=="hibernate":
            res="Chequera wn Hibernacion"
        if state=="cancel":
            res="Chequera Cancelada"
        if state=="done":
            res="Chequera Terminada"
        if len(fecha)==10:
            res=fecha 
            return res
        else:
            return res
        
    def get_state(self, state):
        if state=="draft":
            res="BORRADOR"
        if state=="review":
            res="REVICION"
        if state=="active":
            res="ACTIVADO"
        if state=="assigned":
            res="ASIGNADO"
        if state=="done":
            res="COBRADO"
        if state=="cancel":
            res="ANULADO"
        return res  

    def get_date_check(self, idp):
        res=" - "
        check = self.pool.get('check.note') 
        voucher_pay_support = self.pool.get('voucher.pay.support') 
        voucher_ids = voucher_pay_support.search(self.cr,self.uid,[('check_note_id','=',idp)])
        if voucher_ids:
            obj_v_p_s = voucher_pay_support.browse(self.cr,self.uid, voucher_ids[0])
            res=obj_v_p_s.date 
            return res
        else:
            return res
        
        
    def get_anulados(self, idp):
        res=" SIN ANULAR "
        check = self.pool.get('check.note') 
        voucher_ids = check.search(self.cr,self.uid,[('check_book_id','=',idp), ('state','=','cancel')])
        
        return len(voucher_ids)


    def get_amount_check(self, idp):
        res=" - "
        check = self.pool.get('check.note') 
        obj_check = check.browse(self.cr,self.uid, idp)
        voucher_pay_support = self.pool.get('voucher.pay.support') 
        voucher_ids = voucher_pay_support.search(self.cr,self.uid,[('check_note_id','=',idp)])
        if voucher_ids:
            obj_v_p_s = voucher_pay_support.browse(self.cr,self.uid, voucher_ids[0])
            res=obj_v_p_s.amount
            if obj_check.state=="assigned":
                self.suma_asigner=self.suma_asigner+obj_v_p_s.amount
            if obj_check.state=="done":
                self.suma_done=self.suma_done+obj_v_p_s.amount
            
            return res
        else:
            return res
        
    def get_amount_asignado(self):
        return self.suma_asigner
     
    def get_amount_done(self):
        return self.suma_done

report_sxw.report_sxw(
    'report.chk.book',
    'check.book',
    'addons/check_book/report/reporte_check_book.rml',
    parser=rep_check_book,
)
