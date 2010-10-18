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

from osv import fields,osv
from tools.sql import drop_view_if_exists
import time
import datetime
from mx.DateTime import *
from tools import config


class report_profit_picking(osv.osv):
    def _get_invoice_line(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        aml_obj = self.pool.get('account.move.line')
        purchase_obj = self.pool.get('purchase.order')
        sale_obj = self.pool.get('sale.order')
        il_obj = self.pool.get('account.invoice.line')
        
        for rpp in self.browse(cr, uid, ids, context):
            result[rpp.id] = ()
            il_ids = []
            if rpp.purchase_line_id and rpp.purchase_line_id.id:                
                if rpp.purchase_line_id.order_id.invoice_id and \
                    rpp.purchase_line_id.order_id.invoice_id.id:
                    inv_id = rpp.purchase_line_id.order_id.invoice_id.id
                    il_ids = il_obj.search(cr, uid, [('invoice_id', '=', inv_id), ('product_id', '=', rpp.product_id.id), ('quantity', '=', rpp.picking_qty)])
            if rpp.sale_line_id and rpp.sale_line_id.id:
                for il in rpp.sale_line_id.invoice_lines:
                    il_ids.append(il.id)                    

            if il_ids:
                il = il_obj.browse(cr, uid, il_ids[0], context)
#                print 'lineas consultaxxx: ',il
                result[rpp.id] = (il.id,il.name)
            
        return result

    def _get_aml_cost(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        aml_obj = self.pool.get('account.move.line')
        for rpp in self.browse(cr, uid, ids, context):
            result[rpp.id] = ()
            if rpp.invoice_line_id and rpp.invoice_line_id.id:
                print 'lf: ',rpp.invoice_line_id.id
                moves = self.aml_cost_get(cr, uid, [rpp.invoice_line_id.id])
            #677= llamo get_move_line
            #aml_query = aml_obj.find(cr, uid, mov_id=677)
            #print 'consultaxxx: ',aml_query
            #aml = aml_obj.browse(cr, uid, aml_query[0], context)
                aml = aml_obj.browse(cr, uid, moves[0], context)
                result[rpp.id] = (aml.id,aml.name)
        return result

    def _get_invoice_qty(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for rpp in self.browse(cr, uid, ids, context):
            res[rpp.id] = 0.0
            if rpp.invoice_line_id and rpp.invoice_line_id.id:
                res[rpp.id] = rpp.invoice_line_id.quantity
        return res
    
    def _get_aml_cost_qty(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for rpp in self.browse(cr, uid, ids, context):
            res[rpp.id] = 0.0
            if rpp.aml_cost_id and rpp.aml_cost_id.id:
                res[rpp.id] = rpp.aml_cost_id.quantity
        return res        
    
#    def _get_moveline():
    def aml_cost_get(self, cr, uid, il_id):    
        res = []
        il_obj = self.pool.get('account.invoice.line')
        res = il_obj.move_line_id_cost_get(cr, uid, il_id)    
        return res
    
    def _logistical_process():
          '''
          Aqui va la logica para los casos de conversiones de product
          '''

          return algo
        
    _name = "report.profit.picking"
    _description = "Move by Picking"
    _auto = False
    _columns = {
        'name': fields.char('Date', size=20, readonly=True, select=True),
        'picking_id':fields.many2one('stock.picking', 'Picking', readonly=True, select=True),
        'purchase_line_id': fields.many2one('purchase.order.line', 'Purchase Line', readonly=True, select=True),
        'sale_line_id': fields.many2one('sale.order.line', 'Sale Line', readonly=True, select=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True, select=True),
        'location_id':fields.many2one('stock.location', 'Source Location', readonly=True, select=True),
        'location_dest_id':fields.many2one('stock.location', 'Dest. Location', readonly=True, select=True),                
        'stk_mov_id':fields.many2one('stock.move', 'Picking line', readonly=True, select=True),
        'picking_qty': fields.float('Picking quantity', readonly=True),        
        'type': fields.selection([
            ('out', 'Sending Goods'),
            ('in', 'Getting Goods'),
            ('internal', 'Internal'),
            ('delivery', 'Delivery')
            ],'Type', readonly=True, select=True),        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ],'Status', readonly=True, select=True),
        'aml_cost_id': fields.function(_get_aml_cost, method=True, type='many2one', relation='account.move.line', string='Cost entry'),
        'invoice_line_id': fields.function(_get_invoice_line, method=True, type='many2one', relation='account.invoice.line', string='Invoice line'),
        'invoice_qty': fields.function(_get_invoice_qty, method=True, type='float', string='Invoice quantity', digits=(16, int(config['price_accuracy']))),
        'aml_cost_qty': fields.function(_get_aml_cost_qty, method=True, type='float', string='Cost entry quantity', digits=(16, int(config['price_accuracy']))),                
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_profit_picking')
        cr.execute("""
            create or replace view report_profit_picking as (
            select
                sm.id as id,                
                to_char(sm.date, 'YYYY-MM-DD:HH24:MI:SS') as name,
                sm.picking_id as picking_id,
                sp.type as type,                
                sm.purchase_line_id as purchase_line_id,
                sm.sale_line_id as sale_line_id,
                sm.product_id as product_id,
                sm.location_id as location_id,
                sm.location_dest_id as location_dest_id,                
                sm.id as stk_mov_id,
                sm.product_qty as picking_qty,
                sm.state as state
            from stock_picking sp
                right join stock_move sm on (sp.id=sm.picking_id)
                left join product_template pt on (pt.id=sm.product_id)
            where sm.state='done' and pt.type!='service'
            order by name
            )
        """)
report_profit_picking()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

