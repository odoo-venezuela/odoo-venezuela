# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'wh_iva_agent': fields.boolean('Wh. Agent', help="Indicate if the partner is a withholding vat agent"),
        'wh_iva_rate': fields.float(string='Rate', help="Withholding vat rate"),
        'property_wh_iva_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Purchase withholding vat account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used debit withholding vat amount"),
        'property_wh_iva_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale withholding vat account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used credit withholding vat amount"),

    }
    _defaults = {
        'wh_iva_rate': lambda *a: 0,

    }


res_partner()
