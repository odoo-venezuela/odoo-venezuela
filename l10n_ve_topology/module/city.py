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


class city(osv.osv):
    '''
    Model added to manipulate separately the Cities on Partner address.
    '''
    _description='Model to manipulate Cities'
    _name ='res.city'
    _columns = {
        'state_id': fields.many2one('res.country.state','State', required=True, help="This field selects the states to which this city is associated \n"),
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

city()

