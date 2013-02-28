#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
################################################################################

from openerp.osv import fields, osv
import time

__TYPES__ =[('sale', 'Sale'),
        ('sale_refund','Sale Refund'), 
        ('purchase', 'Purchase'), 
        ('purchase_refund','Purchase Refund'), 
        ('cash', 'Cash'), 
        ('bank', 'Bank and Cheques'), 
        ('general', 'General'), 
        ('situation', 'Opening/Closing Situation'),
        ('sale_debit', 'Sale Debit'),
        ('purchase_debit', 'Purchase Debit'),
        ('iva_sale', 'Sale Wh VAT'), 
        ('iva_purchase', 'Purchase Wh VAT'), 
        ('islr_purchase', 'Purchase Wh Income'), 
        ('islr_sale', 'Sale Wh Income'), 
        ('mun_sale', 'Sale Wh County'), 
        ('mun_purchase', 'Purchase Wh County'),
        ('src_sale', 'Sale Wh src'), 
        ('src_purchase', 'Purchase Wh src')]

class account_journal(osv.osv):
    _inherit = 'account.journal'
    
    _columns = {'type': fields.selection(__TYPES__,  'Type', size=32, required=True, 
            help =  "Select 'Sale' for customer invoices journals."\
                    " Select 'Purchase' for supplier invoices journals."\
                    " Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments."\
                    " Select 'General' for miscellaneous operations journals."\
                    " Select 'Opening/Closing Situation' for entries generated for new fiscal years."\
                    " Select 'Sale Debit' for customer debit note journals."\
                    " Select 'Purchase Debit' for supplier debit note journals."
                    " Select 'Sale Wh VAT' for customer vat withholding journals."
                    " Select 'Purchase Wh VAT' for supplier vat withholding journals."
                    " Select 'Sale Wh Income' for customer income withholding journals."
                    " Select 'Purchase Wh Income' for supplier income withholding journals."
                    " Select 'Sale Wh County' for customer municipal withholding journals."
                    " Select 'Purchase Wh County' for supplier municipal withholding journals."
                    " Select 'Sale Wh SRC' for customer social withholding journals."
                    " Select 'Purchase Wh SRC' for supplier social withholding journals."
                    )
        }

account_journal()

class account_period(osv.osv):
    _inherit = "account.period"

    def find_fortnight(self, cr, uid, dt=None, context=None):
        '''
        This Function returns a tuple composed of 
            *) period for the asked dt (int)
            *) fortnight for the asked dt (boolean):
                -) False: for the 1st. fortnight
                -) True: for the 2nd. fortnight.
            Example:
            (3,True) => a period whose id is 3 in the second fortnight
        '''
        if context is None: context = {}
        if not dt:
            dt = time.strftime('%Y-%m-%d')
        period_ids = self.find(cr,uid,dt=dt,context=context)
        period_ids = self.search(cr,uid,[('special','=',False),('id','in',period_ids)])
        if not period_ids:
            raise osv.except_osv(_('Error !'), _('No period defined for this date: %s !\nPlease create a fiscal year.')%dt)
        
        fortnight= False if int(dt.split('-')[2]) <= 15 else True
        return (period_ids[0],fortnight)
account_period()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
