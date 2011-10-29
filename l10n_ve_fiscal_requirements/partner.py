# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    Programmed by: Alexander Olivares <olivaresa@gmail.com>
#
#    This the script to connect with Seniat website 
#    for consult the rif asociated with a partner was taken from:
#    
#    http://siv.cenditel.gob.ve/svn/sigesic/ramas/sigesic-1.1.x/sigesic/apps/comun/seniat.py
#
#    This script was modify by:
#                   Javier Duran <javier@vauxoo.com>
#                   Miguel Delgado <miguel@openerp.com.ve>
#                   Israel Fermín Montilla <israel@openerp.com.ve>
#                   Juan Márquez <jmarquez@tecvemar.com.ve>
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
from tools.translate import _
import urllib
from xml.dom.minidom import parseString
import netsvc

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
    logger = netsvc.Logger()
    _columns = {
    'vat_apply': fields.boolean('Vat Apply', help="This field indicate if partner is subject to vat apply "),
    }

    '''
    Required Invoice Address
    '''
    def _check_partner_invoice_addr(self,cr,uid,ids,context={}):
        partner_obj = self.browse(cr,uid,ids[0])
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE':
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

    def vat_change_fiscal_requirements(self, cr, uid, ids, value, context=None):
        warning = {'Tittle':'Vat Error !','Message':'You try to put a VAT already existant !'}
        res = self.pool.get('res.partner').search(cr, uid, [('vat', '=', value)])
        if len(res)>=1:
            raise osv.except_osv(_('Vat Error !'),_('Invalid VAT. This vat is alredy used'))
        else:
            return super(res_partner,self).vat_change(cr, uid, ids, value, context=None)

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
    
#    Update Partner Information 

    def _load_url(self,retries,url):
        str_error= '404 Not Found'
        while retries > 0:
            try:
                s = urllib.urlopen(url)
                r = s.read()
                ok = not('404 Not Found' in r)
                if ok:
                    self.logger.notifyChannel("info", netsvc.LOG_INFO,
            "Url Loaded correctly %s" % url)
                    return r
            except:
                self.logger.notifyChannel("warning", netsvc.LOG_WARNING,
            "Url could not be loaded %s" % str_error)
                pass
            retries -= 1
        return str_error

    def _parse_dom(self,dom,rif,url_seniat):
        name = dom.childNodes[0].childNodes[0].firstChild.data 
        vat_apply = dom.childNodes[0].childNodes[2].firstChild.data.upper()=='SI' and True or False
        self.logger.notifyChannel("info", netsvc.LOG_INFO,
            "RIF: %s Found" % rif)
        if name.count('(') > 0:
            name = name[:name.index('(')].rstrip()
        return {'name': name,'vat_apply': vat_apply}

    def _print_error(self, error, msg):
        raise osv.except_osv(error,msg)

    def _eval_seniat_data(self,xml_data,context={}):

        if xml_data.find('450')>=0:
            if not 'all_rif' in context:
                self._print_error(_('Vat Error !'),_('Invalid VAT!'))
            else:
                return True

        if xml_data.find('452')>=0:
            if not 'all_rif' in context:
                self._print_error(_('Vat Error !'),_('Unregistered VAT!'))
            else:
                return True

        if xml_data.find("404")>=0:
            self._print_error(_('No Connection !'),_("Could not connect! Check the URL "))
            return True


    def _dom_giver(self, url1, url2, context, vat):
        xml_data = self._load_url(3,url1 % vat)
        if not self._eval_seniat_data(xml_data,context):
            dom = parseString(xml_data)
            return self._parse_dom(dom, vat, url2)
        else:
            return False

    def update_rif(self, cr, uid, ids, context={}):
        pool = self.pool.get('seniat.url')
        url_obj = pool.browse(cr, uid, pool.search(cr, uid, []))[0]
        url1 = url_obj.name + '%s'
        url2 = url_obj.url_seniat + '%s'
        if context.get('exec_wizard'):
            return self._dom_giver(url1, url2, context, context['vat'])
        for partner in self.browse(cr,uid,ids):
            if partner.vat:
                xml_data = self._load_url(3,url1 %partner.vat[2:])
                if not self._eval_seniat_data(xml_data,context):
                    dom = parseString(xml_data)
                    self.write(cr,uid,partner.id,self._parse_dom(dom,partner.vat[2:],url2))
                else:
                    return False
            else:
                if not 'all_rif' in context:
                    self._print_error(_('Vat Error !'),_('The field vat is empty'))
        return True

    def connect_seniat(self, cr, uid, ids, context={}, all_rif=False):
        if all_rif:
            ctx = context.copy()
            ctx.update({'all_rif': True})
        for partner in self.browse(cr,uid,ids):
            self.update_rif(cr, uid, [partner.id], context=ctx)
        return True

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
