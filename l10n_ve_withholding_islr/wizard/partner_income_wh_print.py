#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
import decimal_precision as dp


class partner_income_wh_printwizard(osv.TransientModel):

    """
    This wizard will print the islr reports for a given partner.
    """

    _name = 'partner.income.wh.print'
    _description = 'Partner Income Withholding Print'
    _columns = {
        'period_id': fields.many2one(
            'account.period',
            string='Period',
            required=True,
            help='Fiscal period to be use in the report.'),
        'partner_id': fields.many2one(
            'res.partner',
            string='Partner',
            required=True,
            help='Partner to be use in the report.'),
        'company_id': fields.many2one(
            'res.company',
            string='Company',
            required=True,
            help='Company'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: \
            self.pool.get('res.users').browse(cr, uid, uid,
                context=context).company_id.id,
    } 

    def print_report(self, cr, uid, ids, context=None):
        """
        """
        context = context or {}
        # TODO: dummy method, add some logic.
        #return action...
        return True
