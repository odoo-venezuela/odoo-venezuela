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

class search_info_partner_seniat(osv.osv_memory):
    
    _name = "search.info.partner.seniat"
    _columns = {
        'vat':fields.char('Numero de RIF', size=64, help='El RIF debe poseer el formato J1234567890',required=True),
        'name':fields.char('Empresa / Persona', size=256, help='Nombre de la Empresa'),
#        'vat_subjected':fields.boolean('Agente de Retencion', help='Es Agente de Retencion'),
        'wh_iva_rate':fields.float('Porcentaje de Retencion', help='Porcentaje de Retencion Aplicable'),
        'vat_apply':fields.boolean('Contribuyente Formal', help='Es Contribuyente'),
    }
    
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
        
    def search_partner_seniat(self, cr, uid, vat, context=None):
        if context is None:
            context={}
        su_obj = self.pool.get('seniat.url')
        rp_obj = self.pool.get('res.partner')
        url_obj = su_obj.browse(cr, uid, su_obj.search(cr, uid, []))[0]
        url1 = url_obj.name + '%s'
        url2 = url_obj.url_seniat + '%s'
        var_vat = self.read(cr,uid,vat,['vat'])
        if var_vat:
            aux = var_vat[0]['vat']
        res = su_obj._dom_giver(url1, url2, context, aux)
        res.update({'wh_iva_rate':self._buscar_porcentaje(aux,url2)})
        self.write(cr,uid,vat,res)
        
        return False
        
search_info_partner_seniat()
