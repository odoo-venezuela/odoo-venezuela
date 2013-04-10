# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 10/04/2012
#    Version: 0.0.0.0
#
#    Description:
#
#
##############################################################################
#~ from datetime import datetime
from osv import fields,osv
from tools.translate import _
import pooler
#~ import decimal_precision as dp
#~ import time
#~ import netsvc


##---------------------------------------------------------------------------------------- seniat_form_86_config

class form_86_config(osv.osv):
    '''
    Stores common config parameters for form_86 data
    '''
    
    _name = 'form.86.config'

    _description = ''

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ _internal methods

    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'company_id':fields.many2one('res.company','Company', required=True, readonly=True, ondelete='restrict'),
        #~ 'account_id':fields.many2one('account.account', 'Account to pay', required=True, ondelete='restrict'),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, ondelete='restrict'),  
        }
        
    _rec_name = "company_id"
        

    _defaults = {
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr,uid,'form.86.config',context=c),
        }

    _sql_constraints = [
        ('company_id_uniq', 'UNIQUE(company_id)', 'The company must be unique!'),
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

form_86_config()



##---------------------------------------------------------------------------------------- form_86_customs

class form_86_customs(osv.osv):
    '''
    Stores a list with Venezuela's customs
    '''

    _name = 'form.86.customs'

    _description = ''

    ##------------------------------------------------------------------------------------
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        so_brw = self.browse(cr,uid,ids,context={})
        res = []
        for item in so_brw:
            res.append((item.id, '[%s] %s'%(item.code, item.name)))
        return res
        
        
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        #~ Based on account.account.name_search...
        res =  super(form_86_customs, self).name_search(cr, user, name, args, operator, context, limit)    
        if not res and name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if ids:
                res = self.name_get(cr, user, ids, context=context)
        return res

    ##------------------------------------------------------------------------------------ _internal methods

    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'code': fields.char('Code', size=16, required=True, readonly=False),   
        'name': fields.char('Name', size=64, required=True, readonly=False),
        }

    _defaults = {
        }

    _sql_constraints = [     
        ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

form_86_customs()



##---------------------------------------------------------------------------------------- form_86_custom_taxes

class form_86_custom_taxes(osv.osv):
    '''
    A list of the concepts for taxes in form_86
    '''

    _name = 'form.86.custom.taxes'

    _description = ''
    
    _order = 'sequence'


    ##------------------------------------------------------------------------------------
   
    def name_get(self,cr, uid, ids, context):
        if not len(ids):
            return []
        res = []
        so_brw = self.browse(cr, uid, ids, context)
        for item in so_brw:
            res.append((item.id, '[%s] %s - %s'%(item.code,item.ref,item.name)))
        return res
        
    ##------------------------------------------------------------------------------------ _internal methods

    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'code': fields.char('Code', size=16, required=True, readonly=False),   
        'name': fields.char('Name', size=64, required=True, readonly=False),
        'ref': fields.char('Ref', size=16, required=False, readonly=False),   
        'sequence': fields.integer('Sequence'), 
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'account_id':fields.many2one('account.account', 'Account to pay', required=True, ondelete='restrict',help="This account will be used for expenses related to taxes"), 
        'acc_tax_id':fields.many2one('account.tax', 'Account Tax ', required=False, ondelete='restrict',domain=[('type_tax_use','=','purchase')],help=""), 
        'company_id': fields.many2one('res.company','Company',required=True, readonly=True, ondelete='restrict'),
        }

    _defaults = {
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr,uid,'form.86.config',context=c),
        }

    _sql_constraints = [     
        ('code_uniq', 'UNIQUE(code,company_id)', 'The code must be unique! (for this comany)'),
        ('sequence_uniq', 'UNIQUE(sequence,company_id)', 'The sequence must be unique! (for this comany)'),
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

form_86_custom_taxes()

