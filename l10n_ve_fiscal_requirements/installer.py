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
from tools.translate import _
import base64

class fiscal_requirements_config(osv.osv_memory):
    """
    Fiscal Requirements installer wizard
    """
    _name = 'fiscal.requirements.config'
    _inherit = 'res.config'
    _description= __doc__

    def execute(self, cr, uid, ids, context=None):
        pass

    _columns = {
        'name': fields.char('Name', 64, help="The commercial name of the company"),
        'vat': fields.char('VAT', 16, required=True, help='Partner\'s VAT to update the other fields'),
        'address': fields.char('Address', 256, help="Billing address"),
    }

    _defaults = {
        'name': "Polar",
        'vat': "B33R",
        'address': "Birrolandia",
    }
fiscal_requirements_config()
