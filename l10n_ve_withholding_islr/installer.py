# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
###############################################################################
from osv import osv
from osv import fields
from tools.translate import _

class wh_islr_config(osv.osv_memory):
    _name = 'wh.islr.config'
    _inherit = 'res.config'
    _description = __doc__

    _columns = {
        'journal_purchase': fields.char("Journal Wh Income Purchase", 64, help="Journal for purchase operations involving Withholding Income"),
        'journal_sale': fields.char("Journal Wh Income Sale", 64, help="Journal for sale operations involving Withholding Income"),
        'account_purchase': fields.many2one(
            "account.account",
            "Account Withholding Income Purchase",
            help="Account for purchase operations involving Withholding Income"
        ),
        'account_sale': fields.many2one(
            "account.account",
            "Account Withholding Income Sale",
            help="Account for sale operations involving Withholding Income",
        ),
        'wh_agent': fields.boolean("Withholding Income Agent", help="Check if this company is a withholding income agent"),
    }

    _defaults = {
        'journal_purchase': _("Journal Withholding Income Purchase"),
        'journal_sale': _("Journal Withholding Income Sale"),
    }

wh_islr_config()
