# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This Modules was developed by Netquatro, C.A. (<http://openerp.netquatro.com>)
#    Silver partner of Tiny.
#    author Nhomar Hernandez (nhomar.hernandez@netquatro.com) &
#           Javier Duran (<javier.duran@netquatro.com>)
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
import time
#import pooler
#import urllib
import base64
import tools
from tools.translate import _
#import wizard
from tools.misc import currency
import csv

#class product_template(osv.osv):
#    '''
#    Relation with product
#    '''
#    _description = 'Inheriting Products templates'
#    _inherit = 'product.template'
#    #Do not touch _name it must be same as _inherit
#    _name = 'product.template'
#    _columns = {
#        'list_line_ids': fields.one2many('load.pricelist.lines', 'product_id', 'Partners'),
#    }
#product_template()


class load_pricelist(osv.osv):
    '''
Price agreements from suppliers
    '''
    _name = 'load.pricelist'
    _description = 'load_pricelist'
    _columns = {
        'name':fields.char('Name', size=64, required=False, readonly=False),
        #'partner_id': fields.related('partner_id','partner_id', type='many2one', relation='res.partner', string='Partner'),
        'file_csv':fields.binary('CSV List', filters=None, help='Load in this order supplier,price,quantity,product_code'),
        'date': fields.date('Valid Since'),
        'price_ids':fields.one2many('load.pricelist.lines', 'line_id', 'Price2Load', required=False),
        'state':fields.selection([
        ('draft','Draft'),
        ('loaded','Loaded'),
        ('review','Review'),
        ('toprocess','To Process'),
        ('dne','Done'),
        ],'State', select=True, readonly=True),
    }




    def product_price_list_import(self, cr, uid, id, file, filename, context={}):
        file2 = base64.decodestring(file)
        file2 = file2.split('\n')
        reader = csv.DictReader(file2, delimiter=',', quotechar='"')
        print 'archivo: ',list(reader)
        return []



load_pricelist()

class load_pricelist_lines(osv.osv):
    '''
Pricelist from supplier
This is recorded and imported before put on right place for control of changes
    '''
    _name = 'load.pricelist.lines'
    _description = 'Pricelist from supplier'
    _columns = {
        'name':fields.char("Element's Identifier", size=64, required=False, readonly=False),
        #'product_id' : fields.many2one('product.template', 'Product', required=True, ondelete='cascade', select=True),
        'product_name':fields.char('Product name', size=64, required=False, readonly=False),
        'product_sup_name':fields.char('Product Sup Name', size=64, required=False, readonly=False),
        'min_qt':fields.float('Min Quantity'),
        'cost':fields.float('Cost by Unit'),
        'price':fields.float('Sugested Price'),
        'line_id':fields.many2one('load.pricelist', 'Load ID', required=False),
        'imported':fields.boolean('Imported', required=False),
    }
load_pricelist_lines()


