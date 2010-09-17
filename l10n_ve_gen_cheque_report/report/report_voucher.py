##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
#
##############################################################################

import time
from report import report_sxw
from tools import amount_to_text_en
from numero_a_texto import Numero_a_Texto


class report_cheque(report_sxw.rml_parse):
    total = 0.0
    def __init__(self, cr, uid, name, context):
        super(report_cheque, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_total':self._get_tot,
            'get_partner':self._get_partner,
            'get_partner_city': self._get_partner_city,
            'obt_texto':self.obt_texto
        })

    
    def _get_partner(self, move_ids):
        for move in move_ids:#self.pool.get('account.move.line').browse(self.cr, self.uid, move_ids):
            self.total +=move.amount
        return '**** '+move.partner_id.name+' ****'

    def _get_tot(self): 
        return self.total

    def _get_partner_city(self, idp=None):
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = addr.city or ''
        return addr_inv + '    '

    def obt_texto(self,cantidad):
        res=Numero_a_Texto(cantidad)
        return res
    
report_sxw.report_sxw(
    'report.account.cheque_ve',
    'account.voucher',
    'addons/l10n_ve_gen_cheque_report/report/report_voucher.rml',
    parser=report_cheque,header=False
)
