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
#                   Humberto Arocha <hbto@vauxoo.com>
#                   Yanina Aular <yanina.aular@vauxoo.com>
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
import re

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def default_get(self, cr, uid, fields, context=None):
        res = super(res_partner, self).default_get(cr, uid, fields, context=context)
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code == 'VE':
            res.update({'uid_country': 'VE'})
        return res

    _columns = {
        'seniat_updated': fields.boolean('Seniat Updated', help="This field indicates if partner was updated using SENIAT button"),
        'uid_country': fields.char("uid_country", size=20,readonly=True),
    }
    
    _default = {
        'seniat_updated': False,
    }

    def name_search(self,cr,uid,name='',args=[],operator='ilike',context=None,limit=80):
	    if context is None: 
	        context={}
	    ids= []
	    if len(name) >= 2:
	        ids = self.search(cr, uid, [('vat',operator,name)] + args, limit=limit, context=context)
	    if not ids:
	        ids = self.search(cr,uid,[('name',operator,name)] + args, limit=limit, context=context)
	    return self.name_get(cr,uid,ids,context=context)
    
    '''
    Required Invoice Address
    '''
    def _check_partner_invoice_addr(self,cr,uid,ids,context={}):
        partner_obj = self.browse(cr,uid,ids[0])
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE' and not partner_obj.parent_id:
                res = partner_obj.type == 'invoice'
                if res:
                    return True
                else:
                    return False
        else:
                return True
        return True

    def _check_vat_uniqueness_def(self, cr, uid, ids, current_vat,list_node_tree, context=None):
        if context is None: context = {}
        nodes = self.search(cr, uid, [] )
        nodes = list( set(nodes) - set(list_node_tree) )
        print nodes
        nodes = self.search(cr, uid, [('vat','=',current_vat),('id','in',nodes)] )
        return not nodes

    def _check_vat_uniqueness(self, cr, uid, ids, context=None):
        if context is None: context = {}
        
        print context
        
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        
        #User must be of VE        
        if user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code != 'VE':
            return True
       
        partner_brw = self.browse(cr, uid,ids)
        current_vat = partner_brw[0].vat
        current_parent_id = partner_brw[0].parent_id
        
        if not current_vat:
            return True # Accept empty VAT's
        
        #Partners without parent, must have RIF uniqueness
        if not current_parent_id:
            duplicates = self.browse(cr, uid, self.search(cr, uid, [('vat', '=', current_vat),('parent_id','=',None),('id','!=',partner_brw[0].id)]))
            return not duplicates
                
        currrent_is_company =partner_brw[0].is_company
        
        #Partners not are company type and have parent, can't have partners' RIF that are not part of its brothers or parent 
        if(current_parent_id and not currrent_is_company):
            list_nodes = current_parent_id.child_ids
            list_nodes = map(lambda x: x.id, list_nodes)
            list_nodes.append(current_parent_id)
            return self._check_vat_uniqueness_def(cr, uid, ids, current_vat, list_nodes , context=context)
        print "4"
        
        return True    

    def _check_vat_mandatory(self, cr, uid, ids, context=None):
        if context is None: context = {}
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        
        #User must be of VE
        if user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code != 'VE':
            return True
        
        partner_brw = self.browse(cr, uid,ids)
        current_vat = partner_brw[0].vat
        current_parent_id = partner_brw[0].parent_id
        current_is_company =partner_brw[0].is_company
        
        #Partners company type and with parent, not exists
        if (current_is_company and current_parent_id):
            return False
        
        #Partners with parent must have vat 
        if not current_vat and not current_parent_id:
            return False
        
        current_type = partner_brw[0].type
       
        #Partners invoice type that not be company and have parent, must have vat 
        if ('invoice' in current_type and not current_vat and not current_is_company and current_parent_id):
            return False       
        
        return True
    
    _constraints = [
        (lambda s, *a, **k: s._check_vat_mandatory(*a, **k), _("Error ! VAT is mandatory"), []),
        (lambda s, *a, **k: s._check_vat_uniqueness(*a, **k), _("Error ! Partner's VAT must be a unique value or empty"), []),
        #~ (_check_partner_invoice_addr, _('Error ! The partner does not have an invoice address.'), []),
    ]
 
    def vat_change_fiscal_requirements(self, cr, uid, ids, value, context=None):
        if context is None:
            context={}
        if not value:
            return super(res_partner,self).vat_change(cr, uid, ids, value, context=context)
        res = self.search(cr, uid, [('vat', 'ilike', value)])
        if res:
            rp = self.browse(cr, uid, res[0],context=context)
            return {'warning':  {
                                'title':_('Vat Error !'),
                                'message':_('The VAT [%s] looks like '%value + 
                                            '[%s] which is'%rp.vat.upper()+
                                            ' already being used by: %s'%rp.name.upper())
                                }
                   }
        else:
            return super(res_partner,self).vat_change(cr, uid, ids, value, context=context)

    def check_vat_ve(self, vat, context = None):
        '''
        Check Venezuelan VAT number, locally called RIF.
        RIF: JXXXXXXXXX RIF VENEZOLAN IDENTIFICATION CARD: VXXXXXXXXX FOREIGN IDENTIFICATION CARD: EXXXXXXXXX
        '''
        
        if context is None:
            context={}
        if re.search(r'^[VJEG][0-9]{9}$', vat):
            return True
        if re.search(r'^([VE][0-9]{1,8}|[D][0-9]{9})$', vat):
            return True
        return False
        
    def update_rif(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        su_obj = self.pool.get('seniat.url')
        return su_obj.update_rif(cr, uid, ids, context=context)

    def button_check_vat(self, cr, uid, ids, context=None):
        if context is None: context = {}
        context.update({'update_fiscal_information':True})
        super(res_partner, self).button_check_vat(cr, uid, ids, context=context)
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if user_company.vat_check_vies:
            # force full VIES online check
            self.update_rif(cr, uid, ids, context=context)
        return True 
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
