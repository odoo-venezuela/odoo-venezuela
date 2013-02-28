#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
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

'''
Fiscal Report For Venezuela
'''

from openerp.osv import fields
from openerp.osv import osv
import time
import ir
from mx import DateTime
import datetime
import openerp.pooler
from openerp.tools import config
import wizard
import openerp.netsvc


book_form= """<?xml version="1.0"?>
<form string="Seniat Book">
     <field name="date_start" />
     <field name="date_end" />
     <field name="model" />

</form>
"""

book_field= {
    'date_start': {'string':'Start Date','type':'date','required': True},
    'date_end': {'string':'End Date','type':'date','required': True},
    'model':{'string':"Type of Report", 'type':'selection', 'selection':[('wh_p','Witholding Purchase'),('wh_s','Witholding Sales')]},
}


class wiz_retencion_list(wizard.interface):
    '''
    Wizzard invoice list
    '''

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : book_form,
                    'fields' : book_field,
                    'state' : [('end', 'Cancel','gtk-cancel'),('print_report', 'Print Report','gtk-print') ]}
        },
        'print_report' : {
            'actions' : [],
            'result' : {'type' : 'print',
                   'report':'fiscal.reports.whp.whp_seniat',
                    'state' : 'end'}
        },
    }
wiz_retencion_list("fiscal.reports.whp.wh_book")
