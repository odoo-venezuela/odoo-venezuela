# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    
#
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
#
##############################################################################

from osv import fields, osv


class account_invoice(osv.osv):
    _inherit = 'account.invoice'    
    _columns = {
        'nro_ctrl': fields.char('Control Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Code used for intern invoice control"),
        'sin_cred': fields.boolean('Tax-exempt?', readonly=False, help="Set it true if the invoice is V.A.T. exempt"),
    }
account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
