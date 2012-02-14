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

class update_info_partner(osv.osv_memory):
    """
    OpenERP osv memory wizard : update_info_partner
    """
    _name = 'update.info.partner'
    
    def update_info(self, cr, uid, ids, context={}):
        aux=[]
        res_part_obj = self.pool.get('res.partner')
        seniat_url_obj = self.pool.get('seniat.url')
        sql= '''SELECT vat FROM res_partner GROUP BY vat HAVING count(vat) > 1 ;'''
        cr.execute(sql)
        record = cr.dictfetchall()
        for r in record:
            aux.append(r.values()[0])
        es_partner_ids= res_part_obj.search(cr, uid, [('vat','not in',aux)])
        seniat_url_obj.connect_seniat(cr, uid, es_partner_ids, context,True)
        return{}

   
update_info_partner()
