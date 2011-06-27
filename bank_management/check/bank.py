# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
from tools.translate import _
import decimal_precision as dp

class res_partner_bank(osv.osv):
    """
    res_partner_bank
    """
    _inherit = 'res.partner.bank'
    _columns = {
        'checkbook_ids':fields.one2many('res.partner.bank.checkbook', 'account_id', 'Bank Account', required=False),
    }
res_partner_bank()


class res_bank(osv.osv):
    '''
    Calculo de Saldo Virtual
    '''
    _name='res.bank'
    _inherit = 'res.bank'
    
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
            mont_virtual_balance=i.transitory_money+ i.bank_account_id.balance         
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
        'transitory_money':fields.function(_get_transitory_money, method=True, type='float', digits_compute= dp.get_precision('Bank'), string='Transitory Money'),
        'virtual_balance':fields.function(_get_virtual_balance, method=True, type='float', digits_compute= dp.get_precision('Bank'), string='Virtual Balance', help="Proposed Balance=Sum transitory money more balance closed or balance account"),  
        'balance':fields.function(_get_balance, method=True, type='float', digits_compute= dp.get_precision('Bank'), string='Account Balance'),
    }
    
res_bank()

