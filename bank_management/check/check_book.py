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
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
import decimal_precision as dp

class check_book(osv.osv):
    '''
    Modulo encargado de crear las chequeras (cabeceras de los cheques)
    '''
    _name='check.book'
    
    
    def _get_qty_active(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para el calculo el numero de cheques disponibles
        '''
        res={}
        for i in self.browse(cr,uid,ids):
            res[i.id]=0
            cr.execute("SELECT COUNT(a.id)  FROM check_note a   WHERE a.state='active' AND a.check_book_id=%s"%(i.id))
            value=cr.fetchone()
            if value:
                res[i.id]=value[0]
        return  res       
        
    def _get_qty_check_selection(self, cr, uid, ids, field_name, arg, context):
        '''
        numero de cheques segun seleccion
        '''
        qty_chk = {
            '25': 25,
            '50': 50,
            '75': 75,
            '100': 100,
        }
        res={}
        for i in self.browse(cr,uid,ids):
            res[i.id] = qty_chk[i.qty_check_selection]
        return  res
   
    def _get_rate_user(self, cr, uid, ids, field_name, arg, context):
        '''
        funcion para el calculo el porcentaje de uso
        '''
        res={}
        for i in self.browse(cr,uid,ids):
            porcentaje=0.0
            cr.execute("SELECT COUNT(a.id)  FROM check_note a   WHERE a.state='active' AND a.check_book_id=%s"%(i.id))
            value=cr.fetchone()
            if value:
                qty_active=value[0]
            porcentaje=100*(1-(float(qty_active)/float(i.qty_check)))
            res[i.id]=porcentaje 
            if  qty_active==0 and i.state=="active": #si ya no existen cheques activos y el estado es activo (se acabaron los cheques de la chequera)
                #write el estado a done
                i.write({'state':"done"})
                #write date_done la fecha de cierre
                i.write({'date_done':time.strftime('%Y-%m-%d')})
        return  res


    def _get_chek_note(self, cr, uid, ids, context=None):
        result = {}
        for check in self.pool.get('check.note').browse(cr, uid, ids, context=context):
            result[check.check_book_id.id] = True
        return result.keys()

    _columns={
    'name':fields.char('Check Book', size=256,readonly=True),
    'accounting_bank_id':fields.many2one('res.partner.bank','Bank Account',required=True, readonly=True,
                        states={'request':[('readonly',False)],
                        'draft':[('readonly',True)],
                        'review':[('readonly',True)]}), 
    'bank_id':fields.related('accounting_bank_id','bank',type='many2one',relation='res.bank',string='Bank',store=True,readonly=True,help='The bank entity name must be load when saved it'),
    'from_suffix':fields.integer('From Suffix',  readonly=True,
                  states={'request':[('readonly',True)]  ,
                          'draft':[('readonly',False), ('required',True)],
                          'review':[('readonly',False), ('required',True)],
                          'active':[('readonly',True)]}) ,    
    'to_suffix':fields.integer('To Suffix',readonly=True),
    'state': fields.selection([
            ('request','Request'),
            ('draft','Draft'),
            ('review','Review'),
            ('active','Active'),
            ('done','Done'),
            ('hibernate','Hibernate'),
            ('cancel','Cancel'),
            ],'State', select=True, readonly=True, help="Check book state"),
    'qty_check_selection': fields.selection([
            ('25','25'),
            ('50','50'),
            ('75','75'),
            ('100','100'),
            ],'Check Qty', select=True, readonly=True, required=True,
            states={'request':[('readonly',False)],
                 'draft':[('readonly',True)],
                 'review':[('readonly',True)],
                 'hibernate':[('readonly',True)],
                 'done':[('readonly',True)],
                 'cancel':[('readonly',True)],
                 'active':[('readonly',True)]}),
    'qty_check':fields.function(_get_qty_check_selection, method=True, type='integer', string='Check'),
    'fixed_prefix': fields.boolean('Fixed Prefix?', help="If the prefix of the number of checks is constant check this option",
                    states={'request':[('readonly',True)],
                    'draft':[('readonly',False)],
                    'review':[('readonly',False)],
                    'hibernate':[('readonly',True)],
                    'cancel':[('readonly',True)],
                    'done':[('readonly',True)],
                    'active':[('readonly',True)]}),
    'prefix':fields.integer('Prefix', required=False,
                    states={'request':[('readonly',True)],
                    'draft':[('readonly',False)],
                    'review':[('readonly',False)],
                    'hibernate':[('readonly',True)],
                    'cancel':[('readonly',True)],
                    'done':[('readonly',True)],
                    'active':[('readonly',True)]}),
    'date_draft': fields.date('Date Received', readonly=True),
    'date_active': fields.date('Activation Date', required=False, readonly=True ),
    'date_done': fields.date('Closing Date', required=False, readonly=True ),
    'notes':fields.char('Note',size=256, required=False, readonly=False ,
                    states={'request':[('readonly',True)],
                    'draft':[('readonly',False)],
                    'review':[('readonly',False)],
                    'hibernate':[('readonly',False)],
                    'cancel':[('readonly',True)],
                    'active':[('readonly',False)]}),
    'cancel_check': fields.selection([
            ('perdida','Lost or misplaced'),
            ('dan_fis','Physical damage'),
            ('otros','Other'),
            ],'Reason for Cancellation', select=True,
                    states={'request':[('readonly',True)],
                    'draft':[('readonly',False)],
                    'review':[('readonly',False)],
                    'hibernate':[('readonly',False)],
                    'cancel':[('readonly',True)],
                    'done':[('readonly',True)],
                    'active':[('readonly',False)]}),
    'check_note_ids': fields.one2many('check.note', 'check_book_id', 'Checks',readonly=True,required=True,
                      states={'request':[('readonly',True)],
                              'draft':[('readonly',False)],
                              'review':[('readonly',False)],
                              'cancel':[('readonly',True)],
                              'active':[('readonly',True)]}),
    'qty_active':fields.function(_get_qty_active, method=True, type='integer', string='Available Checks',
             store={
                'check.book': (lambda self, cr, uid, ids, c={}: ids, ['check_note_ids', 'suffix', 'prefix'], 20),
                'check.note': (_get_chek_note, ['state'], 20),}),
    'rate_user': fields.function(_get_rate_user, method=True, type='float', digits_compute= dp.get_precision('Bank'), string='Use Rate',
             store={
                'check.book': (lambda self, cr, uid, ids, c={}: ids, ['check_note_ids', 'suffix', 'prefix', 'qty_active'], 20),
                'check.note': (_get_chek_note, ['state'], 20),}),
    }
    _defaults = {
        'state': lambda *a: 'request',
    }

    def _check_long(self,cr,uid,ids, field):
        obj = getattr(self.browse(cr,uid,ids[0]), field)
        if (obj <=9999) and (obj >= 0):
            return True
        return False

    def _check_from_suffix(self,cr,uid,ids):
        return self._check_long(cr,uid,ids,'from_suffix')

    def _check_prefix(self,cr,uid,ids):
        return self._check_long(cr,uid,ids,'prefix')

    def _check_qty_check(self,cr,uid,ids):
        obj = getattr(self.browse(cr,uid,ids[0]), 'qty_check')
        if obj>0:
            return True
        return False

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Atencion !'), _('you can not duplicate this document!!!'))
        return super(check_book, self).copy(cr, uid, id, {}, context)

    _constraints = [
        (_check_from_suffix, 'Error ! The field "Desde Sufijo" must be between 0000-9999.', ['from_suffix']),
        (_check_prefix, 'Error ! The field "Prefijo" must be between 0000-9999".', ['prefix']),
        (_check_qty_check, 'Error ! Check number must be greater than zero".', ['qty_check']),
    ]
    def load_check(self, cr, uid, ids, context={}):
        res={}
        books = self.browse(cr,uid,ids)
        for book in books:
            values = {}
            if (book.state=='draft') and (book.qty_check>0):
                if (book.fixed_prefix) and book.prefix: #si es constante el prefijo
                    values['prefix'] = str(book.prefix).rjust(4,'0')
                else:#si no es constante
                    values['prefix']=''
                for suffix in range(book.from_suffix,book.to_suffix + 1):
                    values.update({
                    'suffix': str(suffix).rjust(4,'0'),
                    'check_book_id': book.id,
                    })
                    self.pool.get('check.note').create(cr, uid, values)

        return True

    def _get_name_check(self, cr, uid, ids, context):
        '''
        funcion para obtener el nombre de la chequera concatenado. El campo va a ser la concatenacion de lo siguiente:
        Banco(nombre) + Cuenta(numero de la cuenta) + Fecha de recepcion(date_draft) + from + to.
        '''
        res={}
        for i in self.browse(cr,uid,ids):
            number = str(i.from_suffix).rjust(4,'0') + str(i.to_suffix).rjust(4,'0')
            name_check= i.bank_id.name +' '+i.accounting_bank_id.acc_number+' '+i.date_draft +' '+number
            res[i.id] = name_check
        return name_check
    
    def review(self, cr, uid, ids, context={}):
        #se calcula el to_suffix hasta
        books = self.browse(cr,uid,ids)
        for book in books:
            de_sufijo=book.from_suffix+int(book.qty_check)-1   
            self.write(cr,uid,book.id,{'to_suffix' : de_sufijo}) 
        #se cargan los cheques
        self.load_check(cr, uid, ids, context)
        #se cambia el nombre del cheque
        nombre=self._get_name_check(cr, uid, ids,context)
        self.write(cr,uid,book.id,{'name' : nombre})
        #se cambia de estado el documento
        books = self.browse(cr,uid,ids)
        for book in books:
            if book.fixed_prefix: #si es de prefijo es constante pasa de una vez a estado activo si no a review
                self.write(cr,uid,book.id,{'state' : 'active', 'date_active':time.strftime('%Y-%m-%d')}) 
                for k in book.check_note_ids:
                    self.pool.get('check.note').write(cr,uid,k.id,{'state' : 'active'})
            else: #no constante     
                self.write(cr,uid,book.id,{'state' : 'review'})
                for k in book.check_note_ids:
                    self.pool.get('check.note').write(cr,uid,k.id,{'state' : 'review'})

        return True

    #activar, la primera vez
    def active(self, cr, uid, ids, context={}):
        books = self.browse(cr,uid,ids)
        for book in books:
            self.write(cr,uid,book.id,{'state' : 'active'})
            self.write(cr,uid,book.id,{'date_active' : time.strftime('%Y-%m-%d')})
            for k in book.check_note_ids:
                self.pool.get('check.note').write(cr,uid,k.id,{'state' : 'active'})

        return True

    def hibernate(self, cr, uid, ids, context={}):
        books = self.browse(cr,uid,ids)
        for book in books:
            self.write(cr,uid,book.id,{'state' : 'hibernate'})
            for k in book.check_note_ids:
                if k.state=="active":#solo para los cheques activos
                    self.pool.get('check.note').write(cr,uid,k.id,{'state' : 'hibernate'})

        return True

    #para reactivar despues de hibernar
    def active_hibernate(self, cr, uid, ids, context={}):
        books = self.browse(cr,uid,ids)
        for book in books:
            self.write(cr,uid,book.id,{'state' : 'active'})
            for k in book.check_note_ids:
                if k.state=="hibernate":#solo para los cheques activos
                    self.pool.get('check.note').write(cr,uid,k.id,{'state' : 'active'})

        return True

    def anular(self, cr, uid, ids, context={}):
        books = self.browse(cr,uid,ids)
        for book in books:
            if book.cancel_check=='otros' and book.notes==False:
                raise osv.except_osv(_('Warning !'), _('Enter the Reason for Cancellation in other information field'))
            if book.cancel_check==False and book.notes==False:
                raise osv.except_osv(_('warning !'), _('Enter the Reason for Cancellation in other information field'))
            else:
                self.write(cr,uid,book.id,{'state' : 'cancel'})
                self.write(cr,uid,book.id,{'date_done' : time.strftime('%Y-%m-%d')})
                for k in book.check_note_ids:
                    if k.state=="active":#solo para los cheques activos
                        self.pool.get('check.note').write(cr,uid,k.id,{'state' : 'cancel'})

        return True

check_book()
