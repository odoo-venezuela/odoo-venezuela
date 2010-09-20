from osv import osv, fields
import pooler
import time
import math

from tools import config
from tools.translate import _

class product_product(osv.osv):

    def _get_historical_price(self, cr, uid, ids, field_name, field_value, arg, context={}):

        res = {}

        product_hist = self.pool.get('product.historic')

        for id in ids:
            if self.browse(cr, uid, id).list_price <> self.browse(cr, uid, id).list_price_historical:
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
            if self.browse(cr, uid, id).standard_price <> self.browse(cr, uid, id).cost_historical:
                res[id] = self.browse(cr, uid, id).standard_price
                product_hist.create(cr, uid, {
                    'product_id' : id,
                    'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': self.browse(cr, uid, id).standard_price,
               },context)
        return res

    _inherit = "product.product"
    _columns = {
        'list_price_historical': fields.function(_get_historical_price, method=True, string=' Latest Price', type='float',
            store={
                'product.product': (lambda self, cr, uid, ids, c={}: ids, ['list_price'], 50),
            }, help="Latest Recorded Historical Value"),
        'cost_historical': fields.function(_get_historical_cost, method=True, string=' Latest Cost', type='float',
            store={
                'product.product': (lambda self, cr, uid, ids, c={}: ids, ['standard_price'], 50),
            }, help="Latest Recorded Historical Cost"),
        'list_price_historical_ids': fields.one2many('product.historic','product_id','Historical Prices'),            
        'cost_historical_ids': fields.one2many('product.historic.cost','product_id','Historical Prices'),            
    }
    
product_product()

class product_historic(osv.osv):
    _order= "name desc"
    _name = "product.historic"
    _description = "Historical PriceList"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product related to this Price',  required=True),
        'name': fields.datetime('Date',  required=True),
        'price': fields.float('Price', digits=(16,2)),
        
    }
    
    _defaults = { 'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

product_historic()

class product_historic_cost(osv.osv):
    _order= "name desc" 
    _name = "product.historic.cost"
    _description = "Historical PriceList"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product related to this Cost',  required=True),
        'name': fields.datetime('Date',  required=True),
        'price': fields.float('Cost', digits=(16,2)),
        
    }

    _defaults = { 'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

product_historic_cost()
