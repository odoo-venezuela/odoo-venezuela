#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>             
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime

class purchase_order_line(osv.osv):
    
    _name="purchase.order.line"
    _inherit ="purchase.order.line"

    _columns = {
        'concept_id': fields.many2one('islr.wh.concept','Withhold  Concept',help="Withhold concept associated with this rate",required=False),
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty, uom, partner_id, date_order=False, fiscal_position=False, date_planned=False, name=False, price_unit=False, notes=False):
        '''
        This method loads the withholding concept to a product automatically
        '''
        data = super(purchase_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom,partner_id, date_order, fiscal_position)
        if not product:
            return {'value': {'price_unit': 0.0, 'name':'','notes':'', 'product_uom' : False}, 'domain':{'product_uom':[]}}  
        pro = self.pool.get('product.product').browse(cr, uid, product)
        concepto=pro.concept_id.id
        data[data.keys()[1]]['concept_id'] = concepto
        return data
    
purchase_order_line()


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def inv_line_create(self, cr, uid, a, ol):
        ''' 
        This method adds the withholding concept to an invoice.
        '''
        data = super(purchase_order, self).inv_line_create(cr, uid, a, ol)
        data[2]['concept_id'] = ol.concept_id.id 
        return data

    def onchange_partner_id(self, cr, uid, ids, part):
        ''' 
        Return invoicing address by default
        '''
        if not part:
            return {'value':{'partner_address_id': False, 'fiscal_position': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['invoice'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        pricelist = part.property_product_pricelist_purchase.id
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        return {'value':{'partner_address_id': addr['invoice'], 'pricelist_id': pricelist, 'fiscal_position': fiscal_position}}
purchase_order()
