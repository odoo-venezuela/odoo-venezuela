#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
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

class adjustment_book(osv.osv):

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for adj in self.browse(cr,uid,ids,context):
            res[adj.id] = {
                'amount_total': 0.0,
                'amount_untaxed_n_total' : 0.0,
                'amount_with_vat_n_total': 0.0,
                'amount_untaxed_i_total' : 0.0,
                'amount_with_vat_i_total': 0.0,
                'uncredit_fiscal_total'  : 0.0,
                'amount_with_vat_total'  : 0.0,
                'amount_base_total'  : 0.0,
                'amount_percent_total'  : 0.0,
            }
            for line in adj.adjustment_ids:
                res[adj.id]['amount_total'] += line.amount
                res[adj.id]['amount_untaxed_n_total'] += line.amount_untaxed_n
                res[adj.id]['amount_with_vat_n_total'] += line.amount_with_vat_n
                res[adj.id]['amount_untaxed_i_total'] += line.amount_untaxed_i
                res[adj.id]['amount_with_vat_i_total'] += line.amount_with_vat_i
                res[adj.id]['uncredit_fiscal_total'] += line.uncredit_fiscal
                res[adj.id]['amount_with_vat_total'] += line.amount_with_vat
            res[adj.id]['amount_base_total'] += adj.vat_general_i+adj.vat_general_add_i+adj.vat_reduced_i+adj.vat_general_n+\
                                     adj.vat_general_add_n+adj.vat_reduced_n+adj.adjustment+adj.no_grav+adj.sale_export
            res[adj.id]['amount_percent_total'] += adj.vat_general_icf+adj.vat_general_add_icf+adj.vat_reduced_icf+adj.vat_general_ncf+\
                                         adj.vat_general_add_ncf+adj.vat_reduced_ncf+adj.adjustment_cf+adj.sale_export_cf
            
        return res

    _name='adjustment.book'
    _columns={
    }

    
    
    #~ def action_set_totals(self,cr,uid,ids, *args):
        #~ self.write(cr, uid, ids, {'vat_general_i':0.00,
        #~ 'vat_general_add_i':0.00,'vat_reduced_i':0.00,
        #~ 'vat_general_n':0.00,'vat_general_add_n':0.00,
        #~ 'vat_reduced_n':0.00,'sale_export':0.00,
        #~ })
        #~ total={'amount_untaxed_n':0.0,'amount_untaxed_n_scdf':0.0,
               #~ 'amount_untaxed_i':0.0,'amount_untaxed_i_scdf':0.0,
               #~ 'vat_general_ncf':0.0,'vat_general_ncf':0.0,
               #~ 'vat_add_ncf':0.0}
#~ 
        #~ for adj in self.browse(cr, uid, ids):
            #~ if adj.type=='purchase':
                #~ self.write(cr, uid, ids, {'vat_general_i':adj.amount_untaxed_i_total,
                #~ 'vat_general_add_i':adj.amount_untaxed_i_total,
                #~ 'vat_reduced_i':adj.amount_untaxed_i_total,})
            #~ else:
                #~ self.write(cr, uid, ids, {'sale_export':adj.amount_untaxed_n_total,})
            #~ self.write(cr, uid, ids, {'vat_general_n':adj.amount_untaxed_n_total,
            #~ 'vat_general_add_n':adj.amount_untaxed_n_total,
            #~ 'vat_reduced_n':adj.amount_untaxed_n_total,
            #~ })
            #~ for line in adj.adjustment_ids:
                #~ 
                #~ if 0==line.percent_with_vat_n:
                    #~ total['amount_untaxed_n_scdf']+=line.amount_untaxed_n
                    #~ total['amount_untaxed_i_scdf']+=line.amount_untaxed_i
                #~ else:
                    #~ total['amount_untaxed_n']+=line.amount_untaxed_n
                    #~ total['amount_untaxed_i']+=line.amount_untaxed_i
                #~ if 12 == line.percent_with_vat_n:
                    #~ total['vat_general_ncf']+=12.0
                #~ if 8 == line.percent_with_vat_n:
                    #~ total['vat_reduced_ncf']+=8.0
                #~ if 22 == line.percent_with_vat_n:
                    #~ total['vat_additional_ncf']+=22.0
            #~ self.write(cr, uid, ids, {'vat_general_ncf':total['vat_general_ncf'],
            #~ 'vat_general_add_ncf':total['vat_general_ncf']+total['vat_add_ncf'],
            #~ 'vat_reduced_n':total['vat_reduced_n'],
            #~ })
        #~ return True
    
    
    
adjustment_book()
