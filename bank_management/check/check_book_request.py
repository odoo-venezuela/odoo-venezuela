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

class check_book_request(osv.osv):
    '''
    Modulo de Solicitud de Chequera
    '''
    _name='check.book.request'    
    _columns={
    'code': fields.char('Request Number', size=60, readonly=True),
    'accounting_bank_id':fields.many2one('res.partner.bank','Account Bank',required=True,
                          states={'draft':[('readonly',False)],
                                  'received':[('readonly',True)],
                                  'send':[('readonly',True)]}),
    'bank_id':fields.related('accounting_bank_id','bank',type='many2one',relation='res.bank',string='Bank',store=True,readonly=True,help='The bank entity name must be load when saved it'),
    'agen_id':fields.related('accounting_bank_id', 'name',type='char', size=30, string='Bank Agency', store=True, readonly=True, help='The Bank Agency name must be load when saved it'),
    'partner_id': fields.many2one('res.partner', 'Authorized',required=True,
                   states={'draft':[('readonly',False)],
                           'received':[('readonly',True)],
                           'send':[('readonly',True)]}),
    'check_book_ids': fields.one2many('check.book', 'check_book_request_id', 'Check Books',required=True,
                      states={'draft':[('readonly',False)],
                              'received':[('readonly',True)],
                              'send':[('readonly',True)]}),
    'state': fields.selection([
            ('draft','Draft'),
            ('send','Send'),
            ('received','Received'),
            ('cancel','Cancel'),
            ],'State', readonly=True, help="Request check book state"),
    }
    _rec_name='code' # esto es para no crear un atributo name
    _defaults = {
        'state': lambda *a: 'draft',
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'check.book.request'),
    }


    #cambia el estado del documento y se muestra el rml para impresion
    def get_enviar(self, cr, uid, ids, context={}):
        book_request = self.browse(cr,uid,ids)
        for request in book_request:
            self.write(cr,uid,request.id,{'state' : 'send'})

        return True

    #se cancelan las chequeras asociadas a la solicitud
    def get_anular(self, cr, uid, ids, context={}):
        book_request = self.browse(cr,uid,ids)
        for request in book_request:
            self.write(cr,uid,request.id,{'state' : 'cancel'})
            for book in request.check_book_ids: #por cada chequera
                self.pool.get('check.book').write(cr,uid,book.id,{ 'state' : 'cancel',
                                                                   'date_done' : time.strftime('%Y-%m-%d'),
                                                                   'notes' : 'Cancelacion de Chequera por Solicitud' })
        return True

    #cambia el estado del documento a received, el estado draft en chequera y fecha de recepcion
    def get_received(self, cr, uid, ids, context={}):
        book_request = self.browse(cr,uid,ids)
        for request in book_request:
            self.write(cr,uid,request.id,{'state' : 'received'}) 
            for c in request.check_book_ids: #para las chequeras
                self.pool.get('check.book').write(cr,uid,c.id,{'state' : 'draft', 'date_draft':time.strftime('%Y-%m-%d') }) 

        return True

    def onchange_accounting_bank_id(self, cr, uid, ids, accounting_bank_id): 
        boock = self.pool.get('check.book').search(cr, uid, [('accounting_bank_id','=',accounting_bank_id),
                                                              ('state', '=', 'request'),
                                                              ('check_book_request_id', '=', False)])
        result = {'value': {'check_book_ids': boock} }
        return result

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Warning !'), _('you can not duplicate this document!!!'))
        return super(check_book_request, self).copy(cr, uid, id, {}, context)
        
check_book_request()


class check_book(osv.osv):
    _inherit="check.book"
    _columns={
    'check_book_request_id':fields.many2one('check.book.request','Check Book Request', readonly=True, required=False), # OJOOOO despues se cambia a required=True para que la persona no elimine solicitudes asignadas a chequeras...
    }
check_book()
