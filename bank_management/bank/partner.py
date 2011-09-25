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
import decimal_precision as dp

class res_partner_bank(osv.osv):
    '''
    Modulo que crea las cuentas contables asociadas a las cuentas bancarias
    '''
    _inherit = "res.partner.bank"
    
    def _get_transitory_money(self, cr, uid, ids, field_name, arg, context):
        res={}
        for i in self.browse(cr,uid,ids):
            mont=0
            pay_support = self.pool.get('voucher.pay.support')   
            pay_support_ids = pay_support.search(cr, uid, [('accounting_bank_id','=',i.id)])      
            pay_support_brow = pay_support.browse(cr, uid, pay_support_ids, context=None) 
            for pay in pay_support_brow:# "por cada soporte de pago"
                if pay.state =="open" or pay.state =="draft":
                    mont=mont + pay.amount
            res[i.id]=mont
        return  res 
 
    
    def _get_virtual_balance(self, cr, uid, ids, field_name, arg, context):
        res={}
        mont_virtual_balance=0
        for i in self.browse(cr,uid,ids):    
            mont_virtual_balance=i.transitory_money + (i.bank_account_id and i.bank_account_id.balance or 0.0)
            res[i.id]=mont_virtual_balance
        return  res 


    def _get_balance(self, cr, uid, ids, field_name, arg, context):
        res={}
        balance=0
        for i in self.browse(cr,uid,ids):    
            balance=i.bank_account_id.balance         
            res[i.id]=balance
        return  res    
    
    _columns={
        'trans_account_id':fields.many2one('account.account','Transitory Account',required=False, readonly=False,domain="[('type', '<>', 'view'),('type', '<>', 'consolidation')]"), 
        'bank_account_id':fields.many2one('account.account','Accounting Account',required=True,readonly=False,domain="[('type', '<>', 'view'),('type', '<>', 'consolidation')]"), 
        'journal_id': fields.many2one('account.journal', 'Journal',required=True),
        'transitory_money':fields.function(_get_transitory_money, method=True, type='float', digits_compute=dp.get_precision('Bank'), string='Transitory Money'),
        'virtual_balance':fields.function(_get_virtual_balance, method=True, type='float', digits_compute=dp.get_precision('Bank'), string='Virtual Balance', help="Proposed Balance=Sum transitory money more balance closed or balance account"),  
        'balance':fields.function(_get_balance, method=True, type='float', digits_compute=dp.get_precision('Bank'), string='Account Balance'),        
    }
res_partner_bank()


