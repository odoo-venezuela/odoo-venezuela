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
            res.append((item.id, 'F86 # %s - %s'%(item.name,item.ref or '')))
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
        """ 
        Gets default line_ids from form_86_custom_taxes
        """
        obj_ct = self.pool.get('form.86.custom.taxes')    
        ct_ids = obj_ct.search(cr, uid, [], context=context)
        res = []
        for id in ct_ids:
            vat = obj_ct.browse(cr,uid,id,context=context)
            res.append({'tax_code':id,'amount':0.0,'vat_detail':vat.vat_detail})
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
        'date_liq': fields.date('liq. date', required=True, readonly=True, states={'draft':[('readonly',False)]}, select=True),
        'custom_id': fields.many2one('form.86.customs', 'Custom', change_default=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'line_ids':fields.one2many('seniat.form.86.lines','line_id','Tax lines',readonly=True, states={'draft':[('readonly',False)]}),
        'amount_total':fields.function(_amount_total, method=True, type = 'float', string='Amount total', store=False),
        'move_id': fields.many2one('account.move', 'Account move', ondelete='restrict', select=True, readonly=True, help="The move of this entry line."),
        'narration':fields.text('Notes', readonly=False),
        'invoice_ids':fields.one2many('account.invoice','num_import_form_id','Related invoices',readonly=True), 
        'state': fields.selection([('draft', 'Draft'),('open', 'Open'),('done', 'Done'),('cancel', 'Cancelled')], string='State', required=True, readonly=True),
        }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr,uid,'seniat.form.86',context=c),
        'line_ids': _default_line_ids,
        'state': lambda *a: 'draft', 
        }

    _sql_constraints = [  
        ('name_uniq', 'UNIQUE(name)', 'The form # must be unique!'),      
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods
    
    def create_account_move_lines(self, cr, uid, f86, context=None):
        """
        Creates the account.move.lines from line_ids detail except for taxes with "vat_detail", 
        in this case create debits from line_ids.line_vat_ids and get debit account from account_tax model
        """
        lines = []
        company_id = context.get('f86_company_id')
        f86_cfg = context.get('f86_config')

        #~ expenses
        for line in f86.line_ids:

            debits = []
            if line.tax_code.vat_detail:
                for vat in line.line_vat_ids:
                    debits.append({'account_id':vat.acc_tax_id.account_collected_id.id,'amount':vat.tax_amount,'tax_info':' (%s)'%vat.acc_tax_id.name})
            else:
                debits.append({'account_id':line.tax_code.account_id.id,'amount':line.amount,'tax_info':''})
                
            credit_account_id = line.tax_code.partner_id.property_account_payable.id

            for debit in debits:
                if not debit['account_id'] or not credit_account_id:
                    raise osv.except_osv(_('Error!'),_('No account found, please check customs taxes settings (%s)')%line.tax_code.name)
                lines.append(self._gen_account_move_line(company_id, debit['account_id'], line.tax_code.partner_id.id, '[%s] %s - %s%s'%(line.tax_code.code,line.tax_code.ref,line.tax_code.name,debit['tax_info']) , debit['amount'],0.0))
            lines.append(self._gen_account_move_line(company_id, credit_account_id, line.tax_code.partner_id.id, 'F86 #%s - %s'%(f86.name,line.tax_code.name) ,0.0,line.amount))
        
        lines.reverse() ## set real order ;-)
        return lines
                
        
    def create_account_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        so_brw = self.browse(cr,uid,ids,context={})
        for f86 in so_brw:
            if f86.move_id: #~ The move is already done, nothing to do
                return []
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
        move_ids = []
        for f86 in so_brw:
            move = {
                    'ref':'F86 #%s'%f86.name,
                    'journal_id':f86_cfg.journal_id.id,
                    'date':f86.date_liq,
                    'company_id':company_id,
                    'state':'draft',
                    'to_check':False,
                    'narration':_('Form 86 # %s\n\tReference: %s\n\tBroker: %s\n\nRelated invoices:')%(f86.name,f86.ref or '',f86.broker_id.name or ''),
                    }
            for inv in f86.invoice_ids:
                str_inv = _('\n\tSupplier: %-40s Reference: %s')%(inv.partner_id.name,inv.reference)
                move['narration'] = '%s%s'%(move['narration'],str_inv)            
            lines = self.create_account_move_lines(cr, uid, f86, context)
            if lines:
                move.update({'line_id':lines})
                move_id = obj_move.create(cr, uid, move, context)
                obj_move.post(cr, uid, [move_id], context=context)
                if move_id:
                    move_ids.append(move_id)
                    self.write(cr, uid, f86.id, {'move_id':move_id},context)
        return move_ids        

    ##------------------------------------------------------------------------------------ buttons (object)
    
    ##------------------------------------------------------------------------------------ on_change...

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow
    
    def button_draft(self, cr, uid, ids, context=None):
        vals={'state':'draft'}
        return self.write(cr,uid,ids,vals,context)


    def button_open(self, cr, uid, ids, context=None):
        self.create_account_move(cr, uid, ids, context)
        vals={'state':'open'}
        return self.write(cr,uid,ids,vals,context)


    def button_done(self, cr, uid, ids, context=None):
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


    def test_open(self, cr, uid, ids, *args):
        so_brw = self.browse(cr,uid,ids,context={})
        for f86 in so_brw:
            if f86.amount_total <= 0:
                raise osv.except_osv(_('Warning!'),_('You must indicate a amount'))
            for line in f86.line_ids:    
                if line.vat_detail:
                    vat_total = line.amount
                    for vat in line.line_vat_ids:
                        vat_total -= vat.tax_amount
                    if abs(vat_total) > 0.001:
                        raise osv.except_osv(_('Warning!'),_('The vat detail data dosen\'t corespond with vat amount in line: %s')%line.tax_code.name) 
        return True


    def test_done(self, cr, uid, ids, *args):
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
    
    _rec_name = 'tax_code'

    _columns = {
        'line_id':fields.many2one('seniat.form.86', 'Line', required=True, ondelete='cascade'),
        'tax_code': fields.many2one('form.86.custom.taxes', 'Tax', ondelete='restrict',required=True, readonly=False), 
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'),required=True),
        'line_vat_ids':fields.one2many('seniat.form_86.lines.vat','line_vat_id','Vat lines',attrs="{'readonly':[('vat_detail','=',True)],'required':[('vat_detail','=',True)]}"), ## 
        'vat_detail':fields.related('tax_code','vat_detail', type='boolean', string='Tax detail',store=False, readonly=True)
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


##---------------------------------------------------------------------------------------- seniat_form_86_lines_vat

class seniat_form_86_lines_vat(osv.osv):

    _name = 'seniat.form_86.lines.vat'

    _description = ''

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ _internal methods

    ##------------------------------------------------------------------------------------ function fields
    
    _rec_name = 'reference'

    _columns = {
        'line_vat_id':fields.many2one('seniat.form.86.lines', 'Vat line', required=True, ondelete='cascade'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='restrict', select=True, required=True),
        'partner_id':fields.related('invoice_id','partner_id', type='many2one', relation='res.partner', string='Supplier',store=False, readonly=True),  
        'reference':fields.related('invoice_id','reference', type='char', string='Invoice ref',size=64,store=False, readonly=True), 
        'acc_tax_id':fields.many2one('account.tax', 'Account Tax ', required=True, ondelete='restrict', domain=[('type_tax_use','=','purchase')], help=""), 
        'base_amount': fields.float('Base amount', digits_compute=dp.get_precision('Account'),required=True),
        'tax_amount': fields.float('Tax amount', digits_compute=dp.get_precision('Account'),required=True),
        }

    _defaults = {
        }

    _sql_constraints = [        
        ('base_amount_gt_zero', 'CHECK (base_amount>0)', 'The base amount must be > 0!'),
        ('tax_amount_zero', 'CHECK (tax_amount>=0)', 'The tax amount must be >= 0!'),
        ]

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...
    
    """
    def on_change_line_vat_id(self, cr, uid, ids, line_vat_id):
        '''
        Create a domain to filter invoice_id for invoices listed in seniat_form_86.invoice_ids only
        http://help.openerp.com/question/11180/how-to-create-a-domain-for-field-in-parentparent-model/
        '''
        res = {}
        if line_vat_id:
            line_obj = self.pool.get('seniat.form.86.lines')
            invoices = [i.id for i in line_obj.browse(cr, uid, line_vat_id).line_id.invoice_ids]
            res = {'domain': {'invoice_id': [('id','in',invoices)]}}
        return res
    """
    
    def on_change_amount(self, cr, uid, ids, acc_tax_id, base_amount, tax_amount):
        """
        To autocompute base or tax, only for percent based taxes
        """
        res = {}
        if acc_tax_id:
            obj_vat = self.pool.get('account.tax')
            vat = obj_vat.browse(cr,uid,acc_tax_id)
            if vat.type == 'percent':
                if base_amount == 0 and tax_amount > 0: 
                    base_amount = round(tax_amount / vat.amount,2)
                res = {'value':{'base_amount':base_amount}}
        return res
        
        
    def on_change_invoice_id(self, cr, uid, ids, invoice_id):
        res = {}
        if invoice_id:
            obj_inv = self.pool.get('account.invoice')
            inv = obj_inv.browse(cr,uid,invoice_id)
            res = {'value':{'partner_id':inv.partner_id.id,'reference':inv.reference}}
        return res

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

seniat_form_86_lines_vat()
