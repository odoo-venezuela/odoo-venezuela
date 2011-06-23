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
import time
######################Soporte de Pago##########################

class voucher_pay_support(osv.osv):
    _description = "voucher_pay_support"
    _name='voucher.pay.support'

    def _get_company_currency(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = (rec.company_id.currency_id.id,rec.company_id.currency_id.code)
        return result
      
    def _check_duplicar(self,cr,uid,ids):
        obj_soporte = self.browse(cr,uid,ids[0])
        cr.execute('select a.check_note_id  from voucher_pay_support a   where a.check_note_id=%d'%(obj_soporte.check_note_id))
        lista=cr.fetchall()
        #comprension de lista
        bandera=([x[0] for x in lista if x[0] == obj_soporte.check_note_id.id])
        #bandera devuelve una lista de las ocurrencias
        if  len(bandera)>1 :
            return False
        return True
    
    _columns={
        'name':fields.char('Acuse de Recibido',size=256, required=False, readonly=False ,
                    states={
                    'draft':[('readonly',False)]          ,
                    'open':[('readonly',True)]            ,
                    'done':[('readonly',True)]            ,
                    'cancel':[('readonly',True)]})        , 
        'accounting_bank_id':fields.many2one('res.bank','Cuenta Bancaria', readonly=True), 
        'check_note_id': fields.many2one('check.note', 'Cheque', readonly=True ,required=True, domain="[('accounting_bank_id','=',accounting_bank_id)]"),
        'bank_id':fields.related('check_note_id','bank_id',type='many2one',relation='res.bank.entity',string='Banco', store=True, readonly=True),
        'min_lim':fields.related('bank_id','min_lim',type='integer',relation='res.bank.entity',string='Limite minimo (Bs.)',readonly=True,store=False),
        'max_lim':fields.related('bank_id','max_lim',type='integer',relation='res.bank.entity',string='Limite maximo (Bs.)',readonly=True,store=False),
        'company_id': fields.many2one('res.company', 'Company', required=True , readonly=True),
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
            ],'Type', required=True, select=True , readonly=True),
        'amount':fields.float('Amount', readonly=True),
        'date':fields.date('Fecha de Emision', readonly=True),
        'cancel_check_note': fields.selection([
            ('print','Error de Impresion')      ,
            ('perdida','Perdida o extravio')    ,
            ('dan_fis','Dano fisico')           ,
            ('pago','Pago no realizado')        ,
            ('devuelto','Cheque Devuelto')      ,
            ('caduco','Caduco')                 ,
            ('otros','Otros')                   ,
            ],'Motivo de Cancelacion', select=True, readonly=True,
                        states={'draft':[('readonly',False)],
                        'open':[('readonly',False)]         ,
                        'cancel':[('readonly',True)]        ,
                        'done':[('readonly',True)]})        , 
        'notes':fields.char('Motivo',size=256, required=False, readonly=False ,
                        states={'draft':[('readonly',False)],
                        'open':[('readonly',False)]         ,
                        'cancel':[('readonly',True)]        ,
                        'done':[('readonly',True)]})        ,
        'return_voucher_id':fields.many2one('account.voucher','Comprobante de Anulación', readonly=True), 
        'account_voucher_id':fields.related('check_note_id','account_voucher_id',type='many2one',relation='account.voucher',string='Comprobante Origen',store=True,readonly=True), 
        'account_voucher_transitory_id':fields.many2one('account.voucher','Comprobante Transitorio', readonly=True), 
    
     }
     
     
    _constraints = [
        (_check_duplicar, 'Error ! Este Documento no se puede Duplicar', ['check_note_id']),
    ]
     
     
    def onchange_type(self, cursor, user, ids, type):
        if type:
            return {'value': {'wire': False,
                              'check_note_id': False,}}
        return False
     
     
    _defaults = {
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        'type': lambda *a: 'check', 
        'state': lambda *a: 'draft',
    }
    
    
    def get_retirado(self, cr, uid, ids, context={}):
        soporte = self.browse(cr,uid,ids)
        for i in soporte:
            if i.cancel_check_note or i.notes:
                raise osv.except_osv(_('Atencion !'), _('Retirar el motivo de Cancelacion'))
            else: 
                if i.name:
                    self.write(cr,uid,i.id,{'state' : 'open', 'name':i.name })
                else:
                    raise osv.except_osv(_('Atencion !'), _('Ingrese el Acuse de Recibido'))                 
                
                
    def get_realizado(self, cr, uid, ids, context={}):
        soporte = self.browse(cr,uid,ids)
        for i in soporte:
            #se cambia el documento a estado done
            self.write(cr,uid,i.id,{'state' : 'done' })     
            #se cambia el cheque a estado cobrado= done y la fecha de cobro
            self.pool.get('check.note').write(cr,uid,i.check_note_id.id,{'state' : 'done', 'date_done':time.strftime('%Y-%m-%d')})
            #se realiza el asiento contable, si existen cuentas transitorias
            transitory=self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.transitory
            if transitory== True:   
                cuenta_transitoria=i.accounting_bank_id.trans_account_id
                if cuenta_transitoria: # se llama al metodo que crear el soporte de pago
                    self.create_voucher(cr, uid, ids,i, context) 
                else:
                    raise osv.except_osv(_('Atencion !'), _('Debe de Ingresar la Cuenta Transitoria para el Banco: %s')%(i.accounting_bank_id.bank_id.name))
            
  
  
    def create_voucher(self, cr, uid, ids, soporte, context=None):
        this = self.browse(cr, uid, ids[0])
        created_account_voucher = []  
        account_voucher=self.pool.get('account.voucher')
        account_voucher_line=self.pool.get('account.voucher.line') 
        obj_acount_voucher=soporte.account_voucher_id
        name="COBRO DEL CHEQUE POR CONCEPTO %s"%(obj_acount_voucher.name)
        narration="COBRO DEL CHEQUE POR CONCEPTO %s"%(obj_acount_voucher.narration)
        
        print "las cuenta bancaria es:------------------", soporte.accounting_bank_id.bank_account_id.name
        print "las cuenta transitoria es:------------------", soporte.accounting_bank_id.trans_account_id.name 
        #se crea el nuevo documento de comprobante diario
        account_voucher_id=account_voucher.create(cr, uid,{
                        'name': name                                                ,
                        'type': 'cont_voucher'                                      ,
                        'date': time.strftime('%Y-%m-%d')                           ,       
                        'journal_id':obj_acount_voucher.journal_id.id               , 
                        'account_id':soporte.accounting_bank_id.bank_account_id.id  ,
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

        account_voucher_line_id=account_voucher_line.create(cr, uid,{
                        'voucher_id':account_voucher_id                             ,
                        'name': "Transitorio"                                       ,
                        'account_id': soporte.accounting_bank_id.trans_account_id.id,   
                        'amount': obj_acount_voucher.amount                         ,
                        'type': 'dr'                                                ,                                                                                  
                        },context=None) 
                        
        self.write(cr, uid, [soporte.id], {'account_voucher_transitory_id': account_voucher_id}) 
        return True 
    
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if not context:
            context={}
        return super(voucher_pay_support, self).write(cr, uid, ids, vals, context=context)
          
voucher_pay_support()
