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

from osv import osv, fields
import time
from tools import config
from tools.translate import _


class account_retencion_islr(osv.osv):
    _inherit = 'account.retencion.islr'

    _columns = {
        'invoice_line': fields.one2many('account.islr.invoice', 'retencion_id', 'Invoice Lines', readonly=True, states={'draft':[('readonly',False)]}),


    } 


    def button_reset_invoices(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        aii_obj = self.pool.get('account.islr.invoice')
        for id in ids:
            cr.execute("DELETE FROM account_islr_invoice WHERE retencion_id=%s", (id,))
            partner = self.browse(cr, uid, id,context=context).partner_id
            if partner.lang:
                context.update({'lang': partner.lang})
#            for invoice in aii_obj.compute(cr, uid, id, context=context):
            invoice = aii_obj.compute(cr, uid, id, context=context)
            aii_obj.create(cr, uid, invoice)
         # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.retencion.islr').write(cr, uid, ids, {'invoice_line':[]}, context=context)    
#        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return True


account_retencion_islr()




class account_islr_invoice(osv.osv):
    _name = "account.islr.invoice"
    _description = "Invoice total amount"
    _columns = {
        'retencion_id': fields.many2one('account.retencion.islr', 'Invoice Line', ondelete='cascade', select=True),
        'name': fields.char('Description', size=64),
        'base': fields.float('Base', digits=(16,int(config['price_accuracy']))),
        'amount': fields.float('Retention Amount', digits=(16,int(config['price_accuracy']))),
        'rate': fields.float('Tax Rate', digits=(16,int(config['price_accuracy']))),
    }

    def compute(self, cr, uid, ret_id, context={}):
        tax_grouped = {}
        val={}
        ant = 0
        inv_obj = self.pool.get('account.invoice')
        ret = self.pool.get('account.retencion.islr').browse(cr, uid, ret_id, context)
        cr.execute("select id from account_invoice where partner_id=%s and period_id=%s", (ret.partner_id.id,ret.period_id.id))
        inv_ids = map(lambda x: x[0], cr.fetchall())
        val = {
            'base': 0.0,
            'amount': 0.0,
            'rate': 0.0
        }        
        val['retencion_id'] = ret.id
        val['name'] = ret.name
        for invoice in inv_obj.browse(cr, uid, inv_ids, context):
                for r in invoice.grp_conpt_ids:
                    if r.rate > ant:
                        ant = r.rate

                val['base'] += invoice.amount_untaxed
                if invoice.ret_islr:
                    val['amount'] += invoice.amount_untaxed


        val['rate'] = ant        

        return val

account_islr_invoice()

