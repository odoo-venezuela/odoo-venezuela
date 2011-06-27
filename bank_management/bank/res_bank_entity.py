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

class res_bank_entity(osv.osv):
    '''
    Modulo que crea las entidades bancarias
    '''
    _name='res.bank.entity'
    _columns={
        'name': fields.char('Bank Name',size=64, required=True, readonly=False)                  ,
        'min_lim':fields.float('Min. Limit',digits=(16,2), readonly=False, required=True )     ,
        'max_lim':fields.float('Max. Limit',digits=(16,2), readonly=False, required=True )     ,
        'format_h':fields.text('Format Check', required=True)                                      ,
    }
    
    def _check_bank(self,cr,uid,ids,context={}):

        obj_bank = self.browse(cr,uid,ids[0])
        cr.execute('select a.name  from res_bank_entity a')
        lista=cr.fetchall()
        #comprension de lista
        bandera=([x[0] for x in lista if x[0] == obj_bank.name])
        #bandera devuelve una lista de las ocurrencias
        if  len(bandera)>1 :
            return False
        return True
    
    def _check_lim(self,cr,uid,ids,context={}):

        obj_bank = self.browse(cr,uid,ids[0])
        if obj_bank.min_lim >= obj_bank.max_lim:
            return False
        else:
            return True
    
    _constraints = [
        (_check_bank, 'Error ! Specified bank name already exists for any other registered bank. ', ['name'])                 ,
        (_check_lim, 'Error ! Minimum limit must be less than maximun limit', ['name'])
    ]
        
res_bank_entity()

class res_partner_bank(osv.osv):
    '''Bank Accounts'''
    _inherit = "res.partner.bank"
    _columns = {
        'bank_id': fields.many2one('res.bank.entity', 'Bank Entity'),
    }
res_partner_bank()
