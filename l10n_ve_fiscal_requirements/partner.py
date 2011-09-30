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


class res_partner_address(osv.osv):
    _inherit='res.partner.address'

    '''
    Invoice Address uniqueness check
    '''
    def _check_addr_invoice(self,cr,uid,ids,context={}):
        obj_addr = self.browse(cr,uid,ids[0])
        if obj_addr.partner_id.vat and obj_addr.partner_id.vat[:2].upper() == 'VE':
            if obj_addr.type == 'invoice':
                cr.execute('select id,type from res_partner_address where partner_id=%s and type=%s', (obj_addr.partner_id.id, obj_addr.type))
                res=dict(cr.fetchall())
                if (len(res) == 1):
                    res.pop(ids[0],False)
                if res:
                    return False
        return True


    _constraints = [
        (_check_addr_invoice, 'Error ! The partner already has an invoice address. ', [])
    ]

res_partner_address()


class res_partner(osv.osv):
    _inherit = 'res.partner'

    '''
    Required Invoice Address
    '''
    def _check_partner_invoice_addr(self,cr,uid,ids,context={}):
        partner_obj = self.browse(cr,uid,ids[0])
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE':
            #~ if hasattr(partner_obj, 'address') and partner_obj.address:
            if hasattr(partner_obj, 'address'):
                res = [addr for addr in partner_obj.address if addr.type == 'invoice']

                if res:
                    return True
                else:
                    return False
            else:

                return True
        return True


    _constraints = [
        (_check_partner_invoice_addr, 'Error ! The partner does not have an invoice address. ', [])
    ]



    def check_vat_ve(self, vat):
        '''
        Check Venezuelan VAT number, locally caled RIF.
        RIF: JXXXXXXXXX RIF CEDULA VENEZOLANO: VXXXXXXXXX CEDULA EXTRANJERO: EXXXXXXXXX
        '''
        if len(vat) != 10:
            return False
        if vat[0] not in ('J', 'V', 'E', 'G'):
            return False
        return True
    
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
