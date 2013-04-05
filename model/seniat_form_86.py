# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 03/10/2012
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
import decimal_precision as dp
import time
#~ import netsvc


##---------------------------------------------------------------------------------------- seniat_form_86

class seniat_form_86(osv.osv):

    _name = 'seniat.form.86'

    _description = ''

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ _internal methods
    
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for adv in self.browse(cr, uid, ids, context=context):
            values =   {'amount_total': 0,
                       }
            res[adv.id] = values[field_name]
        return res


    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'name': fields.char('Name', size=16, required=False, readonly=False),
        'ref': fields.char('Reference', size=64, required=False, readonly=False),
        'company_id': fields.many2one('res.company','Company',required=True, readonly=True, ondelete='restrict'),
        'broker_id': fields.many2one('res.partner', 'Broker', change_default=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'ref_reg': fields.char('Reg. reference', size=16, required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'date_reg': fields.date('Reg. date', required=False, readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'ref_liq': fields.char('Liq. reference', size=16, required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'date_liq': fields.date('liq. date', required=False, readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'custom_id': fields.many2one('form.86.customs', 'Custom', change_default=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'line_ids':fields.one2many('seniat.form.86.lines','line_id','Lines',readonly=True, states={'draft':[('readonly',False)]}),
        'amount_total':fields.function(_amount_total, method=True, type = 'float', string='Amount total', store=False),
        'move_id': fields.many2one('account.move', 'Account move', ondelete='restrict', help="The move of this entry line.", select=True, readonly=True),
        'narration':fields.text('Notes', readonly=False),
        'state': fields.selection([('draft', 'Draft'),('done', 'Done'),('cancel', 'Cancelled')], string='State', required=True, readonly=True),
        }

    _defaults = {
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr,uid,'seniat.form.86',context=c),
        'state': lambda *a: 'draft', 
        }

    _sql_constraints = [        
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow
    
    def button_draft(self, cr, uid, ids, context=None):
        vals={'state':'draft'}
        return self.write(cr,uid,ids,vals,context)


    def button_done(self, cr, uid, ids, context=None):
        vals={'state':'done'}
        return self.write(cr,uid,ids,vals,context)


    def button_cancel(self, cr, uid, ids, context=None):
        vals={'state':'cancel'}
        return self.write(cr,uid,ids,vals,context)


    def test_draft(self, cr, uid, ids, *args):
        return True


    def test_done(self, cr, uid, ids, *args):
        return True


    def test_cancel(self, cr, uid, ids, *args):
        return True


seniat_form_86()



##---------------------------------------------------------------------------------------- seniat_form_86

class seniat_form_86_lines(osv.osv):

    _name = 'seniat.form.86.lines'

    _description = ''

    ##------------------------------------------------------------------------------------
    
    ##------------------------------------------------------------------------------------ _internal methods
    
    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'line_id':fields.many2one('seniat.form.86', 'Line', required=True, ondelete='cascade'),
        'code': fields.many2one('form.86.custom.taxes', 'Tax', ondelete='restrict',required=True,), 
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'),required=True),
        }

    _defaults = {

        }

    _sql_constraints = [        
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

seniat_form_86_lines()
