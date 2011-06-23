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
import wizard
import osv
import pooler
import time

_transaction_form = '''<?xml version="1.0"?>
    <form string="Reporte General de Chequeras" >
       <group colspan="4" col='4'>
            <field name="check_book_id" widget="many2many"  nolabel="1"/>
       </group>
        <group colspan="4">
            <separator string="Periodo" colspan="4"/>
            
            <field name="state_check_note"/>
            <newline/>
            
            <group attrs="{'invisible':[('state_check_note','=','sin_filtro')]}" colspan="4">
                <field name="tiempo"/>
                <newline/>
                <group attrs="{'invisible':[('tiempo','=','sin_filtro')]}" colspan="4">
                    <group attrs="{'invisible':[('tiempo','=','mes')]}" colspan="4">
                        <separator string=" Filtrado por Fecha" colspan="4"/>
                        <field name="desde"/>
                        <field name="hasta"/>
                    </group>
                    <group attrs="{'invisible':[('tiempo','=','fecha')]}" colspan="4">
                        <separator string="Filtrado por Periodos" colspan="4"/>
                        <field name="mes" colspan="4" nolabel="1"/>
                    </group>
                </group>
            </group>
            
        </group>
    </form>'''

_transaction_fields = {
    'check_book_id': {
        'string': 'Chequeras'               ,
        'type': 'many2one'                  ,
        'relation': 'check.book'            ,
        'required': False                   ,
      }                                            ,
      
    'state_check_note': {
        'string': 'Estado del Cheque'        ,
        'type': 'selection'                  ,
        'selection': [
            ('sin_filtro','Sin Filtro')      ,
            ('cobrado','Cobrado')            ,
            ('emitido','Emitido')            ,
            ]                                ,
        'required': False                    ,
        'default': lambda *a:'sin_filtro'    ,
      }                                            ,

    'tiempo': {
        'string': 'Tiempo'                   ,
        'type': 'selection'                  ,
        'selection':[
            ('mes','Periodo Fiscal')         ,
            ('fecha','Fecha')                ,
            ]                                ,
         'required': False                   ,  
         'default': lambda *a:'mes'   ,     
      }                                            ,
      
    'desde': {
        'string': 'Desde'                    ,
        'type': 'date'                       ,
        'required': False                    ,
      }                                            ,
     
    'hasta': {
        'string': 'Hasta'                    ,
        'type': 'date'                       ,
        'required': False                    ,
       }                                           ,     

    'mes': {
        'string': 'Mes Fiscal'               ,
        'type': 'many2one'                   ,
        'relation': 'account.period'         ,
        'required': False                    ,                    
       }                                           ,                                                                                            
}

class wizard_report (wizard.interface):  
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form'              , 
                       'arch':_transaction_form    ,  
                       'fields':_transaction_fields, 
                       'state':[('end','Cancel'),('print_report','Ver Reporte')]}
        },       
         'print_report' : {
         'actions' : []                                      ,
         'result' : {'type' : 'print'                        ,
                     'report':'reporte.wizard.general.book'  ,
                     'state' : 'end'}
        }, 
    }
wizard_report ('informe.detallado.check.book')
