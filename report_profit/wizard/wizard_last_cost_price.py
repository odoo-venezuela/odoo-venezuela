# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
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

import wizard
import osv
import pooler
from tools.translate import _

_transaction_form = '''<?xml version="1.0"?>
<form string="Update Last Cost Price">
    <separator string="Are you sure ?" colspan="4"/>
    <field name="sure"/>    
</form>'''

_transaction_fields = {    
    'sure': {'string':'Check this box?', 'type':'boolean'},
   
}

def _data_save(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard(_('Error Usuario'), _('Updating Invoice Line, please check the box !'))
    pool = pooler.get_pool(cr.dbname)
    prod_obj = pool.get('product.product')
#    pxt = data['form']['pret']
#    inv_lst = []

    for inv in pool.get('account.invoice').browse(cr, uid, data['ids']):
        if inv.state in ('open', 'paid') and inv.invoice_line:
            for line in inv.invoice_line:
                prod_info = prod_obj._get_last_invoice_func(('done',))
#                inv_lst.append(line.invoice_id.id)

#    inv_obj.write(cr, uid, inv_lst, {'p_ret':pxt}, context=context)
#    inv_obj.button_compute(cr, uid, inv_lst)

    return {}

class wiz_last_cost(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Update')]}
        },
        'change': {
            'actions': [_data_save],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_last_cost('profit.update.costprice')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

