#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import osv
from osv import fields
from tools.translate import _
import wizard
import pooler

class sector(osv.osv):

    #~ def name_get(self, cr, uid, ids, context=None):
        #~ if not len(ids):
            #~ return []
        #~ res = []
        #~ 
        #~ for line in self.browse(cr, uid, ids):
            #~ city = line.city.name
            #~ parish = line.parish.name
            #~ state= line.parish.municipalities_id.state_id.name
            #~ municipality=line.parish.municipalities_id.name
            #~ location = "%s %s, %s, %s, %s, %s" %(line.zipcode.name,line.name,parish,municipality,state,city)
            #~ res.append((line['id'], location))
        #~ return res

    #~ def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        #~ if args is None:
            #~ args = []
        #~ if context is None:
            #~ context = {}
        #~ ids = []
        #~ if name:
            #~ ids = self.search(cr, uid, [('zipcode', 'ilike', name)]+ args, limit=limit)
        #~ if not ids:
            #~ ids = self.search(cr, uid, [('name', operator, name)]+ args, limit=limit)
        #~ return self.name_get(cr, uid, ids, context=context)

    _name = 'res.sector'
    _description = 'Sector'
    _columns = {
        'name': fields.char('Sector', size=128, required=True,help="In this field enter the name of the Sector"),
        'city':fields.related('city_id',type="many2one",required=True,relation='res.partner.address',help="In this field you enter the city to which the sector is associated"),
        'municipality':fields.related('municipality_id',type="many2one",relation='res.partner.address',required=True, help="In this field enter the name of the municipality which is associated with the parish"),
        'parish':fields.related('parish_id',type="many2one",required=True,relation='res.partner.address',help="In this field you enter the parish to which the sector is associated"),
        'zipcode':fields.related('zipcode_id',type="many2one",string='Zip Code',relation='res.partner.address',required=False,help="in this field is selected Zip Code associated with this sector"),
        'state':fields.related('state_id',type="many2one",required=False, relation='res.partner.address',help="In this field enter the name of state associated with the country"),
        'country':fields.related('country_id',type="many2one",required=False, relation='res.partner.address',help="In this field enter the name of Country"),
    }

sector()

class res_partner_address(osv.osv):
    
    def _get_zip(self, cr, uid, ids, field_name, arg, context):
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.location:
                print 'PASEEEE:',obj.location.zipcode
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
                res[obj.id] = [obj.location.city.state_ids.id, obj.location.city.state_ids.name]
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
                print 'obj.location.city.state_ids',obj.location.city.state_ids
                res[obj.id] = [obj.location.city.state_ids[0].country_id.id, obj.location.city.state_ids[0].country_id.name]
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
        'municipality_id':fields.many2one('res.municipality','Municipality',required=True, help="In this field enter the name of the municipality which is associated with the parish", domain= "[('state_id','=',state_id)]"),
        'parish_id':fields.many2one('res.parish','Parish',required=True,help="In this field you enter the parish to which the sector is associated",domain= "[('municipalities_id','=',municipality_id)]" ),
        'zipcode_id':fields.many2one('res.zipcode',string='Zip Code',required=False,help="in this field is selected Zip Code associated with this sector"),
        'sector_id':fields.many2one('res.sector',string='Sector',required=False,help="in this field select the Sector associated with this Municipality"),
        'city_id':fields.many2one('res.city','City',required=True,help="In this field you enter the city to which the sector is associated", domain= "[('state_id','=',state_id)]"),
    }

res_partner_address()
