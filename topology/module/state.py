# -*- encoding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
# Copyright (C) 2004-2009 Netquatro, C.A. (<http://openerp.netquatro.com>). 
# All Rights Reserved
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

class state(osv.osv):
    '''
    Model added to manipulate separately the States on Partner address.
    '''
    _inherit = 'res.country.state'
    _columns = {
        'city_ids':fields.many2many('res.city','state_city_rel','state_id','city_id','Cities',help="In this field selects the cities associated with the state\n"),
        'municipalities_ids': fields.one2many('res.municipality',"state_id",'State', required=True,help="In this field enter the name of the associated municipalities to the state"),
    }
state()
