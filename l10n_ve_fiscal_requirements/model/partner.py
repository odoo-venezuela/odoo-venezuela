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

from openerp.osv.orm import except_orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
import re

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _get_country_code(self, cr, uid, context=None):
		'''
		This function return the country code
		of the user company. If not exists, 
		return XX.
		'''
        context = context or {}
        user_company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        return user_company.partner_id and user_company.partner_id.country_id \
                and user_company.partner_id.country_id.code or 'XX'

    def default_get(self, cr, uid, fields, context=None):
        '''
		This function load the country code
		of the user company to form to be
		created.
        '''
        context = context or {}
        res = super(res_partner, self).default_get(cr, uid, fields, context=context)
        res.update({'uid_country': self._get_country_code(cr,uid,context=context)})
        return res

    def _get_uid_country(self, cr, uid, ids, field_name, args, context=None):
        '''
		This function returns a dictionary of key 
		ids as invoices, and value the country code
		of the user company.
        '''
        context = context or {}
        res= {}.fromkeys(ids,self._get_country_code(cr,uid,context=context))
        return res
    
    _columns = {
        'seniat_updated': fields.boolean('Seniat Updated', help="This field indicates if partner was updated using SENIAT button"),
        'uid_country': fields.function(_get_uid_country, type='char', string="uid_country", size=20, help="country code of the current company"),
    }
    
    _default = {
        'seniat_updated': False,
    }

    def name_search(self,cr,uid,name='',args=[],operator='ilike',context=None,limit=80):
	    '''
		This function gets el id of the partner
		with the vat or the name and return the
		name
	    '''
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
        '''
		This function returns true if the partner
		is a company of Venezuela and if the
		address is for billing.
        '''
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
        '''
		This function receiving nodes in the tree 
		that are not members of the current partner
		level, and the remainder of the assembly 
		to ensure that the partner at the same
		level as the current vat has different.
        '''
        
        if context is None: context = {}
        nodes = self.search(cr, uid, [] )
        nodes = list( set(nodes) - set(list_node_tree) )
        nodes = self.search(cr, uid, [('vat','=',current_vat),('id','in',nodes)] )
        return not nodes

    def _check_vat_uniqueness(self, cr, uid, ids, context=None):
		'''
		This function check that the vat is unique
		in the level where the partner in the tree
		'''
        if context is None: context = {}
        
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        
        #User must be of VE        
        if not (user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code == 'VE'):
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
        
        #Partners that are not company and have parent_id, can't have partners' RIF that are not part of its siblings or parent 
        if(current_parent_id and not currrent_is_company):
            list_nodes = current_parent_id.child_ids
            list_nodes = map(lambda x: x.id, list_nodes)
            list_nodes.append(current_parent_id.id)
            return self._check_vat_uniqueness_def(cr, uid, ids, current_vat, list_nodes , context=context)
              
        return True    

    def _check_vat_mandatory(self, cr, uid, ids, context=None):
        '''This method will check the vat mandatoriness in partners
        for those user logged on with a Venezuelan Company
        
        The method will return True when:
            *) The user's company is not from Venezuela
            *) The partner being created is the one for the a company being created [TODO]
        
        The method will return False when:
            *) The user's company is from Venezuela AND the vat field is empty AND:
                +) partner is_company=True AND parent_id is not NULL
                +) partner with parent_id is NULL 
                +) partner with parent_id is NOT NULL AND type of address is invoice   
            '''
        if context is None: context = {}
        # Avoiding Egg-Chicken Syndrome
        # TODO: Refine this approach this is big exception
        # One that can be handle be end user, I hope so!!!
        if context.get('create_company',False):
            return True
        
        user_company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        #Check if the user is not from a VE Company
        if not (user_company.partner_id and user_company.partner_id.country_id and user_company.partner_id.country_id.code == 'VE'):
            return True
        
        partner_brw = self.browse(cr, uid,ids)
        current_vat = partner_brw[0].vat
        current_parent_id = partner_brw[0].parent_id
        current_is_company =partner_brw[0].is_company
        current_type = partner_brw[0].type

        #Partners company type and with parent, not exists
        if (current_is_company and current_parent_id):
            return False
        
        #Partners without parent must have vat 
        if not current_vat and not current_parent_id:
            return False

        #Partners invoice type that not be company and have parent, must have vat 
        if (current_type == 'invoice' and not current_vat and not current_is_company and current_parent_id):
            return False       
        
        return True

    def _validate(self, cr, uid, ids, context=None):
		'''
		This function validates the fields
		'''
			
        #In the original orm.py openerp does not allow using
        #context within the constraint because we have to yield 
        # the same result always,
        # we have overridden this behaviour 
        # TO ALLOW PASSING CONTEXT TO THE RESTRICTION IN RES.PARTNER
        context = context or {}
        lng = context.get('lang')
        trans = self.pool.get('ir.translation')
        error_msgs = []
        for constraint in self._constraints:
            fun, msg, fields = constraint
            # We don't pass around the context here: validation code
            # must always yield the same results.
            if not fun(self, cr, uid, ids, context=context):
                # Check presence of __call__ directly instead of using
                # callable() because it will be deprecated as of Python 3.0
                if hasattr(msg, '__call__'):
                    tmp_msg = msg(self, cr, uid, ids, context=context)
                    if isinstance(tmp_msg, tuple):
                        tmp_msg, params = tmp_msg
                        translated_msg = tmp_msg % params
                    else:
                        translated_msg = tmp_msg
                else:
                    translated_msg = trans._get_source(cr, uid, self._name, 'constraint', lng, msg)
                error_msgs.append(
                        _("Error occurred while validating the field(s) %s: %s") % (','.join(fields), translated_msg)
                )
                self._invalids.update(fields)
        if error_msgs:
            raise except_orm('ValidateError', '\n'.join(error_msgs))
        else:
            self._invalids.clear()

    _constraints = [
        (_check_vat_mandatory, _("Error ! VAT is mandatory"), []),
        (_check_vat_uniqueness, _("Error ! Partner's VAT must be a unique value or empty"), []),
        #~ (_check_partner_invoice_addr, _('Error ! The partner does not have an invoice address.'), []),
    ]
 
    def vat_change_fiscal_requirements(self, cr, uid, ids, value, context=None):
        '''
		This function checks the syntax of the vat
        '''
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
		'''
		This function load the rif and name of the partner
		from the database seniat
		'''
        if context is None:
            context = {}
        su_obj = self.pool.get('seniat.url')
        return su_obj.update_rif(cr, uid, ids, context=context)

    def button_check_vat(self, cr, uid, ids, context=None):
		'''
		This function is called by the button that load
		information of the partner from database 
		SENIAT
		'''
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
