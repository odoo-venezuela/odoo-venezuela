#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
################################################################################
import wizard
import osv
import pooler
import time
from dateutil.relativedelta import relativedelta
from tools.translate import _
import tools

_transaction_form = '''<?xml version="1.0"?>
<form string=" Seleccione las Facturas a Pagar">
     <newline/>
     <field name="invoice_ids" nolabel="1" domain="[('type','=','in_invoice'),
                                                    ('state','=','open'),
                                                    ('residual','&gt;',0)]"/>
</form>'''

_transaction_fields = {
    'invoice_ids': {
        'string': 'Facturas',
        'type': 'many2many',
        'relation': 'account.invoice',
        'required': True
        },
   # 'date':{'string':'Vencimiento','type':'date','required':True, 'default':time.strftime('%Y-%m-%d')}     
}

def _create_voucher_lines(self, cr, uid, data, context):
    invoice_ids=data['form']['invoice_ids'][0][2]
    pool= pooler.get_pool(cr.dbname)    
    avl_obj=pool.get('account.voucher.line')
    inv_obj=pool.get('account.invoice')
    for i in invoice_ids:
        invoice = inv_obj.browse(cr,uid,i,context)
        values = {
            'voucher_id':None,
            'name': 'Factura %s' % (invoice.reference),
            'account_id':invoice.account_id and invoice.account_id.id or False,
            'partner_id':invoice.partner_id and invoice.partner_id.id or False,
            'amount':invoice.residual,
            'type':'dr',
            'ref': '',
            'invoice_id':i
        }
        a =avl_obj.create(cr, uid, values)
    return {}

class wizard_invoice(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form'              , 
                       'arch':_transaction_form    ,  
                       'fields':_transaction_fields, 
                       'state':[('end','Cancel'),('create','Generar lineas de Orden de Pago')]}
        },
        'create': {
        'actions': [],
        'result': {'type': 'action',
                    'action':_create_voucher_lines,
                   'state':'end'}
        },
    }
wizard_invoice('account_gen_pay_su')
