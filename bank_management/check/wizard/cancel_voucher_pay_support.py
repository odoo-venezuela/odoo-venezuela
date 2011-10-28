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
        'name':fields.char('Nombre', 64),
        'accounting_bank_id':fields.many2one('res.bank','Cuenta Bancaria', readonly=False , required=True), 
        'check_note_id': fields.many2one('check.note', 'Non. Cheque', required=True, readonly=True, domain="[('accounting_bank_id','=',accounting_bank_id)]"),
        'bank_id':fields.related('check_note_id','bank_id',type='many2one',relation='res.bank.entity',string='Banco', store=True, readonly=True),
        'min_lim':fields.related('bank_id','min_lim',type='integer',relation='res.bank.entity',string='Limite minimo (Bs.)',readonly=True,store=False),
        'max_lim':fields.related('bank_id','max_lim',type='integer',relation='res.bank.entity',string='Limite maximo (Bs.)',readonly=True,store=False),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'expiry':fields.related('company_id','expiry', type='integer',relation='res.company',string='Dias de Caducidad',readonly=True,store=True),
        'payee_id':fields.many2one('res.partner.address','Beneficiario',required=False, readonly=True),
        'partner_id':fields.many2one('res.partner','Contrapartida',required=True, readonly=True),
        'state': fields.selection([
            ('draft','Draft'), 
            ('open','Open'),
            ('done','Done'),
            ('cancel','Cancel'),
            ],'Estado', select=True, readonly=True, help="Estado del Cheque Voucher"),
        'wire':fields.char('Transferencia',size=26),
        'type': fields.selection([
            ('check','Cheque'),
            ('wire','Transferencia'),
            ],'Type', required=True, select=True),
        'bool_good': fields.boolean('Si se imprimio'),
        'bool_bad': fields.boolean('No se imprimio'),
        'bool_sure': fields.boolean('¿Estas Seguro?'),
        'notes':fields.char('Motivo',size=256, required=False, readonly=False ),
        'cancel_check_note': fields.selection([
            ('print','Error de Impresion')      ,
            ('perdida','Perdida o extravio')    ,
            ('dan_fis','Dano fisico')           ,
            ('pago','Pago no realizado')        ,
            ('devuelto','Cheque Devuelto')      ,
            ('caduco','Caduco')                 ,
            ('otros','Otros')                   ,
            ],'Motivo de Cancelacion', select=True, required=True),
        'amount':fields.float('Total a Pagar', readonly=True),
        'date':fields.date('Fecha', required=True),
        'period_id': fields.many2one('account.period', 'Periodo', required=True),
    }

   
    def action_cheque(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        created_account_voucher = []  
        account_voucher=self.pool.get('account.voucher')
        account_voucher_line=self.pool.get('account.voucher.line') 
        id=context["active_id"] 
        acount_voucher_id=account_voucher.search(cr, uid, [('voucher_pay_support_id','=',id)]) [0]
        obj_acount_voucher=account_voucher.browse(cr, uid, acount_voucher_id, context=None)
        
        voucher_pay_support=self.pool.get('voucher.pay.support')
        obj_voucher_pay_support=voucher_pay_support.browse(cr, uid, id, context=None)
        

        fecha=this.date
        periodo=this.period_id.id
        cancelar=this.cancel_check_note
        nota=this.notes
        if nota==False:
            cancelar1=" "
            if cancelar=="print":
                cancelar1="Error de Impresion"
            if cancelar=="perdida":
                cancelar1="Perdida o extravio"
            if cancelar=="dan_fis":
                cancelar1="Dano fisico"
            if cancelar=="pago":
                cancelar1="Pago no realizado"
            if cancelar=="devuelto":
                cancelar1="Cheque Devuelto"
            if cancelar=="caduco":
                cancelar1="Caduco" 
            name="ANULACION DE CHEQUE POR CONCEPTO %s - MOTIVO: %s"%(obj_acount_voucher.name,cancelar1)
            narration="ANULACION DE CHEQUE DE PAGO NUMERO %s - %s POR MOTIVO: %s"%(obj_acount_voucher.number,obj_acount_voucher.name,cancelar1)
        else:
            name="ANULACION DE CHEQUE POR CONCEPRO %s - MOTIVO: %s"%(obj_acount_voucher.name,nota)
            narration="ANULACION DE CHEQUE DE PAGO NUMERO %s - %s POR MOTIVO: %s"%(obj_acount_voucher.number,obj_acount_voucher.name,nota)   



        transitory=self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.transitory
        if transitory== True:   
            cuenta_transitoria=obj_voucher_pay_support.accounting_bank_id.trans_account_id   
            if cuenta_transitoria: #si hay cuenta transitoria
                #se crea el nuevo documento de comprobante diario
                account_voucher_id=account_voucher.create(cr, uid,{
                                'name': name                                                ,
                                'type': 'journal_voucher'                                   ,
                                'date': fecha                                               ,       
                                'journal_id':obj_acount_voucher.journal_id.id               , 
                                'account_id':obj_voucher_pay_support.accounting_bank_id.trans_account_id.id  ,
                                'period_id':obj_acount_voucher.period_id.id                 , 
                                'narration': narration                                      ,
                                'currency_id':obj_acount_voucher.currency_id.id             ,
                                'company_id': obj_acount_voucher.company_id.id              ,
                                'state':   'draft'                                          ,
                                'amount':obj_acount_voucher.amount                          ,
                                'reference_type': 'none'                                    ,  
                                'partner_id': obj_acount_voucher.partner_id.id              , 
                                'payee_id': obj_acount_voucher.payee_id.id                  ,                                                                                    
                                },context=None)  
                for line in obj_acount_voucher.payment_ids:    
                    account_voucher_line_id=account_voucher_line.create(cr, uid,{
                                    'voucher_id':account_voucher_id                   ,
                                    'name': line.name                                 ,
                                    'account_id': line.account_id.id                  ,       
                                    'partner_id': line.partner_id.id                  , 
                                    'amount': line.amount                             ,
                                    'type': 'cr'                                      , 
                                    'ref':line.ref                                    ,
                                    'account_analytic_id': line.account_analytic_id   ,                                                                                  
                                    },context=None)                     
                                                
                #xml_id = 'action_view_cont_voucher_form'
                xml_id = 'action_view_jour_voucher_form'
            else:
                raise osv.except_osv(_('Atencion !'), _('Debe de Ingresar la Cuenta Transitoria para el Banco: %s')%(obj_voucher_pay_support.accounting_bank_id.bank_id.name))
        

        
        else:#no hay cuentas transitorias
            #se crea el nuevo documento de comprobante diario
            account_voucher_id=account_voucher.create(cr, uid,{
                            'name': name                                        ,
                            'type': 'journal_voucher'                           ,
                            'date': fecha                                       ,       
                            'journal_id':obj_acount_voucher.journal_id.id       , 
                            'account_id':obj_acount_voucher.account_id.id       ,
                            'period_id':periodo                                 , 
                            'narration': narration                              ,
                            'currency_id':obj_acount_voucher.currency_id.id     ,
                            'company_id': obj_acount_voucher.company_id.id      ,
                            'state':   'draft'                                  ,
                            'amount':obj_acount_voucher.amount                  ,
                            'reference_type': 'none'                            ,  
                            'partner_id': obj_acount_voucher.partner_id.id      , 
                            'payee_id': obj_acount_voucher.payee_id.id          ,                                                                                    
                            },context=None)  

            for line in obj_acount_voucher.payment_ids:    
                account_voucher_line_id=account_voucher_line.create(cr, uid,{
                                'voucher_id':account_voucher_id                   ,
                                'name': line.name                                 ,
                                'account_id': line.account_id.id                  ,       
                                'partner_id': line.partner_id.id                  , 
                                'amount': line.amount                             ,
                                'type': 'cr'                                      , 
                                'ref':line.ref                                    ,
                                'account_analytic_id': line.account_analytic_id   ,                                                                                  
                                },context=None) 
            xml_id = 'action_view_jour_voucher_form'

        #se cambia el documento a estado a cancel
        voucher_pay_support.write(cr,uid,id,
                                  {'state' : 'cancel' , 
                                   'cancel_check_note': this.cancel_check_note , 
                                   'notes':this.notes, 
                                   'return_voucher_id':account_voucher_id})
        #se cambia el cheque a estado cancelado
        self.pool.get('check.note').write(cr,uid,obj_voucher_pay_support.check_note_id.id,{'state' : 'cancel', 'cancel_check_note':this.cancel_check_note, 'notes':this.notes })

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
