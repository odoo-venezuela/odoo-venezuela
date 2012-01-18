#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
#
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
#
##############################################################################
import wizard
import pooler
from osv import osv, fields
from tools.translate import _
import urllib
from xml.dom.minidom import parseString
import netsvc

class search_info_partner_seniat(osv.osv_memory):
    
    _name = "search.info.partner.seniat"
    _columns = {
        'name':fields.char('Numero de RIF', size=64, help='El RIF debe poseer el formato J1234567890',required=True),
        'vat_name':fields.char('Empresa / Persona', size=256, help='Nombre de la Empresa'),
        'vat_agent':fields.boolean('Agente de Retencion', help='Es Agente de Retencion'),
        'percent':fields.float('Porcentaje de Retencion', help='Porcentaje de Retencion Aplicable'),
        'vat_apply':fields.boolean('Contribuyente Formal', help='Es Contribuyente'),
    }
    
    logger = netsvc.Logger()
    
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

    def _parse_dom(self,dom,rif,url_seniat):
        name = dom.childNodes[0].childNodes[0].firstChild.data
        vat_agent = dom.childNodes[0].childNodes[1].firstChild.data.upper()=='SI' and True or False
        vat_apply = dom.childNodes[0].childNodes[2].firstChild.data.upper()=='SI' and True or False
        self.logger.notifyChannel("info", netsvc.LOG_INFO,
            "RIF: %s Found" % rif)
        if name.count('(') > 0:
            name = name[:name.index('(')].rstrip()
        return {'vat_name': name,'vat_apply': vat_apply, 'vat_agent':vat_agent}
    
    def _buscar_porcentaje(self,rif,url):
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
    
    def _dom_giver(self, url1, url2, context, vat):
        xml_data = self._load_url(3,url1 % vat)
        if not self._eval_seniat_data(xml_data,context):
            dom = parseString(xml_data)
            return self._parse_dom(dom, vat, url2)
        else:
            return False
        
    def search_partner_seniat(self, cr, uid, vat, context=None):
        pool = self.pool.get('seniat.url')
        var_vat = self.read(cr,uid,vat,['name'])
        context.update({'vat':var_vat and var_vat[0] and var_vat[0]['name'] or []})
        if not context['vat']:
            self._print_error(_('Vat Error !'),_('The field vat is empty'))
        else:
            url_obj = pool.browse(cr, uid, pool.search(cr, uid, []))[0]
            url1 = url_obj.name + '%s'
            url2 = url_obj.url_seniat + '%s'
            res = self._dom_giver(url1, url2, context, context['vat'])
            if res:
                percent = self._buscar_porcentaje(context['vat'],url2)
                res.update({'percent':percent, 'name':var_vat[0]['name']})
                context.update(res)
                self.write(cr,uid,vat,res)
            else:
                return False
        res_id = self.pool.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_vat_return')])
        resource_id = self.pool.get('ir.model.data').read(cr, uid, res_id, fields=['res_id'])[0]['res_id']
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'search.info.partner.seniat',
            'views': [(resource_id,'form')], #Comentar en caso de que no funcione
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': context,
            #~ 'ref': 'search_info_partner_seniat.view_vat_return', 
            'res_id': vat and vat[0] or [],
        }
        
search_info_partner_seniat()
