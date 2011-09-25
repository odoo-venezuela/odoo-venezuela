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

from osv import fields, osv
import tools
from tools.translate import _
from tools import config

class voucher_pay_support_wizard(osv.osv_memory):
    _name = "voucher.pay.support.wizard"
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
            ],'Motivo de Cancelacion', select=True),
        'amount':fields.float('Total a Pagar', readonly=True),
        'date':fields.date('Date', readonly=True),
    }

    def accion_tipo(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        tipo=this.type
        obj_model = self.pool.get('ir.model.data')
        if tipo=="check":
            model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_voucher_pay_support_wizard_check')])
        else: #cuando se trata de transferencia
            model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_voucher_pay_support_wizard_transf')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'voucher.pay.support.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
        accion_cheque

    
    def action_cheque(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        obj_model = self.pool.get('ir.model.data')
        check_book = self.pool.get('check.book') 
        check_note = self.pool.get('check.note')   
        che_b= check_book.search(cr, uid, [('accounting_bank_id','=',this.accounting_bank_id.id), ('state','=',"active")], limit = 1)  
        if che_b:
            che_n= check_note.search(cr, uid, [('check_book_id','=',che_b[0]), ('state','=',"active")], limit = 1)
        else:
            raise osv.except_osv(_('Atencion !'), _('No existen cheques en esta cuenta, ingrese otra!!!'))   
        id=context["active_id"]
        a_v=self.pool.get('account.voucher')
        obj_account_v=a_v.browse(cr, uid, id, context=None)  
        context.update({'accounting_bank_id': this.accounting_bank_id.id})
        context.update({'bank_id':  this.accounting_bank_id.bank_id.id})
        context.update({'check_note_id': che_n[0]})
        context.update({'payee_id': obj_account_v.payee_id.id})
        context.update({'partner_id': obj_account_v.partner_id.id})
        context.update({'company_id': obj_account_v.company_id.id})
        context.update({'account_voucher_id': obj_account_v.id}) #este se utilza al final en la generacion del asiento contable 
        context.update({'amount': obj_account_v.amount})
        context.update({'date': obj_account_v.date})   
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_voucher_pay_support_wizard_generar_cheque')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'voucher.pay.support.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'domain': str([
                            ('accounting_bank_id', '=', this.accounting_bank_id.id)   ,
                            ('bank_id', '=', this.accounting_bank_id.bank_id.id)      ,
                            ('check_note_id', '=', che_n[0])                          ,
                            ('partner_id', '=', obj_account_v.partner_id.id)          ,
                            ('payee_id', '=', obj_account_v.payee_id.id)              ,
                            ('amount', '=', obj_account_v.amount)                     ,
                            ('date', '=', obj_account_v.date)])               
        }

    def pop_check_printer(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_voucher_pay_support_wizard_preguntar')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'voucher.pay.support.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        } 
   
    def pop_check(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        created_account_voucher = []  
        if this.bool_sure: #si selecciono la opcion estas seguro?
            if this.bool_bad: #si el cheque esta malo
                vista="view_voucher_pay_support_wizard_escribir_nota" #muestra la interface para escribir la razon en la nota
            else: #si el cheque esta bien
                if this.bool_bad==False and this.bool_good == False: #no selecciono ninguna opcion
                    raise osv.except_osv(_('Atencion !'), _('Ingrese al menos una opcion!!!'))
                check_note = self.pool.get('check.note') 
                payee_id = self.pool.get('res.partner.address')
                accounting_bank_id = self.pool.get('res.bank')
                bank_id = self.pool.get('res.bank.entity') 
                contrapartida = self.pool.get('res.partner') 
                compania = self.pool.get('res.company')
                account_voucher = self.pool.get('account.voucher')
                

                obj_check_note=check_note.browse(cr, uid, context["check_note_id"], context=None)
                try:
                    obj_payee_id=payee_id.browse(cr, uid, context["payee_id"], context=None)
                    payee=obj_payee_id.id
                except:
                    payee=False   
                obj_accounting_bank_id=accounting_bank_id.browse(cr, uid, context["accounting_bank_id"], context=None)
                obj_bank_id= bank_id.browse(cr, uid, context["bank_id"], context=None)
                obj_contrapartida=contrapartida.browse(cr, uid, context["partner_id"], context=None)
                obj_compania=compania.browse(cr, uid, context["company_id"], context=None)
                obj_account_voucher=account_voucher.browse(cr, uid, context["account_voucher_id"], context=None)
                #se hace el cambio (WRITE) del estado del cheque (asignado)
                obj_check_note.write({'state':"assigned"}) 
                #Se crea el documento (CREATE) voucher.pay.support con los datos "Soporte de Pago"
                voucher_pay=self.pool.get('voucher.pay.support')
                voucher_pay_id=voucher_pay.create(cr, uid,{
                                'check_note_id':obj_check_note.id                ,
                                'company_id': obj_compania.id                    ,
                                'partner_id': obj_contrapartida.id               ,       
                                'type': 'check'                                  , 
                                'amount': context["amount"]                      ,
                                'date': context["date"]                          ,
                                'payee_id':payee                                 , 
                                'accounting_bank_id':obj_accounting_bank_id.id   ,
                                                                                         
                                },context=None)  
                ids2=[]
                ids2.append(context["account_voucher_id"])      
                #Se guarda el account_voucher
                obj_account_voucher.write({'voucher_pay_support_id':voucher_pay_id})
                #Se escribe el diario y la cuenta contable en el modelo accout_voucher
                #cuando existen cuentas transitorias
                transitory=self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.transitory
                if transitory== False: 
                    obj_account_voucher.write({'account_id':obj_accounting_bank_id.bank_account_id.id, 'journal_id': obj_accounting_bank_id.journal_id.id })
                else: #cuenta transitoria
                    cuenta_transitoria=obj_accounting_bank_id.trans_account_id
                    if cuenta_transitoria:
                        obj_account_voucher.write({'account_id':obj_accounting_bank_id.trans_account_id.id, 'journal_id': obj_accounting_bank_id.journal_id.id })
                    else:
                        raise osv.except_osv(_('Atencion !'), _('Debe de Ingresar la Cuenta Transitoria para el Banco: %s')%(obj_accounting_bank_id.bank_id.name))
                    
                #Se hace un write de check_note el campo account_voucher_id
                obj_check_note.write({'account_voucher_id':obj_account_voucher.id})          
                #Se dispara el proceso de contabilizacion de voucher, asientos contables
                account_voucher.proforma_voucher(cr, uid,  ids2)
                #Se redirecciona laventana al tree
                mod_obj = self.pool.get('ir.model.data')
                act_obj = self.pool.get('ir.actions.act_window')
                xml_id = 'action_pay_order_wizard_soporte'
                result = mod_obj._get_id(cr, uid, 'voucher_pay_support', xml_id) 
                id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
                result = act_obj.read(cr, uid, id)
                created_account_voucher.append(voucher_pay_id)
                result['res_id'] = created_account_voucher
                return result           
        else: #si no selecciono la opcion estas seguro?
            vista="view_voucher_pay_support_wizard_preguntar"
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=',vista)])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'voucher.pay.support.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }   
 
    def fin_check(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        nota=this.notes
        check_note = self.pool.get('check.note') 
        accounting_bank_id = self.pool.get('res.bank')
        bank_id = self.pool.get('res.bank.entity') 
        account_voucher = self.pool.get('account.voucher')
        obj_check_note=check_note.browse(cr, uid, context["check_note_id"], context=None)
        obj_accounting_bank_id=accounting_bank_id.browse(cr, uid, context["accounting_bank_id"], context=None)
        obj_bank_id= bank_id.browse(cr, uid, context["bank_id"], context=None)
        obj_account_voucher=account_voucher.browse(cr, uid, context["account_voucher_id"], context=None)
        bandera=True
        this = self.browse(cr, uid, ids[0])
        tipo=this.cancel_check_note
        nota=this.notes
        if tipo=='otros' and nota==False:
            bandera=False
        if tipo==False and nota==False:
            bandera=False 
        if bandera==False:
            ventana="view_voucher_pay_support_wizard_escribir_nota"       
        else:#si todo lo ingreso bien
            #Se cambia (WRITE) el estado del cheque a Cancel 
            obj_check_note.write({'cancel_check_note':tipo, 'notes':nota})
            #Se cambia (WRITE) la nota de justificacion de la perdida del cheque 
            obj_check_note.write({'state':'cancel'})
            #Se hace un write de check_note el campo account_voucher_id
            obj_check_note.write({'account_voucher_id':obj_account_voucher.id})
            ventana="view_voucher_pay_support_wizard_check"
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=',ventana)])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'voucher.pay.support.wizard',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }   
voucher_pay_support_wizard()
