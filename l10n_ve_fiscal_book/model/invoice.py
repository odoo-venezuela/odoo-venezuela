#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#    Planified by: Nhomar Hernandez
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
from openerp.osv import osv, fields


class inherited_invoice(osv.osv):
    _inherit = "account.invoice"

    def _get_inv_number(self,cr,uid,ids,name,args,context=None):
        '''
        Get Invoice Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        if res:
            for r in res:
                ret.update({r.id : r.number and str(r.number) or ''})
        return ret

    def _get_total(self,cr,uid,ids,name,args,context=None):
        '''
        Get Total Invoice Amount
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:0})
        if res:
            for r in res:
                ret.update({ r.id : r.amount_total })
        return ret

    def _get_nro_inport_form(self, cr, uid,ids, name, args, context=None):
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        for r in res:
            if hasattr(r, 'num_import_form'):
                if r.num_import_form:
                    ret.pudate({r.id : r.num_import_form})
        return ret

    def _get_nro_inport_expe(self, cr, uid,ids, name, args, context=None):
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        for r in res:
            if hasattr(r, 'num_import_expe'):
                if r.num_import_expe:
                    ret.pudate({r.id : r.nro_inport_expe})
        return ret

    _columns = {
        'get_total': fields.function(_get_total, method=True, string='Invoice total', type='float',
                            help=""),
        'get_nro_inport_form': fields.function(_get_nro_inport_form, method=True, string='Import form number', type='char',
                            help=""),
        'get_nro_inport_expe': fields.function(_get_nro_inport_expe, method=True, string='Import file number', type='char',
                            help=""),

        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        #TODO: THIS FIELD TO BE CHANGED TO A STORABLE FUNCTIONAL FIELD
        #CHANGE EVEN FROM boolean to selection
        'issue_fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this invoice needs to be add'),
        'fb_submitted':fields.boolean('Fiscal Book Submitted?',
                help='Indicates if this invoice is in a Fiscal Book which has'\
                        ' being already submitted to the statutory institute'),
        'num_import_expe': fields.char('Import File number', 15,
            help="Import the file number for this invoice"),
        'num_import_form': fields.char('Import Form number', 15,
            help="Import the form number for this invoice"),
        }

inherited_invoice()
