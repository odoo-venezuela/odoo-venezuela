##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _

class product_uom(osv.osv):
    """
    Third Unit to consolidate sales and purchases!
    """
    _name = 'product.uom'
    _inherit = 'product.uom'
    _description = ''' Elements to control the seconds unit of measure. '''
    
#    def _factor(self, cursor, user, ids, name, arg, context):
#        res = {}
#        for uom in self.browse(cursor, user, ids, context=context):
#            if uom.factor_consol:
#                if uom.factor_inv_data_consol:
#                    res[uom.id] = uom.factor_inv_data_consol
#                else:
#                    res[uom.id] = round(1 / uom.factor_consol, 6)
#            else:
#                res[uom.id] = 0.0
#        return res
    _columns = {
#        'p_uom_id':fields.many2one('product.uom.consol', 'Consolidate Unit', required=False),
        'factor_consol': fields.float('Rate', digits=(12, 6), required=True,
            help='The coefficient for the formula:\n' \
                    '1 (base unit) = coeff (this unit). Rate = 1 / Factor.'),
#        'factor_inv_consol': fields.function(_factor, digits=(12, 6),
#            method=True, string='Factor',
#            help='The coefficient for the formula:\n' \
#                    'coeff (base unit) = 1 (this unit). Factor = 1 / Rate.'),
        'factor_inv_data_consol': fields.float('Factor', digits=(12, 6)),
        'rounding_consol': fields.float('Rounding Precision', digits=(16, 3), required=True,
            help="The computed quantity will be a multiple of this value. Use 1.0 for products that can not be split."),
        'active': fields.boolean('Active'),
    }
                    
product_uom()

class product_uom_consol():
    _name = 'product.uom.consol'
    _description = 'Object to control a third unit to consolidate the sales and purchase.'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
#        'uom_ids':fields.one2many('product.uom', 'p_uom_id', 'Units', required=False),
    }    
    
product_uom_consol()


