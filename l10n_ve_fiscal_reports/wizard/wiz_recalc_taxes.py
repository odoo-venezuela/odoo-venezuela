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

from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import wizard
import netsvc


book_form= """<?xml version="1.0"?>
<form string="Recompute taxes on Invoices">
<group colspan="6" cols="2">
    <label align="0.7" colspan="6" string="Please Select date range of invoices to be recalculated, this method allow group same taxes on invoices."/>
     <field name="date_start" />
     <newline/>
     <field name="date_end" />
</group>
</form>
"""

book_field= {
    'date_start': {'string':'Start Date','type':'date','required': True},
    'date_end': {'string':'End Date','type':'date','required': True},
}


class wiz_invoice_recalc(wizard.interface):
    '''
    Wizzard recalc taxes for error in the behaviour of group taxes
    '''
    def _recalc_taxes(self, cr, uid, data, context):
        d1=data['form']['date_start']
        d2=data['form']['date_end']
        invoice_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        invoices = invoice_obj.search(cr, uid, [('date_invoice', '<=', d2), ('date_invoice', '>=', d1)])
        for inv in invoice_obj.browse(cr,uid,invoices):
            invoice_obj.button_compute(cr,uid,[inv.id],{},set_total=True)
            print "RECALCULADA.........",inv.id
        return True
    
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : book_form,
                    'fields' : book_field,
                    'state' : [('end', 'Cancel','gtk-cancel'),('compute_taxes', 'Execute Update','gtk-print') ]}
        },
        'compute_taxes' : {
            'actions' : [],
            'result' : {'type' : 'action',
                        'action': _recalc_taxes,
                    'state' : 'end'}
        },
    }
wiz_invoice_recalc("fiscal.recalc.taxes")
