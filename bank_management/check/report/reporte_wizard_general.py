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
import datetime
from mx.DateTime import *


class rep_check_general(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rep_check_general, self).__init__(cr, uid, name, context)  
        self.suma_asigner = 0.00 
        self.suma_done = 0.00     
        self.localcontext.update({
            'time': time                                           ,
            'get_data':self.get_data                               ,
            'get_close_date':self.get_close_date                   ,
            'get_anulados':self.get_anulados                       ,
            'get_date_check':self.get_date_check                   ,
            'get_beneficiario':self.get_beneficiario               ,
            'get_amount_check':self.get_amount_check               ,
            'get_amount_asignado': self.get_amount_asignado        ,
            'get_amount_done':self.get_amount_done                 ,
            'get_amount_asignado_par':self.get_amount_asignado_par ,
            'get_check_note':self.get_check_note                   ,
            'get_estado':self.get_estado                           ,
            'get_cancel':self.get_cancel                           ,
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
    
    
    def get_data (self,form):
        data=[]
        #se toman los valores del wizard
        state_check_note=form["state_check_note"]
        tiempo=form["tiempo"]
        mes=form["mes"]
        hasta=form["hasta"]
        desde=form["desde"]
#        check=form['check_book_id']
#        check_book_id=check[0][2]
        check_book_id=form.get('check_book_id',False) and [form['check_book_id']]
        self_check_book=self.pool.get('check.book')
#        if len(check_book_id)==0: #si no elije chequeras, se reportan todas...
        if not check_book_id:
            check_book_id=self_check_book.search(self.cr,self.uid,[])
        data=self_check_book.browse(self.cr,self.uid, check_book_id)
        return data
    
    
    
    def get_check_note (self,form,chequera):
        cheques=[]
        #se toman los valores del wizard
        state_check_note=form["state_check_note"]
        tiempo=form["tiempo"]
        mes=form["mes"]
        hasta=form["hasta"]
        desde=form["desde"]
#        check=form['check_book_id']
#        check_book_id=check[0][2]
        self_check_note=self.pool.get('check.note')
        self_fiscal_per = self.pool.get('account.period')
        if state_check_note=="sin_filtro":
            cheques=chequera.check_note_ids #todos los cheques de la chequera
        else:
            if state_check_note=="cobrado": #cheques en estado done
                if tiempo=="mes": #Periodo Fiscal
                    periodo=self_fiscal_per.browse(self.cr,self.uid, mes)
                    check_note_id = self_check_note.search(self.cr, self.uid, 
                                                            [ ('state','=','done')                      , 
                                                              ('check_book_id','=',chequera.id)         ,
                                                              ('date_done' , '>=', periodo.date_start)  ,
                                                              ('date_done', '<=',periodo.date_stop )    ,])
                    cheques=self_check_note.browse(self.cr,self.uid, check_note_id)
                
                else: #si elijio fecha desde hasta
                    check_note_id = self_check_note.search(self.cr, self.uid, 
                                                            [ ('state','=','done')               , 
                                                              ('check_book_id','=',chequera.id)  ,
                                                              ('date_done' , '>=', desde)        ,
                                                              ('date_done', '<=',hasta )         ,])
                    cheques=self_check_note.browse(self.cr,self.uid, check_note_id)  
                
            else: #cheques con estado assigned "emitidos"
                if tiempo=="mes": #Periodo Fiscal
                    periodo=self_fiscal_per.browse(self.cr,self.uid, mes)
                    self_voucher_pay_support = self.pool.get('voucher.pay.support') 
                    voucher_ids= self_voucher_pay_support.search(self.cr, self.uid, 
                                                            [ ('date' , '>=', periodo.date_start)   ,
                                                              ('date', '<=',periodo.date_stop )     ,])
                    voucher_obj=self_voucher_pay_support.browse(self.cr,self.uid,voucher_ids)
                    check=[]
                    for vou in voucher_obj:
                        id_cheque=vou.check_note_id.id
                        check.append(id_cheque)
                    check_note_id=self_check_note.search(self.cr,self.uid,
                                                            [ ('state','=','assigned')            ,
                                                              ('check_book_id','=',chequera.id)  ,  ])
                    #saco los cheques en comun entre check_note_id y check (los de voucher_pay_support)
                    sin_repetir=list(set(check)&set(check_note_id))
                    cheques=self_check_note.browse(self.cr,self.uid, sin_repetir) 
                    
                else: #si elijio fecha desde hasta
                    self_voucher_pay_support = self.pool.get('voucher.pay.support') 
                    voucher_ids= self_voucher_pay_support.search(self.cr, self.uid, 
                                                            [ ('date' , '>=', desde)   ,
                                                              ('date', '<=',hasta )     ,])
                    voucher_obj=self_voucher_pay_support.browse(self.cr,self.uid,voucher_ids)
                    check=[]
                    for vou in voucher_obj:
                        id_cheque=vou.check_note_id.id
                        check.append(id_cheque)
                    check_note_id=self_check_note.search(self.cr,self.uid,
                                                            [ ('state','=','assigned')            ,
                                                              ('check_book_id','=',chequera.id)  ,  ])
                    #saco los cheques en comun entre check_note_id y check (los de voucher_pay_support)
                    sin_repetir=list(set(check)&set(check_note_id))
                    cheques=self_check_note.browse(self.cr,self.uid, sin_repetir) 
        return cheques



    def get_close_date(self, fecha,state):
        if fecha==False:
            if state=="draft":
                res="Chequera en Borrador"
            if state=="review":
                res="Chequera en Revicion"
            if state=="active":
                res="Chequera Activa"
            if state=="hibernate":
                res="Chequera en Hibernacion"
            if state=="cancel":
                res="Chequera Cancelada"
            if state=="done":
                res="Chequera Terminada"
            return res
        else:
            if len(fecha)==10:
                res=fecha 
                return res
              
        
    def get_anulados(self, idp):
        res=" SIN ANULAR "
        check = self.pool.get('check.note') 
        voucher_ids = check.search(self.cr,self.uid,[('check_book_id','=',idp), ('state','=','cancel')])
        
        return len(voucher_ids)
   


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
   
    
    def get_amount_asignado_par(self, id_chequera):
        amount=0.0
        amount2=0.0
        res=[]
        check = self.pool.get('check.note').search(self.cr,self.uid,[('check_book_id','=',id_chequera),('state','=','assigned') ])
        check2 = self.pool.get('check.note').search(self.cr,self.uid,[('check_book_id','=',id_chequera),('state','=','done') ])
        voucher = self.pool.get('voucher.pay.support')
        for i in check:
            voucher_id=voucher.search(self.cr,self.uid,[('check_note_id','=',i)])
            if voucher_id:
                voucher_brow=voucher.browse(self.cr,self.uid, voucher_id[0])
                amount=amount+voucher_brow.amount
        for i in check2:
            voucher_id=voucher.search(self.cr,self.uid,[('check_note_id','=',i)])
            if voucher_id:
                voucher_brow=voucher.browse(self.cr,self.uid, voucher_id[0])
                amount2=amount2+voucher_brow.amount
        res=[amount, amount2]
        return res

report_sxw.report_sxw(
    'report.wizard.general.book',
    'check.book.wizard',
    'addons/bank_management/check/report/reporte_wizard_general.rml', 
    parser=rep_check_general,
    header = False
)      
