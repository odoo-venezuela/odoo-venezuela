#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import urllib
from xml.dom.minidom import parseString
import re
import logging

class seniat_url(osv.osv):
    """
    OpenERP Model : seniat_url
    """
    _name = 'seniat.url'
    _description = "Seniat config needed to run auto-config partner"
    logger = logging.getLogger('res.partner')
    _columns = {
        'name':fields.char('URL Seniat for Partner Information',size=255, required=True, readonly=False,help='In this field enter the URL from Seniat for search the fiscal information from partner'),
        'url_seniat':fields.char('URL Seniat for Retention Rate',size=255, required=True, readonly=False,help='In this field enter the URL from Seniat for search the retention rate from partner (RIF)'),
        'url_seniat2':fields.char('URL Seniat for Retention Rate',size=255, required=True, readonly=False,help='In this field enter the URL from Seniat for search the retention rate from partner (CI or Passport)'),
    }
    
    #    Update Partner Information 

    def _load_url(self,retries,url):
        str_error= '404 Not Found'
        while retries > 0:
            try:
                s = urllib.urlopen(url)
                r = s.read()
                ok = not('404 Not Found' in r)
                if ok:
                    self.logger.info("Url Loaded correctly %s" % url)
                    return r
            except:
                self.logger.warning("Url could not be loaded %s" % str_error)
                pass
            retries -= 1
        return str_error
    
    def _buscar_porcentaje(self,rif,url):
        context={}
        html_data = self.pool.get('seniat.url')._load_url(3,url %rif)
        html_data = unicode(html_data, 'ISO-8859-1').encode('utf-8')
        search_str='La condición de este contribuyente requiere la retención del '
        pos = html_data.find(search_str)
        if pos > 0:
            pos += len(search_str)
            pct = html_data[pos:pos+4].replace('%','').replace(' ','')
            return float(pct)
        else:
            return 0.0

    def _parse_dom(self,dom,rif,url_seniat,context={}):
        rif_aux = dom.childNodes[0].getAttribute('rif:numeroRif')
        name = dom.childNodes[0].childNodes[0].firstChild.data
        wh_agent = dom.childNodes[0].childNodes[1].firstChild.data.upper()=='SI' and True or False
        vat_subjected = dom.childNodes[0].childNodes[2].firstChild.data.upper()=='SI' and True or False
        self.logger.info("RIF: %s Found" % rif)
        if name.count('(') > 0:
            name = name[:name.index('(')].rstrip()
        return {'name': name,'vat_subjected': vat_subjected,'vat':'VE'+rif_aux,'wh_iva_agent':wh_agent}  

    def _print_error(self, error, msg):
        raise osv.except_osv(error,msg)

    def _eval_seniat_data(self,xml_data,vat,context={}):
        if context is None:
            context={}
        if not context.get('all_rif'):
            if xml_data.find('450')>=0 and not vat.find('450')>=0:
                self._print_error(_('Vat Error !'),_('Invalid VAT!'))
            elif xml_data.find('452')>=0 and not vat.find('452')>=0:
                self._print_error(_('Vat Error !'),_('Unregistered VAT!'))
            elif xml_data.find("404")>=0 and not vat.find('404')>=0:
                self._print_error(_('No Connection !'),_("Could not connect! Check the URL "))
            else:
                return False
        else:
            if xml_data.find('450')>=0 or xml_data.find('452')>=0 or xml_data.find("404")>=0:
                return True
            else:
                return False
    def _get_rif(self, vat, url1, url2, context=None):
        if context is None: context={}

        xml_data = self._load_url(3,url1 % vat)
        if not self._eval_seniat_data(xml_data,vat,context=context):
            dom = parseString(xml_data)
            return self._parse_dom(dom, vat, url2,context=context)

    def _dom_giver(self, url1, url2, url3, vat, context=None):
        if context is None: context={}

        if re.search(r'^[VJEG][0-9]{9}$', vat):
            '''Checked vat is a RIF'''
            return self._get_rif(vat, url1, url2, context=context)

        elif re.search(r'^([D][0-9]{9})$', vat):
            '''Checked vat is a Passport'''
            #TODO: NEEDS VALID NUMBERS TO CHECK THE VALIDITY AND COMPLETE THIS CODE
            return False

        elif re.search(r'^([VE][0-9]{1,8})$', vat):
            '''Checked vat is an ID'''
            xml_data = self._load_url(3,url3 % str(int(vat[1:])))
            vat = vat[1:].rjust(8,'0') 
            match2 = re.search(r'[VE]'+vat+'[0-9]{1}', xml_data)
            if re.search(r'No existe el contribuyente solicitado', xml_data):
                return False
            elif match2:
                vat = match2.group(0)
                return self._get_rif(vat, url1, url2, context=context)

    def _update_partner(self, cr, uid, id, context=None):
        rp_obj = self.pool.get('res.partner')
        rp_obj.write(cr, uid, id, {'seniat_updated': True})

    def update_rif(self, cr, uid, ids, context={}):
        aux=[]
        rp_obj = self.pool.get('res.partner')
        url_obj = self.browse(cr, uid, self.search(cr, uid, []))[0]
        url1 = url_obj.name + '%s'
        url2 = url_obj.url_seniat + '%s'
        url3 = url_obj.url_seniat2 + '%s'
        if context.get('exec_wizard'):
            res = self._dom_giver(url1, url2, url3, context['vat'],context=context)
            if res:
                self._update_partner(cr, uid, ids, context=context)
                return res
            else:
                return False
        for partner in rp_obj.browse(cr,uid,ids):
            if not partner.vat or partner.vat[:2]!='VE':
                continue
            rp_obj.write(cr, uid, partner.id, {'seniat_updated': False})
            res = self._dom_giver(url1, url2, url3,partner.vat[2:],context=context)
            if res:
                rp_obj.write(cr,uid,partner.id,res)
                self._update_partner(cr, uid, partner.id, context)
            else:
                if not context.get('all_rif'):
                    return False
                    #~ self._print_error(_('Error'),_("The RIF, CI or passport are not well constructed, please check \n The format of the RIF should be for example J1234567890,CI should be 12345678, and passports must be D123456789"))
        return True

    def connect_seniat(self, cr, uid, ids, context={}, all_rif=False):
        ctx = context.copy()
        if all_rif:
            ctx.update({'all_rif': True})
        self.update_rif(cr, uid, ids, context=ctx)
        return True

seniat_url()
