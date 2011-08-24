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
from numero_a_texto import Numero_a_Texto

class rep_check_book_request(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rep_check_book_request, self).__init__(cr, uid, name, context)  
        self.localcontext.update({
            'time': time,
            'get_fecha': self.get_fecha                         ,
            'get_banco':self.get_banco                          ,
            'get_total':self.get_total                          ,
            'get_cantidad_chequera':self.get_cantidad_chequera  ,
            'get_beneficiario':self.get_beneficiario            ,

        })

    def get_fecha(self):
        fecha= time.strftime('%Y-%m-%d')
        dia=fecha[8:10]
        mes=fecha[5:7]
        ano=fecha[0:4]
        if mes=="01":
            m="Enero"
        if mes=="02":
            m="Febrero"
        if mes=="03":
            m="Marzo"
        if mes=="04":
            m="Abril"
        if mes=="05":
            m="Mayo"
        if mes=="06":
            m="Junio"
        if mes=="07":
            m="Julio"
        if mes=="08":
            m="Agosto"
        if mes=="09":
            m="Septiembre"
        if mes=="10":
            m="Octubre"
        if mes=="11":
            m="Noviembre"
        if mes=="12":
            m="Diciembre"
        res="Caracas, %s de %s de %s "%(dia, m , ano)
        return res

    def get_banco(self, cuenta):
        banco=cuenta.bank.name
        agencia=cuenta.name
        cuenta=cuenta.acc_number
        res=[banco,agencia,cuenta]
        return res
    
    def get_total(self, id_request):
        numero=0
        self.cr.execute("SELECT COUNT(a.id)  FROM check_book a   WHERE a.check_book_request_id=%s"%(id_request))
        value=self.cr.fetchone()
        if value:
            numero=value[0] 
            txt=Numero_a_Texto(numero)
            res=[numero,txt]
        return res
    
    def get_cantidad_chequera(self, id_request):
        total=[]
        check = self.pool.get('check.book.request') 
        check_book = check.browse(self.cr,self.uid, id_request)
        for i in check_book.check_book_ids:
            total.append(i.qty_check)
        res=""
        contador=1
        for cantidad in total:
            txt=Numero_a_Texto(cantidad)
            nun=cantidad
            if contador==len(total) and contador!=1: #para el ultimo elemento se coloca el y
                res= res +''' y %s (%s)'''%(txt,nun)
                res=res.lower()
            else:
                if len(total)>=3 and contador!=(len(total)-1): #esto es para poner las comas (,) si es mayor a 3 y no es la antepenultima
                    res= res +'''%s (%s), '''%(txt,nun)
                    res=res.title()
                else: #no se coloca la (,)
                    res= res +'''%s (%s)'''%(txt,nun)
                    res=res.lower()
            
            contador=contador+1
        return res
    
    
    def get_beneficiario(self, partner_id):
        bene=partner_id.name
        rif=partner_id.vat
        #VEV111234456 pasa a ser: V-11123445
        r='%s-%s'%(rif[2:3],int(rif[3:-1]))
        res=[bene,r]
        return res

report_sxw.report_sxw(
    'report.reporte.check.book.request'                                ,
    'check.book.request'                                               ,
    'addons/check_book_request/report/report_request_check_book.rml'   ,
    parser=rep_check_book_request                                      ,
)      
