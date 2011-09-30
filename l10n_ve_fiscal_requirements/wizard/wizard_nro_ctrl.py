# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
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

from osv import osv
from osv import fields
from tools.translate import _

_transaction_form = '''<?xml version="1.0"?>
<form string="Modificacion del nro. de control">
    <field name="nro_ctrl"/>
    <separator string="Esta seguro de cambiar el Nro Control ?" colspan="4"/>
    <field name="sure"/>
</form>'''

class wiz_nroctrl(osv.osv_memory):
    _name = 'wiz.nroctrl'
    _description = "Wizard that changes the invoice control number"

    def _set_noctrl(self, cr, uid, data, context):
        if not data['form']['sure']:
            raise osv.except_osv(_("Error!"), _("Please confirm that you want to do this by checking the option"))
        inv_obj = self.pool.get('account.invoice')
        n_ctrl = data['form']['name']
        
        invoice = inv_obj.browse(cr, uid, data['id'])
        if invoice.state == 'draft':
            raise osv.except_osv(_("Error!"), _("You cannot change the state of a Draft invoice"))

        inv_obj.write(cr, uid, data['id'], {'name': n_ctrd}, context=context)
        return {}

    _columns = {
        'name': fields.char('Control Number', 32, required=True),
        'sure': fields.boolean('Are you sure?'),
    }
wiz_nroctrl()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

