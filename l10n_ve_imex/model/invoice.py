# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Vauxoo C.A. (http://openerp.com.ve/)
#    All Rights Reserved
############# Credits #########################################################
#    Coded by:  Juan Marzquez (Tecvemar, c.a.) <jmarquez@tecvemar.com.ve>
#               Katherine Zaoral               <katherine.zaoral@vauxoo.com>
#    Planified by:
#                Juan Marquez                  <jmarquez@tecvemar.com.ve>
#                Humberto Arocha               <hbto@vauxoo.com>
#    Audited by: Humberto Arocha               <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


class inherited_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'customs_form_id': fields.many2one(
            'seniat.form.86', 'Import file number', change_default=True,
            required=False, readonly=True,
            states={'draft': [('readonly', False)]}, ondelete='restrict',
            domain=[('state', '=', ('draft'))],
            help="The related form 86 for this import invoice (only draft)"),
    }

    def on_change_customs_form_id(self, cr, uid, ids, customs_form_id):
        res = {}
        if customs_form_id:
            imp = self.pool.get('seniat.form.86').browse(cr, uid,
                                                         customs_form_id,
                                                         context=None)
            res = {'value': {'num_import_form': imp.name,
                             'import_invo': imp.date_liq}}
        return res

    def test_open(self, cr, uid, ids, *args):
        so_brw = self.browse(cr, uid, ids, context={})
        for item in so_brw:
            if item.customs_form_id and \
                    item.customs_form_id.state in ('draft', 'cancel'):
                raise osv.except_osv(_('Error!'), _(
                    'Can\'t validate a invoice while the form 86 state\'s is \
                    cancel or draft (%s).\nPlease validate the form 86 first.')
                    % item.customs_form_id.name)
        return super(account_invoice, self).test_open(cr, uid, ids, args)

inherited_invoice()
