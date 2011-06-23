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

class check_note(osv.osv):
    '''
    Hojas de la Chequera, Cheques (la lineas de la Chequera)
    '''
    _name='check.note'
   
    def _get_number(self, cr, uid, ids, field_name, arg, context):
        res={}
        notes= self.browse(cr,uid,ids)
        for note in notes:
        
            res[note.id] = str(note.prefix).rjust(4,'0') + str(note.suffix).rjust(4,'0')

        return res
 
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Atencion !'), _('No se puede duplicar este documento!!!'))
        return super(check_note, self).copy(cr, uid, id, {}, context)

    _columns={
    'check_book_id':fields.many2one('check.book','Chequera',required=False, readonly=True),
    'bank_id':fields.related('check_book_id','bank_id',type='many2one',relation='res.bank.entity',string='Banco',store=True, readonly=True),
    'accounting_bank_id':fields.related('check_book_id','accounting_bank_id', type='many2one',relation='res.bank',string='Cuenta Bancaria',store=True, readonly=True),
    'number': fields.function(_get_number, method=True, type='char', string='Numero de Cheque', size=8,
        store={
            'check.note': (lambda self, cr, uid, ids, c={}: ids, ['suffix','prefix'], 20),
        },),
    'suffix':fields.char('Sufijo', size=4,required=True),
    'prefix':fields.char('Prefijo', size=4,required=True),
    'notes':fields.char('Motivo',size=256, required=False, readonly=False ,
                    states={'draft':[('readonly',True)],
                    'review':[('readonly',True)]       ,
                    'assigned':[('readonly',False)]    ,
                    'hibernate':[('readonly',True)]    ,
                    'done':[('readonly',True)]         ,
                    'cancel':[('readonly',True)]       ,
                    'active':[('readonly',False)]})    ,  
    'account_voucher_id':fields.many2one('account.voucher','Account Voucher',required=False, readonly=True),
    'date_done':fields.date('Fecha de Cobro', readonly=True ),
    'cancel_check_note': fields.selection([
        ('print','Error de Impresion')      ,
        ('perdida','Perdida o extravio')    ,
        ('dan_fis','Dano fisico')           ,
        ('pago','Pago no realizado')        ,
        ('devuelto','Cheque Devuelto')      ,
        ('caduco','Caduco')                 ,
        ('otros','Otros')                   ,
        ],'Motivo de Cancelacion', select=True, readonly=True,
                    states={'draft':[('readonly',True)],
                    'review':[('readonly',True)]       ,
                    'assigned':[('readonly',False)]    ,
                    'hibernate':[('readonly',True)]    ,
                    'done':[('readonly',True)]         ,
                    'cancel':[('readonly',True)]       ,
                    'active':[('readonly',False)]})    , 
    'state': fields.selection([
            ('draft','Draft')               ,
            ('review','Review')             ,
            ('active','Active')             , 
            ('assigned','Assigned')           ,
            ('hibernate','Hibernate')       ,
            ('done','Done')                 ,
            ('cancel','Cancel')             ,
            ],'Estado', select=True, readonly=True, help="Estado del Check Note"),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    _rec_name='number'  
    
    def anular(self, cr, uid, ids, context={}):
        note_books = self.browse(cr,uid,ids)
        for note in note_books:
            if note.cancel_check_note=='otros' and note.notes==False:
                raise osv.except_osv(_('Atencion !'), _('Debe de ingresar el motivo de Cancelacion del Cheque en Otra Informacion')) 
            if note.cancel_check_note==False and note.notes==False:
                raise osv.except_osv(_('Atencion !'), _('Debe de ingresar el motivo de Cancelacion del Cheque en Otra Informacion')) 
            else:
                self.write(cr,uid,note.id,{'state' : 'cancel'})
check_note()
