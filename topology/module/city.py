##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
# Copyright (C) 2004-2009 Netquatro, C.A. (<http://openerp.netquatro.com>). All Rights Reserved
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


class City(osv.osv):
    '''
    Model added to manipulate separately the Cities on Partner address.
    '''
    _description='Model to manipulate Cities'
    _name ='res.city'
    _columns = {
        'state_ids': fields.many2many('res.country.state','state_city_rel','city_id','state_id','State', required=True, help="This field selects the states to which this city is associated \n"),
        'name': fields.char('City Name', size=64, required=True, help="In this field enter the name of the City \n"),
        'code': fields.char('City Code', size=3,
            help='The city code in three chars, Example: CCS for Caracas .\n', required=True),
    }
    def name_search(self, cr, user, name='', args=None, operator='ilike',
            context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        ids = self.search(cr, user, [('code', '=', name)] + args, limit=limit,
                context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    _order = 'code'

City()

