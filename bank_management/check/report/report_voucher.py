##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import time
from report import report_sxw
from tools import amount_to_text_en
from numero_a_texto import Numero_a_Texto

class report_voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_voucher, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time                    ,
            'convert':self.convert          ,
            'debit':self.debit              ,
            'credit':self.credit            ,
            'get_ref' : self._get_ref       ,
            'get_payee':self.get_payee      ,
            'obt_texto':self.obt_texto      ,
            'get_vat':self.get_vat          ,
            'get_number':self.get_number    ,
            'get_name':self.get_name        ,
        })      
        
    def get_payee(self, voucher):
        payee=""
        if voucher.payee_id: #si existe un beneficiario se toma este si no se toma la comania 
            payee=voucher.payee_id.name
        else:#la compania
            payee=voucher.partner_id.name
        return payee
    
    def get_vat(self, voucher):
        rif=""
        if voucher.payee_id: #si existe un beneficiario se toma este si no se toma la comania 
            rif=" "
        else:#la compania
            rif=voucher.partner_id.vat
            a=rif[3:12]
        return a
    

    def obt_texto(self, amount):
        res=Numero_a_Texto(amount)
        return res

    def convert(self,amount, cur):
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return amt_en
    
    def debit(self, move_ids):
        debit = 0.0
        for move in move_ids:#self.pool.get('account.move.line').browse(self.cr, self.uid, move_ids):
            debit +=move.debit
        return debit
    
    def credit(self, move_ids):
        credit = 0.0
        for move in move_ids:#self.pool.get('account.move.line').browse(self.cr, self.uid, move_ids):
            credit +=move.credit
        return credit
    
    def _get_ref(self, voucher_id, move_ids):
        voucher_line = self.pool.get('account.voucher.line').search(self.cr, self.uid, [('partner_id','=',move_ids.partner_id.id), ('voucher_id','=',voucher_id)])
        if voucher_line:
            voucher = self.pool.get('account.voucher.line').browse(self.cr, self.uid, voucher_line)[0]
            return voucher.ref
        else:
            return

    def get_number(self,id_voucher):
        voucher = self.pool.get('account.voucher')
        id_voucher_pay_sup=voucher.search(self.cr, self.uid, [('voucher_pay_support_id','=',id_voucher)])[0]
        res1=voucher.browse(self.cr, self.uid, id_voucher_pay_sup).number
        res2=voucher.browse(self.cr, self.uid, id_voucher_pay_sup).state
        res=[res1,res2]
        return res
    
    def get_name(self,id_voucher):
        res1=""
        voucher = self.pool.get('account.voucher')
        id_voucher_pay_sup=voucher.search(self.cr, self.uid, [('voucher_pay_support_id','=',id_voucher.id)])[0]
        res1=voucher.browse(self.cr, self.uid, id_voucher_pay_sup).name
        return res1
        
report_sxw.report_sxw(
    'report.cash_receipt.drcr.3',
    'voucher.pay.support',
    'addons/voucher_pay_support/report/report_voucher.rml',
    parser=report_voucher,header=False
)
