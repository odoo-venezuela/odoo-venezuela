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

class sector(osv.osv):

    _name = 'res.sector'
    _description = 'Sector'
    _columns = {
        'zipcode': fields.char('Code', size=10,required=True, help="In this field enter the code of the Sector"),
        'name': fields.char('Sector', size=256,required=True, help="In this field enter the name of the Sector"),
        'state_id': fields.many2one('res.country.state', 'State', required=True , help="In this field enter the name of the state to which the municipality is associated \n"),
    }

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','zipcode']):
            elems = [r['name'],r['zipcode']]
            addr = ', '.join(filter(bool, elems))
            res.append((r['id'], addr or '/'))
        return res

sector()
