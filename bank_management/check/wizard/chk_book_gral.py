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
#              Javier Duran              <javieredm@gmail.com>             
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


class gral_check_book(osv.osv_memory):
    _name = "gral.check.book"
    _columns = {
        'check_book_id': fields.many2one('check.book', 'Check Book', required=False, readonly=False),
        'state_check_note': fields.selection([
            ('sin_filtro','Unfiltered'), 
            ('cobrado','Charged'),
            ('emitido','Issued')
            ],'Check Note State', readonly=False, help="Estado del Cheque en Voucher"),        
        'tiempo': fields.selection([('mes','Period'), ('fecha','Date')],'Time', readonly=False, help="Estado del Cheque en Voucher"),
        'desde': fields.date('Starting Date', required=False),
        'hasta': fields.date('Ending Date', required=False),
        'mes': fields.many2one('account.period', 'Period', required=False),        
        
    }
    _defaults = {
        'state_check_note': 'sin_filtro',
        'tiempo': 'fecha',
    }   
  
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, [])[0]
        data.update({'ids' : ids})
        return self._print_report(cr, uid, ids, data, context=context)
    
    def _print_report(self, cr, uid, ids, data, context=None):
        return {'type': 'ir.actions.report.xml', 'report_name': 'wizard.general.book', 'datas': data}
    
gral_check_book()


