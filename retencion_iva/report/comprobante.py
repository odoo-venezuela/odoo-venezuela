# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from osv import osv
import pooler

class rep_comprobante(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rep_comprobante, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_alicuota': self._get_alicuota,
            'get_tipo_doc': self._get_tipo_doc
        })

    def _get_partner_addr(self, idp=None):
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv 


    def _get_alicuota(self, tnom=None):
        if not tnom:
            return []

        tax_obj = self.pool.get('account.tax')
        tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])[0]
        tax = tax_obj.browse(self.cr,self.uid, tax_ids)

        return tax.amount*100


    def _get_tipo_doc(self, tipo=None):
        if not tipo:
            return []

        types = {'out_invoice': 'F', 'in_invoice': 'F', 'out_refund': 'C', 'in_refund': 'C'}

        return types[tipo]

    
      
report_sxw.report_sxw(
    'report.comprobante.retencion',
    'account.retention',
    'addons/retencion_iva/report/comprobante.rml',
    parser=rep_comprobante,
    header=False
)      
