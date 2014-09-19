#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
import decimal_precision as dp


class change_invoice_sin_credwizard(osv.TransientModel):

    """
    Wizard that changes the invoice sin cred attribute.
    """
    _name = 'change.invoice.sin.cred'
    _description = 'Change Invoice Sin Cred'
    _columns = {
        'sin_cred': fields.boolean('Sin Cred'),
    }

    def set_sin_cred(self, cr, uid, ids, context=None):
        """
        Change the sin cred field in the invoice
        @return 
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_obj = self.pool.get('account.invoice')
        data = self.browse(cr, uid, ids[0], context=context)
        inv_ids = context.get('active_ids', [])
        if inv_ids:
            inv_obj.write(cr, uid, inv_ids, {
                'sin_cred': data.sin_cred}, context=context)
        return {}
