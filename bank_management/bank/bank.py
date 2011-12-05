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
#              Javier Duran              <javier@vauxoo.com>             
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import decimal_precision as dp

class Bank(osv.osv):
    '''
    Modulo que agrega limites las entidades bancarias
    '''
    _inherit = 'res.bank'
    _columns={
        'min_lim':fields.float('Min. Limit', digits_compute= dp.get_precision('Bank'), readonly=False, required=True, help="Minimum amount for check"),
        'max_lim':fields.float('Max. Limit', digits_compute= dp.get_precision('Bank'), readonly=False, required=True, help="Maximum amount for check"),
        'format_h':fields.text('Format Check', required=True, help="Print format of check"),
    }
    
    def _check_bank(self,cr,uid,ids,context={}):
        """
        Check that the bank name is unique.
        -------------------------------------------
        Verifica que el nombre del banco sea único.

        @return: return a boolean True if valid False if invalid
        """
        obj_bank = self.browse(cr,uid,ids[0])
        cr.execute('select a.name from res_bank a')
        lista=cr.fetchall()
        #comprension de lista
        bandera=([x[0] for x in lista if x[0] == obj_bank.name])
        #bandera devuelve una lista de las ocurrencias
        if  len(bandera)>1 :
            return False
        return True
    
    def _check_lim(self,cr,uid,ids,context={}):
        """
        Check that the minimum limit of check note is less than maximum.
        ----------------------------------------------------------------
        Verifica que el límite mínimo del cheque sea menor al límite máximo.

        @return: return a boolean True if valid False if invalid
        """
        obj_bank = self.browse(cr,uid,ids[0])
        if obj_bank.min_lim > obj_bank.max_lim:
            return False
        else:
            return True
    
    _constraints = [
        (_check_bank, 'Error ! Specified bank name already exists for any other registered bank. ', ['name']),
        (_check_lim, 'Error ! Minimum limit must be less than maximun limit', ['name'])
    ]

Bank()


