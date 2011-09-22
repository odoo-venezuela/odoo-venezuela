# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
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

import time
from osv import fields, osv



class account_invoice(osv.osv):
    _inherit = 'account.invoice'


    def _retenida_munici(self, cr, uid, ids, name, args, context):
        res = {}
        for id in ids:
            res[id] = self.test_retenida(cr, uid, [id], 'retmun')
        return res


    def _get_inv_munici_from_line(self, cr, uid, ids, context={}):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids

    def _get_inv_munici_from_reconcile(self, cr, uid, ids, context={}):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True
        
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids


    _columns = {
        'wh_local': fields.function(_retenida_munici, method=True, string='Local Withholding', type='boolean',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, None, 50),
                'account.move.line': (_get_inv_munici_from_line, None, 50),
                'account.move.reconcile': (_get_inv_munici_from_reconcile, None, 50),
            }, help="The account moves of the invoice have been withheld with account moves of the payment(s)."),

    }
    




account_invoice()




