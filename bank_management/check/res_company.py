#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Angelica Barrios          <angélicaisabelb@gmail.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################


from osv import osv
from osv import fields
from tools.translate import _
from tools import config


class res_company(osv.osv):
    _inherit = "res.company"
    
    _columns = {
    'expiry':fields.integer('Dias de Caducidad', readonly=False, required=True),
    'transitory': fields.boolean('Cuenta Transitoria', help="Manejo de Cuentas Transitorias"),
    }
    _defaults = {
        'expiry': lambda *a: 30,
    }
res_company()





