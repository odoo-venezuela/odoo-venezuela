# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 04/04/2012
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
    
    def name_get(self,cr, uid, ids, context):
        if not len(ids):
            return []
        res = []
        so_brw = self.browse(cr, uid, ids, context)
        for item in so_brw:
            res.append((item.id, 'F86 # %s - %s'%(item.name,item.ref)))
        return res

    ##------------------------------------------------------------------------------------ _internal methods
    
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for f86 in self.browse(cr, uid, ids, context=context):
            amount_total = 0.0
            for line in f86.line_ids:
                amount_total += line.amount
            res[f86.id] = amount_total
        return res
        
        
    def _default_line_ids(self, cr, uid, context=None):
        """ Gets default line_ids from form_86_custom_taxes
        """
        obj_ct = self.pool.get('form.86.custom.taxes')    
        ct_ids = obj_ct.search(cr, uid, [('name', '!=', '')])
        res = []
        for id in ct_ids:
            res.append({'tax_code':id,'amount':0.0})
        return res
        
    def _gen_account_move_line(self, company_id, account_id, partner_id, name, debit, credit):
        return (0,0,{
                'auto' : True,
                'company_id': company_id,
                'account_id': account_id,
                'partner_id':partner_id,
                'name': name[:64],
                'debit': debit,
                'credit': credit,
                'reconcile':False,
                })        


    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'name': fields.char('Form #', size=16, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'ref': fields.char('Reference', size=64, required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'date': fields.date('Date', required=True, readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'company_id': fields.many2one('res.company','Company',required=True, readonly=True, ondelete='restrict'),
        'broker_id': fields.many2one('res.partner', 'Broker', change_default=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'ref_reg': fields.char('Reg. number', size=16, required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'date_reg': fields.date('Reg. date', required=False, readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'ref_liq': fields.char('Liq. number', size=16, required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'date_liq': fields.date('liq. date', required=False, readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'custom_id': fields.many2one('form.86.customs', 'Custom', change_default=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'line_ids':fields.one2many('seniat.form.86.lines','line_id','Lines',readonly=True, states={'draft':[('readonly',False)]}),
        'amount_total':fields.function(_amount_total, method=True, type = 'float', string='Amount total', store=False),
        'move_id': fields.many2one('account.move', 'Account move', ondelete='restrict', help="The move of this entry line.", select=True, readonly=True),
        'narration':fields.text('Notes', readonly=False),
        'state': fields.selection([('draft', 'Draft'),('done', 'Done'),('cancel', 'Cancelled')], string='State', required=True, readonly=True),
        }

    _defaults = {
        'name': lambda *a: '', 
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr,uid,'seniat.form.86',context=c),
        'line_ids': _default_line_ids,
        'state': lambda *a: 'draft', 
        }

    _sql_constraints = [        
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods
    
    def create_account_move_lines(self, cr, uid, f86, context=None):
        lines = []
        company_id = context.get('f86_company_id')
        f86_cfg = context.get('f86_config')

        #~ expenses
        for line in f86.line_ids:
            debit_account_id = line.tax_code.account_id.id
            credit_account_id = line.tax_code.partner_id.property_account_payable.id
            if not debit_account_id or not debit_account_id:
                raise osv.except_osv(_('Error!'),_('No account found, please check customs taxes settings (%s)')%line.tax_code.name)
            lines.append(self._gen_account_move_line(company_id, debit_account_id, line.tax_code.partner_id.id, '[%s] %s - %s'%(line.tax_code.code,line.tax_code.ref,line.tax_code.name) , line.amount,0.0))
            lines.append(self._gen_account_move_line(company_id, credit_account_id, line.tax_code.partner_id.id, 'F86 #%s'%f86.name ,0.0,line.amount))
        
        lines.reverse() ## set real order ;-)
        return lines
                
        
    def create_account_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj_move = self.pool.get('account.move')
        obj_cfg = self.pool.get('form.86.config')
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        company = self.pool.get('res.company').browse(cr,uid,company_id,context=context)
        cfg_id = obj_cfg.search(cr, uid, [('company_id', '=', company_id)])
        if cfg_id:
            f86_cfg = obj_cfg.browse(cr,uid,cfg_id[0],context=context)
        else:
            raise osv.except_osv(_('Error!'),_('Please set a valid configuration'))
        date = time.strftime('%Y-%m-%d')
        context.update({'f86_company_id':company_id,'f86_config':f86_cfg})
        so_brw = self.browse(cr,uid,ids,context={})
        move_ids = []
        for f86 in so_brw:
            move = {
                    'ref':'F86 #%s'%f86.name,
                    'journal_id':f86_cfg.journal_id.id,
                    'date':f86.date_liq,
                    'company_id':company_id,
                    'state':'draft',
                    'to_check':False,
                    'narration':_('SENIAT - Forma 86  # %s):\n\tReference: %s\n\tBroker: %s')%(f86.name,f86.ref,f86.broker_id.name),
                    }
            lines = self.create_account_move_lines(cr, uid, f86, context)
            if lines:
                move.update({'line_id':lines})
                move_id = obj_move.create(cr, uid, move, context)
                obj_move.post(cr, uid, [move_id], context=context)
                if move_id:
                    move_ids.append(move_id)
                    self.write(cr, uid, f86.id, {'move_id':move_id},context)
        return move_ids        
        return True

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow
    
    def button_draft(self, cr, uid, ids, context=None):
        vals={'state':'draft'}
        return self.write(cr,uid,ids,vals,context)


    def button_done(self, cr, uid, ids, context=None):
        self.create_account_move(cr, uid, ids, context)
        vals={'state':'done'}
        return self.write(cr,uid,ids,vals,context)


    def button_cancel(self, cr, uid, ids, context=None):
        f86 = self.browse(cr,uid,ids[0],context=context)
        f86_move_id = f86.move_id.id if f86 and f86.move_id else False
        vals={'state':'cancel','move_id':0}
        res = self.write(cr,uid,ids,vals,context)
        if f86_move_id:
            self.pool.get('account.move').unlink(cr,uid,[f86_move_id],context)
        return self.write(cr,uid,ids,vals,context)


    def test_draft(self, cr, uid, ids, *args):
        return True


    def test_done(self, cr, uid, ids, *args):
        so_brw = self.browse(cr,uid,ids,context={})
        for f86 in so_brw:
            if f86.amount_total <= 0:
                raise osv.except_osv(_('Warning!'),_('You must indicate a amount'))
            if not f86.date_liq:
                raise osv.except_osv(_('Warning!'),_('You must indicate a liquidation date '))
        return True


    def test_cancel(self, cr, uid, ids, *args):
        if len(ids) != 1:
            raise osv.except_osv(_('Error!'),_('Multiple operations not allowed'))
        for f86 in self.browse(cr,uid,ids,context=None):
            if f86.move_id and f86.move_id.state != 'draft':
                raise osv.except_osv(_('Error!'),_('Can\'t cancel a import while account move state <> "Draft"'))
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
        'tax_code': fields.many2one('form.86.custom.taxes', 'Tax', ondelete='restrict',required=True, readonly=True), 
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'),required=True),
        }

    _defaults = {
        }

    _sql_constraints = [        
        ('code_uniq', 'UNIQUE(line_id,tax_code)', 'The code must be unique! (for this form)'),
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

seniat_form_86_lines()
