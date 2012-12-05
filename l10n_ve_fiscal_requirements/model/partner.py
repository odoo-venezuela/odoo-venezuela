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
   
    _columns = {
        'seniat_updated': fields.boolean('Seniat Updated', help="This field indicates if partner was updated using SENIAT button"),
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
        if partner_obj.vat and partner_obj.vat[:2].upper() == 'VE':
                res = partner_obj.type == 'invoice'
                if res:
                    return True
                else:
                    return False
        else:
                return True
        return True

    def _check_vat_uniqueness_root(self, cr, uid, obj, name, partner_obj, args, context=None):
        
        if( partner_obj.parent_id is None ):
            return partner_obj

        return _check_vat_uniqueness_root(cr, uid, obj, name, partner_brw.parent_id, args, context=context)

    def _check_vat_uniqueness_tree(self, cr, uid, obj, name, partner_root, list_node_tree ,args, context=None):
               
        list_node_tree.append(partner_root)
        list_adjacent_node = partner_root.child_ids
        
        for node in list_adjacent_node:
            _check_vat_uniqueness_tree(cr, uid, obj, name, node, list_node_tree ,args, context=context)

        return list_node_tree

    def _check_vat_uniqueness_def(self, cr, uid, obj, name, current_vat,list_node_tree, args, context=None):
        nodes = self.browse(cr, uid, self.search(cr, uid, [('vat', '=', current_vat)]) )
        
        for node in nodes:
            if(node not in list_node_tree):
                return False
        
        return True

    def _check_vat_uniqueness(self, cr, uid, ids, context={}):
        #Check if its possible to use 'browse' in this 'read'
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
                
        if user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code != 'VE':
            return True

        partner_brw = self.browse(cr, uid,ids)
        current_vat = partner_brw[0].vat
        current_parent_id = partner_brw[0].parent_id
        
        if not current_vat:
            return True # Accept empty VAT's
        
        #Case b y d
        if not current_parent_id:
            duplicates = self.browse(cr, uid, self.search(cr, uid, [('vat', '=', current_vat),('parent_id','=',None)]))
            return duplicates is None
        
        currrent_is_company =partner_brw[0].is_company
        
        #Case c
        if(current_parent_id and not currrent_is_company):
            partner_root = _check_vat_uniqueness_root(cr, uid, obj, name, partner_brw[0], args, context=context)
            list_partner_tree = _check_vat_uniqueness_tree(cr, uid, obj, name, partner_root, [] ,args, context=context)
            return _check_vat_uniqueness_def(cr, uid, obj, name, current_vat,list_partner_tree ,args, context=context)

        return True    

    def _check_vat_mandatory(self, cr, uid, ids, context={}):
        
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        
        if user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code != 'VE':
            return True

        partner_brw = self.browse(cr, uid,ids)
        current_vat = partner_brw[0].vat
        current_parent_id = partner_brw[0].parent_id
        current_is_company =partner_brw[0].is_company
        
        if (current_is_company and current_parent_id):
            return False
        
        if not current_vat and not current_parent_id:
            return False
        
        current_type = partner_brw[0].type
       
        if ('invoice' in current_type and not current_vat and not current_is_company and current_parent_id):
            return False       
        
        <return True
    
    _constraints = [
        (_check_vat_mandatory, _("Error ! VAT is mandatory"), []),
        (_check_vat_uniqueness, _("Error ! Partner's VAT must be a unique value or empty"), []),
    ]
    
#    _constraints = [
#        
#        (_check_partner_invoice_addr, _('Error ! The partner does not have an invoice address.'), []),
#       
#    ]

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
