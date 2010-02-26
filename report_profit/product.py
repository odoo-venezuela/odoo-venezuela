# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
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


from osv import fields
from osv import osv
import ir
import pooler

class product_supplierinfo(osv.osv):
    _inherit = 'product.supplierinfo'
    _name = "product.supplierinfo"

    def _last_sup_invoice(self, cr, uid, ids, name, arg, context):
        res = {}
        for supinfo in self.browse(cr, uid, ids):
            cr.execute("select inv.id, max(inv.date_invoice) from account_invoice as inv, account_invoice_line as line where inv.id=line.invoice_id and product_id=%s and partner_id=%s and state in ('open', 'paid') and type='in_invoice' group by inv.id", (supinfo.product_id.id, supinfo.name.id,))
            record = cr.fetchone()
            if record:
                res[supinfo.id] = record[0]
            else:
                res[supinfo.id] = False
        return res

    def _last_sup_invoice_date(self, cr, uid, ids, name, arg, context):
        res = {}
        inv = self.pool.get('account.invoice')
        _last_sup_invoices = self._last_sup_invoice(cr, uid, ids, name, arg, context)
        dates = inv.read(cr, uid, filter(None, _last_sup_invoices.values()), ['date_invoice'])
        for suppinfo in ids:
            date_inv = [x['date_invoice'] for x in dates if x['id']==_last_sup_invoices[suppinfo]]
            if date_inv:
                res[suppinfo] = date_inv[0]
            else:
                res[suppinfo] = False
        return res

    _columns = {
        'last_inv' : fields.function(_last_sup_invoice, type='many2one', obj='account.invoice', method=True, string='Last Invoice'),
        'last_inv_date' : fields.function(_last_sup_invoice_date, type='date', method=True, string='Last Invoice date'),
    }
product_supplierinfo()


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'


    def _last_invoice(self, cr, uid, ids, name, arg, context):
        res = {}
        tipo='in_invoice'
        for product in self.browse(cr, uid, ids):
            cr.execute("select inv.id, max(inv.date_invoice) as date from account_invoice as inv, account_invoice_line as line where inv.id=line.invoice_id and product_id=%s and state in ('open', 'paid') and type=%s group by inv.id order by date desc", (product.id, tipo,))
            record = cr.fetchone()
            if record:
                res[product.id] = record[0]
            else:
                res[product.id] = False
        return res

    def _last_invoice_date(self, cr, uid, ids, name, arg, context):
        res = {}
        inv = self.pool.get('account.invoice')
        _last_invoices = self._last_invoice(cr, uid, ids, name, arg, context)
        dates = inv.read(cr, uid, filter(None, _last_invoices.values()), ['date_invoice'])
        for prod_id in ids:
            date_inv = [x['date_invoice'] for x in dates if x['id']==_last_invoices[prod_id]]
            if date_inv:
                res[prod_id] = date_inv[0]
            else:
                res[prod_id] = False
        return res



    _columns = {
        'last_inv' : fields.function(_last_invoice, type='many2one', obj='account.invoice', method=True, string='Last Invoice'),
        'last_inv_date' : fields.function(_last_invoice_date, type='date', method=True, string='Last Invoice date'),
    }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

