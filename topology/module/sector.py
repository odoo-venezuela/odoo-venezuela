# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
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
import wizard
import pooler

class sector(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        
        for line in self.browse(cr, uid, ids):
            city = line.city.name
            parish = line.parish.name
            state= line.parish.municipalities_id.state_id.name
            country= line.parish.municipalities_id.state_id.country_id.name
            municipality=line.parish.municipalities_id.name
            location = "%s %s, %s, %s, %s, %s, %s" %(line.zipcode.name,line.name,parish,municipality,state,city,country)
            res.append((line['id'], location))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('zipcode', 'ilike', name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name', operator, name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)

    _name = 'res.sector'
    _description = 'Sector'
    _columns = {
        'name': fields.char('Sector', size=128, required=True,help="In this field enter the name of the Sector\n"),
        'city':fields.many2one('res.city','City',required=True,help="In this field you enter the city to which the sector is associated\n"),
        'parish':fields.many2one('res.parish','Parish',required=True,help="In this field you enter the parish to which the sector is associated\n"),
        'zipcode':fields.many2one('res.zipcode',string='Zip Code',required=True,help="in this field is selected Zip Code associated with this sector\n"),
    }

sector()

class res_partner_address(osv.osv):
    
    def _get_zip(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = obj.location.zipcode
            else:
                res[obj.id] = ""
        return res

    def _zip_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.sector').search(cr, uid, [('zipcode',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args
    
    def _get_parish(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.parish.id, obj.location.parish.name]
            else:
                res[obj.id] = ""
        return res

    def _parish_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.sector').search(cr, uid, [('parish',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args
    
    def _get_municipalities(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.parish.municipalities_id.id, obj.location.parish.municipalities_id.name]
            else:
                res[obj.id] = ""
        return res

    def _municipalities_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.sector').search(cr, uid, [('parish',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args
    
    
    def _get_city(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.city.id, obj.location.city.name]
            else:
                res[obj.id] = ""
        return res

    def _city_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.city').search(cr, uid, [('name',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            # We need to ensure that locatio is NOT NULL. Otherwise all addresses
            # that have no location will 'match' current search pattern.
            new_args.append( ('location','!=',False) )
        return new_args

    def _get_state(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.city.state_id.id, obj.location.city.state_id.name]
            else:
                res[obj.id] = False
        return res

    def _state_id_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.country.state').search(cr, uid, [('state_id',operator,value)], context=context)
            new_args.append( ('location','in',ids) )
        if new_args:
            new_args.append( ('location','!=',False) )
        return new_args

    def _get_country(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                res[obj.id] = [obj.location.city.state_id.country_id.id, obj.location.city.state_id.country_id.name]
            else:
                res[obj.id] = False
        return res

    def _country_id_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            ids = self.pool.get('res.country.state').search(cr, uid, [('country_id',operator,value)], context=context)
            address_ids = []
            for country in self.pool.get('res.country.state').browse(cr, uid, ids, context):
                ids += [city.id for city in country.city_ids]
            new_args.append( ('location','in',tuple(ids)) )
        if new_args:
            new_args.append( ('location','!=',False) )
        return new_args

    _inherit='res.partner.address'
    _columns = {
        
        'location': fields.many2one('res.sector','Location',help="This field shows the full address"),
        'zip': fields.function(_get_zip, fnct_search=_zip_search, method=True,type="char", string='Zip', size=24),
        'parish_id': fields.function(_get_parish, fnct_search=_parish_search, method=True,type="char", string='Parish', size=128),
        'municipalities': fields.function(_get_municipalities, fnct_search=_municipalities_search, method=True,type="char", string='Municipalities', size=128),
        'city': fields.function(_get_city, fnct_search=_city_search, method=True,type="char", string='City', size=128),
        'state_id': fields.function(_get_state, fnct_search=_state_id_search,obj="res.country.state", method=True, type="many2one", string='State'),
        'country_id': fields.function(_get_country, fnct_search=_country_id_search,obj="res.country" ,method=True, type="many2one", string='Country'),
    }

res_partner_address()
