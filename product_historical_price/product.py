# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
from tools.translate import _
import decimal_precision as dp
import pooler
import time
import math

class product_historical(osv.osv):
    """
    product_historical
    """
    def _get_historical_price(self, cr, uid, ids, field_name, field_value, arg, context={}):
        res = {}
        product_hist = self.pool.get('product.historic')
        for id in ids:
            if self.browse(cr, uid, id).list_price != self.browse(cr, uid, id).list_price_historical:
                res[id] = self.browse(cr, uid, id).list_price
                product_hist.create(cr, uid, {
                    'product_id' : id,
                    'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': self.browse(cr, uid, id).list_price,
               },context)
        return res
    
    def _get_historical_cost(self, cr, uid, ids, field_name, field_value, arg, context={}):
        res = {}
        product_hist = self.pool.get('product.historic.cost')
        for id in ids:
            if self.browse(cr, uid, id).standard_price != self.browse(cr, uid, id).cost_historical:
                res[id] = self.browse(cr, uid, id).standard_price
                product_hist.create(cr, uid, {
                    'product_id' : id,
                    'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': self.browse(cr, uid, id).standard_price,
               },context)
        return res
    
    _inherit = 'product.product'
    _columns = {
        'list_price_historical': fields.function(_get_historical_price, method=True, string='Latest Price', type='float',digits_compute= dp.get_precision('List_Price_Historical'),
            store={'product.product': (lambda self, cr, uid, ids, c={}: ids, ['list_price'], 50),}, 
            help="Latest Recorded Historical Value"),
        'cost_historical': fields.function(_get_historical_cost, method=True, string=' Latest Cost', type='float',digits_compute= dp.get_precision('Cost_Historical'),
            store={'product.product': (lambda self, cr, uid, ids, c={}: ids, ['standard_price'], 50),}, 
            help="Latest Recorded Historical Cost"),
        'list_price_historical_ids': fields.one2many('product.historic','product_id','Historical Prices'),
        'cost_historical_ids': fields.one2many('product.historic.cost','product_id','Historical Prices'),
        
    }
product_historical()

class product_historic_price(osv.osv):
    _order= "name desc"
    _name = "product.historic.price"
    _description = "Historical Price List"

    _columns = {
        'product_id': fields.many2one('product.product',string='Product related to this Price', required=True),
        'name': fields.datetime(string='Date',  required=True),
        'price': fields.float(string='Price',digits_compute= dp.get_precision('Price')),
        'product_uom': fields.many2one('product.uom', string="Supplier UoM", help="Choose here the Unit of Measure in which the prices and quantities are expressed below.")
        
    }
    _defaults = { 'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

product_historic_price()

class product_historic_cost(osv.osv):
    _order= "name desc" 
    _name = "product.historic.cost"
    _description = "Historical Price List"

    _columns = {
        'product_id': fields.many2one('product.product', string='Product related to this Cost', required=True),
        'name': fields.datetime(string='Date', required=True),
        'price': fields.float(string='Cost', digits_compute= dp.get_precision('Price2')),
        'product_uom': fields.many2one('product.uom', string="Supplier UoM", help="Choose here the Unit of Measure in which the prices and quantities are expressed below.")
        
    }
    _defaults = { 'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

product_historic_cost()
