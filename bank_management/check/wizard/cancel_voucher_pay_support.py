#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Angelica Barrios          <angelicaisabelb@gmail.com>
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

from osv import fields, osv
import tools
from tools.translate import _
from tools import config

class cancel_voucher_pay_support(osv.osv_memory):
    _name = "cancel.voucher.pay.support"
    _columns = {
        'name':fields.char('Name', 64),
        'accounting_bank_id':fields.many2one('res.partner.bank','Bank Account', readonly=False , required=True), 
        'check_note_id': fields.many2one('check.note', 'Check No', required=True, readonly=True, domain="[('accounting_bank_id','=',accounting_bank_id)]"),
        'bank_id':fields.related('check_note_id','bank_id',type='many2one',relation='res.bank',string='Bank', store=True, readonly=True),
        'min_lim':fields.related('bank_id','min_lim',type='integer',relation='res.bank',string='Min. Limit (Bs.)',readonly=True,store=False),
        'max_lim':fields.related('bank_id','max_lim',type='integer',relation='res.bank',string='Max Limit (Bs.)',readonly=True,store=False),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'expiry':fields.related('company_id','expiry', type='integer',relation='res.company',string='expiration days',readonly=True,store=True),
        'payee_id':fields.many2one('res.partner.address','Beneficiary',required=False, readonly=True),
        'partner_id':fields.many2one('res.partner','Contrapartida',required=True, readonly=True),
        'state': fields.selection([
            ('draft','Draft'), 
            ('open','Open'),
            ('done','Done'),
            ('cancel','Cancel'),
            ],'Estado', select=True, readonly=True, help="Check note state"),
        'wire':fields.char('Transfer',size=26),
        'type': fields.selection([
            ('check','Check'),
            ('wire','Transfer'),
            ],'Type', required=True, select=True),
        'bool_good': fields.boolean('Printed'),
        'bool_bad': fields.boolean('No Printed'),
        'bool_sure': fields.boolean('Are you sure?'),
        'notes':fields.char('Reason',size=256, required=False, readonly=False ),
        'cancel_check_note': fields.selection([
            ('print','Print error'),
            ('perdida','Loss or misplacement'),
            ('dan_fis','Physical damage'),
            ('pago','Payment is not made'),
            ('devuelto','Returned check'),
            ('caduco','Expired'),
            ('otros','Others'),
            ],'Reason for Cancellation', select=True, required=True),
        'amount':fields.float('Total amount', readonly=True),
        'date':fields.date('Date', required=True),
        'period_id': fields.many2one('account.period', 'Period', required=True),
    }

   
    def action_cheque(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        created_account_voucher = []  
        account_voucher=self.pool.get('account.voucher')
        account_voucher_line=self.pool.get('account.voucher.line') 
        id=context["active_id"] 
        acount_voucher_id=account_voucher.search(cr, uid, [('voucher_pay_support_id','=',id)]) [0]
        obj_acount_voucher=account_voucher.browse(cr, uid, acount_voucher_id, context=None)
        
        voucher_pay_support=self.pool.get('voucher.pay.support')
        obj_voucher_pay_support=voucher_pay_support.browse(cr, uid, id, context=None)
        

        fecha=obj.date
        periodo=obj.period_id.id
        nota=obj.notes
        if nota==False:
            can = {
            'print': _('Print Error'),
            'perdida':_('Loss or misplacement'),
            'dan_fis': _('Physical damage'),
            'pago':_('Payment is not made'),
            'caduco':_('Expired'),
            'devuelto':_('Returned check')
            }
            name= _("CANCELLATION OF THE CHECK FOR CONCEPT %s - REASON: %s")%(obj_acount_voucher.name,can[obj.cancel_check_note])
            narration= _("CANCELLATION PAYCHECK NUMBER %s - %s REASON: %s")%(obj_acount_voucher.number,obj_acount_voucher.name,can[obj.cancel_check_note])
        else:
            name=_("CANCELLATION OF THE CHECK FOR CONCEPT %s - REASON: %s")%(obj_acount_voucher.name,nota)
            narration=_("CANCELLATION PAYCHECK NUMBER %s - %s REASON: %s")%(obj_acount_voucher.number,obj_acount_voucher.name,nota)



        transitory=self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.transitory
        if transitory== True:   
            cuenta_transitoria=obj_voucher_pay_support.accounting_bank_id.trans_account_id   
            if cuenta_transitoria: #si hay cuenta transitoria
                #se crea el nuevo documento de comprobante diario
                account_voucher_id=account_voucher.create(cr, uid,{
                                'name':name,
                                'type':'journal_voucher',
                                'date':fecha,
                                'journal_id':obj_acount_voucher.journal_id.id,
                                'account_id':obj_voucher_pay_support.accounting_bank_id.trans_account_id.id,
                                'period_id':obj_acount_voucher.period_id.id,
                                'narration':narration,
                                'currency_id':obj_acount_voucher.currency_id.id,
                                'company_id':obj_acount_voucher.company_id.id,
                                'state':'draft',
                                'amount':obj_acount_voucher.amount,
                                'reference_type': 'none',
                                'partner_id':obj_acount_voucher.partner_id.id,
                                'payee_id':obj_acount_voucher.payee_id.id,
                                },context=None)
                for line in obj_acount_voucher.payment_ids:    
                    account_voucher_line_id=account_voucher_line.create(cr, uid,{
                                    'voucher_id':account_voucher_id,
                                    'name': line.name,
                                    'account_id': line.account_id.id,
                                    'partner_id': line.partner_id.id,
                                    'amount': line.amount,
                                    'type': 'cr',
                                    'ref':line.ref,
                                    'account_analytic_id': line.account_analytic_id,
                                    },context=None)

                #xml_id = 'action_view_cont_voucher_form'
                xml_id = 'action_view_jour_voucher_form'
            else:
                raise osv.except_osv(_('Alert !'), _('You have to enter the transitory bank account: %s')%(obj_voucher_pay_support.accounting_bank_id.bank_id.name))


        else:#no hay cuentas transitorias
            #se crea el nuevo documento de comprobante diario
            account_voucher_id=account_voucher.create(cr, uid,{
                            'name':name,
                            'type':'journal_voucher',
                            'date':fecha,
                            'journal_id':obj_acount_voucher.journal_id.id,
                            'account_id':obj_acount_voucher.account_id.id,
                            'period_id':periodo,
                            'narration': narration,
                            'currency_id':obj_acount_voucher.currency_id.id,
                            'company_id': obj_acount_voucher.company_id.id,
                            'state':'draft',
                            'amount':obj_acount_voucher.amount,
                            'reference_type': 'none',
                            'partner_id': obj_acount_voucher.partner_id.id,
                            'payee_id': obj_acount_voucher.payee_id.id,
                            },context=None)

            for line in obj_acount_voucher.payment_ids:
                account_voucher_line_id=account_voucher_line.create(cr, uid,{
                                'voucher_id':account_voucher_id,
                                'name':line.name,
                                'account_id':line.account_id.id,
                                'partner_id':line.partner_id.id,
                                'amount':line.amount,
                                'type':'cr',
                                'ref':line.ref,
                                'account_analytic_id':line.account_analytic_id,
                                },context=None) 
            xml_id = 'action_view_jour_voucher_form'

        #se cambia el documento a estado a cancel
        voucher_pay_support.write(cr,uid,id,
                                  {'state' : 'cancel' , 
                                   'cancel_check_note': obj.cancel_check_note , 
                                   'notes':obj.notes, 
                                   'return_voucher_id':account_voucher_id})
        #se cambia el cheque a estado cancelado
        self.pool.get('check.note').write(cr,uid,obj_voucher_pay_support.check_note_id.id,{'state' : 'cancel', 'cancel_check_note':obj.cancel_check_note, 'notes':obj.notes })

        #Se redirecciona la ventana al tree
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        #xml_id = 'action_view_jour_voucher_form'
        result = mod_obj._get_id(cr, uid, 'account_voucher', xml_id) 
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        result = act_obj.read(cr, uid, id)
        created_account_voucher.append(account_voucher_id)
        result['res_id'] = created_account_voucher  
        return result

cancel_voucher_pay_support()
