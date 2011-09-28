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
import decimal_precision as dp
from tools.translate import _
import urllib
from xml.dom.minidom import parseString

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'wh_iva_agent': fields.boolean('Wh. Agent', help="Indicate if the partner is a withholding vat agent"),
        'wh_iva_rate': fields.float(string='Rate', digits_compute= dp.get_precision('Withhold'), help="Withholding vat rate"),
        'property_wh_iva_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Purchase withholding vat account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used debit withholding vat amount"),
        'property_wh_iva_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale withholding vat account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used credit withholding vat amount"),

    }
    _defaults = {
        'wh_iva_rate': lambda *a: 0,

    }

    def _load_url(self,retries,url):
        str_error= '404 Not Found'
        while retries > 0:
            try:
                s = urllib.urlopen(url)
                r = s.read()
                ok = not('404 Not Found' in r)
                if ok:
                    return r
            except:
                pass
            retries -= 1
        return str_error

    def _buscar_porcentaje(self,rif,url):
        '''
        Search percent of withholding connecting to SENIAT
        '''
        context={}
        html_data = self._load_url(3,url %rif)
        html_data = unicode(html_data, 'ISO-8859-1').encode('utf-8')
        self._eval_seniat_data(html_data,context)
        search_str='La condición de este contribuyente requiere la retención del '
        pos = html_data.find(search_str)
        if pos > 0:
            pos += len(search_str)
            pct = html_data[pos:pos+4].replace('%','').replace(' ','')
            return float(pct)
        else:
            return 0.0

    def _parse_dom(self,dom,rif,url_seniat):
        '''
        Parsing data from SENIAT
        '''
        name = dom.childNodes[0].childNodes[0].firstChild.data 
        wh_agent = dom.childNodes[0].childNodes[1].firstChild.data.upper()=='SI' and True or False
        vat_apply = dom.childNodes[0].childNodes[2].firstChild.data.upper()=='SI' and True or False
        wh_rate = self._buscar_porcentaje(rif,url_seniat)
        return {'name':name, 'wh_iva_agent':wh_agent,'vat_subjected':vat_apply,'wh_iva_rate':wh_rate}

    def _print_error(self, error, msg):
        raise osv.except_osv(error,msg)
    
    def _eval_seniat_data(self,xml_data,context={}):

        if xml_data.find('450')>=0:
            if not 'all_rif' in context:
                self._print_error(_('Vat Error !'),_('Invalid VAT!'))

        if xml_data.find('452')>=0:
            if not 'all_rif' in context:
                self._print_error(_('Vat Error !'),_('Unregistered VAT!'))

        if xml_data.find("404")>=0:
            if not 'all_rif' in context:
                self._print_error(_('No Connection !'),_("Could not connect! Check the URL "))
    
    def update_rif(self, cr, uid, ids, context={}):
        for partner in self.browse(cr,uid,ids):
            url1=partner.company_id.url_seniat1_company+'%s'
            url2=partner.company_id.url_seniat2_company+'%s'
            xml_data = self._load_url(3,url1 %partner.vat[2:])
            self._eval_seniat_data(xml_data,context)
            dom = parseString(xml_data)
            self.write(cr,uid,partner.id,self._parse_dom(dom,partner.vat[2:],url2))
        return True

    def connect_seniat(self, cr, uid, ids, context={}, all_rif=False):
        if all_rif:
            ctx = context.copy()
            ctx.update({'all_rif': True})
        for partner in self.browse(cr,uid,ids):
            self. update_rif(cr, uid, [partner.id], context=ctx)

        return True
    
res_partner()
