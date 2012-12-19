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
import addons

class wh_islr_config(osv.osv_memory):
    _name = 'wh.islr.config'
    _inherit = 'res.config'
    _description = __doc__

    def default_get(self, cr, uid, fields_list=None, context=None):
        defaults = super(wh_islr_config, self).default_get(cr, uid, fields_list=fields_list, context=context)
        logo = open(addons.get_module_resource('l10n_ve_withholding_islr', 'images', 'playa-medina.jpg'), 'rb')
        defaults['config_logo'] = base64.encodestring(logo.read())
        return defaults

    def _create_journal(self, cr, uid, name, type, code):
        self.pool.get("account.journal").create(cr, uid, { 
            'name': name,
            'type': type,
            'code': code,
            'view_id': 3,}
        )

    def _update_concepts(self, cr, uid, sale, purchase,context={}):
        concept_pool = self.pool.get("islr.wh.concept")
        concept_pool.write(cr, uid, concept_pool.search(cr, uid, [],context=context), {
            'property_retencion_islr_payable': purchase,
            'property_retencion_islr_receivable': sale
        },context=context)
        return True

    def _set_wh_agent(self, cr, uid):
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        self.pool.get('res.partner').write(cr, uid, [company.partner_id.id], {'islr_withholding_agent': True})

    def execute(self, cr, uid, ids, context=None):
        wiz_data = self.read(cr, uid, ids[0],context=context)
        if wiz_data['journal_purchase']:
            self._create_journal(cr, uid, wiz_data["journal_purchase"], 'islr_purchase', 'ISLRP')
        if wiz_data['journal_sale']:
            self._create_journal(cr, uid, wiz_data['journal_sale'], 'islr_sale', 'ISLRS')
        if wiz_data['account_sale'] or wiz_data['account_purchase']:
            self._update_concepts(cr, uid, wiz_data['account_sale'][0], wiz_data['account_purchase'][0],context=context)
        if wiz_data['wh_agent']:
            self._set_wh_agent(cr, uid)

    _columns = {
        'journal_purchase': fields.char("Journal Wh Income Purchase", 64, help="Journal for purchase operations involving Withholding Income"),
        'journal_sale': fields.char("Journal Wh Income Sale", 64, help="Journal for sale operations involving Withholding Income"),
        'account_purchase': fields.many2one(
            "account.account",
            "Account Withholding Income Purchase",
            help="Account for purchase operations involving Withholding Income"
        ),
        'account_sale': fields.many2one(
            "account.account",
            "Account Withholding Income Sale",
            help="Account for sale operations involving Withholding Income",
        ),
        'wh_agent': fields.boolean("Withholding Income Agent", help="Check if this company is a withholding income agent"),
    }

    _defaults = {
        'journal_purchase': _("Journal Withholding Income Purchase"),
        'journal_sale': _("Journal Withholding Income Sale"),
    }

wh_islr_config()
