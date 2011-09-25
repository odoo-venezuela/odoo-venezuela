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
from osv import osv, fields
import time
from tools import config

class check_book_wizard(osv.osv):
    _name = "check.book.wizard"
    _columns = {                                                                     
    'check_book_id': fields.many2one('check.book', 'Check Book', required=False)     ,   
    'state_check_note': fields.selection([
            ('sin_filtro','Sin Filtro')                             ,
            ('cobrado','Cobrado')                                   ,
            ('emitido','Emitido')                                   ,
            ],'Check Note State', select=True, required=False)                     ,
    'tiempo': fields.selection([
            ('mes','Periodo Fiscal')                                ,
            ('fecha','Fecha')                                       ,
            ],'Time', select=True)                                ,
    'desde': fields.date('From', required=False)                                   ,
    'hasta': fields.date('To', required=False)                                   ,
    'mes': fields.many2one('account.period', 'Period', required=False)          ,
    }

    _rec_name='check_book_id' # esto es para no crear un atributo name

check_book_wizard()
