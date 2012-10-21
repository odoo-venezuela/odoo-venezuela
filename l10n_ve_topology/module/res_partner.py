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

class res_partner_address(osv.osv):
    
    def _get_city_name(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context={}
        res={}
        for obj in self.browse(cr,uid,ids):
            if obj.city_id:
                res[obj.id] = obj.city_id.name
            else:
                res[obj.id] = ''
        return res

    _inherit='res.partner.address'
    _columns = {
        'municipality_id':fields.many2one('res.municipality','Municipality', help="In this field enter the name of the municipality which is associated with the parish", domain= "[('state_id','=',state_id)]"),
        'parish_id':fields.many2one('res.parish','Parish',help="In this field you enter the parish to which the sector is associated",domain= "[('municipalities_id','=',municipality_id)]" ),
        'sector_id':fields.many2one('res.sector',string='Sector',required=False,help="in this field select the Sector associated with this Municipality",domain= "[('state_id','=',state_id)]"),
        'city_id':fields.many2one('res.city',string='City',domain= "[('state_id','=',state_id)]",help="in this field select the city associated with this State"),
        'city':fields.function(_get_city_name, method=True, type='char', string='City', size=256, domain= "[('state_id','=',state_id)]",store=True),
    }

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = super(res_partner_address,self).name_get(cr, user, ids, context=context)
        res = []
        for r in self.read(cr, user, ids, ['name','country_id','state_id','city','municipality_id','parish_id','sector_id','street','street2','partner_id']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                elems = [r['name'], r['country_id'] and r['country_id'][1],r['state_id'] and r['state_id'][1], r['city'], r['municipality_id'] and r['municipality_id'][1],r['parish_id'] and r['parish_id'][1],r['sector_id'] and r['sector_id'][1], r['street'], r['street2'],r['partner_id'] and r['partner_id'][1]]
                addr = ', '.join(filter(bool, elems))
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr or '/')))
                else:
                    res.append((r['id'], addr or '/'))
        return res

res_partner_address()
