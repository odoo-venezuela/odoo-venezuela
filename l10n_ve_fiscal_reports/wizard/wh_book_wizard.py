# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from osv import osv
from osv import fields
import sys
from tools.translate import _
import time


class wh_book_wizard(osv.osv_memory):
    """
    Withholding book wizard implemented using the osv_memory wizard system
    """
    _name = "wh.book.wizard"

    _columns = {
            "date_start": fields.date("Start Date", required=True),
            "date_end": fields.date("End Date", required=True),
            "model": fields.selection([
                        ("wh_p", _("Witholding Purchase")),
                        ("wh_s", _("Witholding Sales")),
                    ],"Type", required=True,
                ),
        }
        
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_start',  'date_end', 'model'])[0]
        return self._print_report(cr, uid, ids, data, context=context)

    def _print_report(self, cr, uid, ids,data, context=None):
        return { 'type': 'ir.actions.report.xml', 'report_name': 'fiscal.reports.whp.whp_seniat', 'datas': data}        
        
        
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
        'model': lambda *a: 'wh_p',
    }
wh_book_wizard()
