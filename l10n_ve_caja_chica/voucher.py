# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
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



class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _description = "Caja Chica"
    _columns = {
        'caj_chi': fields.boolean('Es voucher caja chica', help="Indica si es un voucher de caja chica"),

    }


    def button_reset_line(self, cr, uid, ids, context={}):
        inv_obj = self.pool.get('account.invoice')   
        vline_lst = []     
        for id in ids:
            cr.execute("DELETE FROM account_voucher_line WHERE voucher_id=%s", (id,))            

        inv_ids = inv_obj.search(cr,uid,[('caj_chi','=',True),('state','=','open'),('type','=','in_invoice')])
        for inv in inv_obj.browse(cr, uid, inv_ids):
            vline_vals = {
                'name': inv.name,
                'account_id': inv.account_id.id,
                'partner_id': inv.partner_id.id,
                'amount': inv.residual,
                'invoice_id': inv.id
                }
            vline_lst.append((0,0,vline_vals))

        voucher_vals = {
            'voucher_line_ids': vline_lst
        }
        self.write(cr, uid, ids, voucher_vals)
            
        return True


account_voucher()


class VoucherLine(osv.osv):
    _inherit = 'account.voucher.line'

    def _check_invoice(self,cr,uid,ids,context={}):
        obj_vline = self.browse(cr,uid,ids[0])

        if obj_vline.invoice_id and obj_vline.invoice_id.id:
            cr.execute('select id,invoice_id from account_voucher_line where voucher_id=%s and invoice_id=%s', (obj_vline.voucher_id.id, obj_vline.invoice_id.id))
            res=dict(cr.fetchall())
            if (len(res) == 1):
                res.pop(ids[0],False)            
            if res:
                return False
        return True


    _constraints = [
        (_check_invoice, 'Error ! Factura asignada. ', ['invoice_id'])
    ]

    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context={}):
        res = super(VoucherLine, self).onchange_invoice_id(cr, uid, ids, invoice_id, context)
        invoice_obj = self.pool.get('account.invoice')
        invoice = invoice_obj.browse(cr, uid, invoice_id, context)
        res['value'].update({'account_id':invoice.account_id.id,'partner_id':invoice.partner_id.id,'name':invoice.name})
        return res 


VoucherLine()


