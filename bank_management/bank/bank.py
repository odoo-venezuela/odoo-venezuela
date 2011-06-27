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

class res_bank(osv.osv):
    '''
    Modulo que crea las cuentas bancarias de las entidades asociadas
    '''
    _name='res.bank'
    _inherit = 'res.bank'
    _columns={
        'trans_account_id':fields.many2one('account.account','Transitory Account',required=False, readonly=False,domain="[('type', '<>', 'view'),('type', '<>', 'consolidation')]"), 
        'bank_account_id':fields.many2one('account.account','Bank Account',required=True,readonly=False,domain="[('type', '<>', 'view'),('type', '<>', 'consolidation')]"), 
        'journal_id': fields.many2one('account.journal', 'Journal',required=True),
        'bank_id': fields.many2one('res.bank.entity','Bank',required=True),
        'agencia':fields.char('Bank Agency', size=30,required=True),
    }
res_bank()

class res_bank_entity(osv.osv):
    _inherit='res.bank.entity'
    _columns={
        'accounting_bank_ids':fields.one2many('res.bank','bank_id','Account'),
    }
res_bank_entity()
