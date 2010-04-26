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
        'invoice_line': fields.one2many('account.islr.invoice', 'invoice_id', 'Invoice Lines', readonly=True, states={'draft':[('readonly',False)]}),


    } 


account_retencion_islr()




class account_islr_invoice(osv.osv):
    _name = "account.islr.invoice"
    _description = "Invoice total amount"
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice Line', ondelete='cascade', select=True),
        'name': fields.char('Description', size=64, required=True),
        'base': fields.float('Base', digits=(16,int(config['price_accuracy']))),
#        'amount': fields.float('Amount', digits=(16,int(config['price_accuracy']))),
#        'manual': fields.boolean('Manual'),
#        'sequence': fields.integer('Sequence'),

#        'base_code_id': fields.many2one('account.tax.code', 'Base Code', help="The account basis of the tax declaration."),
#        'base_amount': fields.float('Base Code Amount', digits=(16,int(config['price_accuracy']))),
#        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),
#        'tax_amount': fields.float('Tax Code Amount', digits=(16,int(config['price_accuracy']))),
    }
    
account_islr_invoice()

