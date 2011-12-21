#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
################################################################################

from osv import osv, fields
import time
from tools.translate import _
import decimal_precision as dp

class account_wh_iva_line_tax(osv.osv):
    _name = 'account.wh.iva.line.tax'
account_wh_iva_line_tax()

class account_wh_iva_line(osv.osv):
    _name = "account.wh.iva.line"
account_wh_iva_line()

class account_wh_iva(osv.osv):
    _name = "account.wh.iva"
account_wh_iva()

class account_wh_iva_line_tax(osv.osv):
    
    def _set_amount_ret(self, cr, uid, id, name, value, arg, ctx=None):
        if ctx is None: 
            ctx = {}
        if not self.browse(cr,uid,id,context=ctx).wh_vat_line_id.retention_id.type=='out_invoice':
            return False
        sql_str = """UPDATE account_wh_iva_line_tax set
                    amount_ret='%s'
                    WHERE id=%d """ % (value, id)
        cr.execute(sql_str)
        return True
        
    def _get_amount_ret(self, cr, uid, ids, fieldname, args, context=None):
        if context is None: context=None
        res = {}
        
        awilt_brw = self.browse(cr, uid, ids, context=context)
        
        for each in awilt_brw:
            #~ TODO: THIS NEEDS REFACTORY IN ORDER TO COMPLY WITH THE SALE WITHHOLDING
            res[each.id] = each.amount * each.wh_vat_line_id.wh_iva_rate /100.0
        return res
    
    _name = 'account.wh.iva.line.tax'
    _columns = {
        'inv_tax_id': fields.many2one('account.invoice.tax', 'Invoice Tax', required=True, ondelete='set null', help="Tax Line"),
        'wh_vat_line_id':fields.many2one('account.wh.iva.line', 'Withholding VAT Line', required=True, ondelete='cascade',),
        'tax_id': fields.related('inv_tax_id', 'tax_id', type='many2one',relation='account.tax', string='Tax', store=True, select=True, readonly=True, ondelete='set null'),
        'name': fields.related('inv_tax_id', 'name', type='char', string='Tax Name', size=256, store=True, select=True, readonly=True, ondelete='set null'),
        'base': fields.related('inv_tax_id', 'base', type='float', string='Tax Base', store=True, select=True, readonly=True, ondelete='set null'),
        'amount': fields.related('inv_tax_id', 'amount', type='float', string='Taxed Amount', store=True, select=True, readonly=True, ondelete='set null'),
        # Otro campo related
        'company_id': fields.related('inv_tax_id', 'company_id', type='many2one',relation='res.company', string='Company', store=True, select=True, readonly=True, ondelete='set null'),
        'amount_ret': fields.function(
            _get_amount_ret,
            method=True,
            type='float',
            string='Withheld Taxed Amount',
            digits_compute= dp.get_precision('Withhold'), 
            store= {
                'account.wh.iva.line.tax': (lambda self, cr, uid, ids, c={}: ids, ['amount'],15)
            },
            fnct_inv=_set_amount_ret,
            help="Withholding vat amount"),
        #~ 'amount_ret': fields.float('Withheld Taxed Amount', digits_compute= dp.get_precision('Withhold'), help="Withholding vat amount"),
    }

account_wh_iva_line_tax()

class account_wh_iva_line(osv.osv):
    
    ####################################################################
    #~ ESTO SE DEBE BORRAR UNA VEZ QUE SE TERMINE
    #~ DE DEFINIR LA EXISTENCIA DE LAS LINEAS NUEVAS PARA RETENCION
    ####################################################################
    
    def _compute_tax_lines(self, cr, uid, ids, name, args, context=None):
        if context is None: context = {}
        res = {}
        awilt_obj = self.pool.get('account.wh.iva.line.tax')
        for ret_line in self.browse(cr, uid, ids, context):
            lines = []
            if ret_line.invoice_id:
                tax_ids = [i.id for i in ret_line.invoice_id.tax_line if i.tax_id and i.tax_id.ret]
                print 'tax_ids ',tax_ids
                for i in tax_ids:
                    lines.append(awilt_obj.create(cr, uid, {
                            'inv_tax_id':i,
                            'wh_vat_line_id':ret_line.id
                                                }, context=context))
                #~ ids_tline = ret_line.invoice_id.tax_line
                #~ lines = map(lambda x: x.id, ids_tline)
                print 'lines ', lines
            res[ret_line.id] = lines
        return res

    def _get_tax_lines(self, cr, uid, tax_id_brw, context=None):
        if context is None: context = {}
        return {
            'inv_tax_id':tax_id_brw.id,
            'tax_id':tax_id_brw.tax_id.id,
            'name':tax_id_brw.tax_id.name,
            'base':tax_id_brw.base,
            'amount':tax_id_brw.amount,
            'company_id':tax_id_brw.company_id.id,
            'wh_iva_rate':tax_id_brw.invoice_id.partner_id.wh_iva_rate
        }
    
    def load_taxes(self, cr, uid, ids, context=None):
        if context is None: context = {}
        awilt_obj = self.pool.get('account.wh.iva.line.tax')
        for ret_line in self.browse(cr, uid, ids, context):
            lines = []
            if ret_line.invoice_id:
                rate = \
                    ret_line.retention_id.type == 'out_invoice' and ret_line.invoice_id.company_id.partner_id.wh_iva_rate or \
                    ret_line.retention_id.type == 'in_invoice' and ret_line.invoice_id.partner_id.wh_iva_rate
                self.write(cr, uid, ret_line.id, {'wh_iva_rate':  rate})
                tax_lines = awilt_obj.search(cr, uid, [('wh_vat_line_id', '=', ret_line.id)])
                if tax_lines:
                    awilt_obj.unlink(cr, uid, tax_lines)
                
                tax_ids = [i for i in ret_line.invoice_id.tax_line if i.tax_id and i.tax_id.ret]
                for i in tax_ids:
                    values = self._get_tax_lines(cr, uid, i, context=context)
                    values.update({'wh_vat_line_id':ret_line.id,})
                    lines.append(awilt_obj.create(cr, uid, values, context=context))
        return True

    ####################################################################
    #~ FIN DEL BORRADO
    ####################################################################
    
    def _amount_all(self, cr, uid, ids, fieldname, args, context=None):
        res = {}
        print '_amount_all'
        for ret_line in self.browse(cr, uid, ids, context):
            res[ret_line.id] = {
                'amount_tax_ret': 0.0,
                'base_ret': 0.0
            }
            for line in ret_line.tax_line:
                res[ret_line.id]['amount_tax_ret'] += line.amount_ret
                res[ret_line.id]['base_ret'] += line.base

        return res

    _name = "account.wh.iva.line"
    _description = "Withholding vat line"
    _columns = {
        'name': fields.char('Description', size=64, required=True, help="Withholding line Description"),
        'retention_id': fields.many2one('account.wh.iva', 'Withholding vat', ondelete='cascade', help="Withholding vat"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, ondelete='set null', help="Withholding invoice"),
        #########################################
        #~ REDEFINIENDO EL CAMPO TAX LINE,
        #~ AHORA SERA UN NUEVO MODELO EL QUE LLEVARA A CABO TAL TAREA
        'tax_line': fields.one2many('account.wh.iva.line.tax','wh_vat_line_id', string='Taxes', help="Invoice taxes"),
        #~ 'tax_line': fields.function(_compute_tax_lines, method=True, relation='account.wh.iva.line.tax', type="one2many", string='Taxes', help="Invoice taxes",store = {'account.wh.iva.line': (lambda  self, cr, uid, ids, c={}: ids,['invoice_id'],15)}),
        #~ 'tax_line': fields.function(_compute_tax_lines, method=True, relation='account.invoice.tax', type="one2many", string='Taxes', help="Invoice taxes"),
        #########################################
        'amount_tax_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Wh. tax amount', multi='all', help="Withholding tax amount"),
        'base_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Wh. amount', multi='all', help="Withholding without tax amount"),
#        'retention_rate': fields.function(_retention_rate, method=True, string='Wh. rate', type='float', help="Withholding rate"),
        'move_id': fields.many2one('account.move', 'Account Entry', readonly=True, help="Account entry"),
        #~ 'amount_base_wh': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount without tax"),        
        #~ 'amount_tax_wh': fields.float('Amount wh. tax vat', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withholding tax vat"),        
        'wh_iva_rate': fields.float(string='Withholding Vat Rate', digits_compute= dp.get_precision('Withhold'), help="Withholding vat rate"),
    }

    _sql_constraints = [
      ('ret_fact_uniq', 'unique (invoice_id)', 'The invoice has already assigned in withholding vat, you cannot assigned it twice!')
    ] 

    def invoice_id_change(self, cr, uid, ids, invoice, context=None):
        if context is None:
            context = {}
        if not invoice:
            return {}
        result = {}
        lst=[]
        domain = {}
        ok = True
        res = self.pool.get('account.invoice').browse(cr, uid, invoice, context=context)
        cr.execute('select retention_id from account_wh_iva_line where invoice_id=%s', (invoice,))
        ret_ids = cr.fetchone()
        ok = ok and bool(ret_ids)
        if ok:
            ret = self.pool.get('account.wh.iva').browse(cr, uid, ret_ids[0], context)
            raise osv.except_osv('Assigned Invoice !',"The invoice has already assigned in withholding vat code: '%s' !" % (ret.code,))

        result['name'] = res.name


        return {'value':result, 'domain':domain}

account_wh_iva_line()

class account_wh_iva(osv.osv):

    def _amount_ret_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for retention in self.browse(cr, uid, ids, context):
            res[retention.id] = {
                'amount_base_ret': 0.0,
                'total_tax_ret': 0.0
            }
            #cambiar por los campos no calculados
            for line in retention.wh_lines:
                res[retention.id]['total_tax_ret'] += line.amount_tax_ret
                res[retention.id]['amount_base_ret'] += line.base_ret

        return res
        
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type', 'in_invoice')
        type2journal = {'out_invoice': 'iva_sale', 'in_invoice': 'iva_purchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'iva_purchase'))], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_currency(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]
    
    _name = "account.wh.iva"
    _description = "Withholding Vat"
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly',False)]}, required=True, help="Description of withholding"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Withholding reference"),
        'number': fields.char('Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Withholding number"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ],'Type', readonly=True, help="Withholding type"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'State', readonly=True, help="Withholding State"),
        'date_ret': fields.date('Accounting date', readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the current date"),
        'date': fields.date('Voucher Date', readonly=True, states={'draft':[('readonly',False)]}, help="Date"),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True, states={'draft':[('readonly',False)]}, help="Keep empty to use the period of the validation(Withholding date) date."),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The pay account used for this withholding."),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Withholding customer/supplier"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal entry"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'wh_lines': fields.one2many('account.wh.iva.line', 'retention_id', 'Withholding vat lines', readonly=True, states={'draft':[('readonly',False)]}, help="Withholding vat lines"),
        #~ 'tot_amount_base_wh': fields.float('Amount', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount without tax"),
        #~ 'tot_amount_tax_wh': fields.float('Amount wh. tax vat', required=False, digits_compute= dp.get_precision('Withhold'), help="Amount withholding tax vat"),
        'amount_base_ret': fields.function(_amount_ret_all, method=True, digits_compute= dp.get_precision('Withhold'), string='Compute amount', multi='all', help="Compute amount without tax"),
        'total_tax_ret': fields.function(_amount_ret_all, method=True, digits_compute= dp.get_precision('Withhold'), string='Compute amount wh. tax vat', multi='all', help="compute amount withholding tax vat"),
        
    } 
    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('account.wh.iva').wh_iva_seq_get(cr, uid, context),
        'type': _get_type,
        'state': lambda *a: 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,

    }

    def _get_valid_wh(self, cr, uid, amount_ret, amount, wh_iva_rate, offset=0.5,  context=None):
        '''This method can be override in a way that
        you can afford your own value for the offset'''
        if context is None: context = {}
        return amount_ret >= amount * (wh_iva_rate - offset)/100.0 and amount_ret <= amount * (wh_iva_rate + offset)/100.0
    
    def check_wh_taxes(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res = {}
        note = _('Taxes in the following invoices have been miscalculated\n\n')
        for wh_line in self.browse(cr,uid, ids[0]).wh_lines:
            for tax in wh_line.tax_line:
                #~ if not self._get_valid_wh(cr, uid, tax.amount_ret, tax.amount, tax.wh_vat_line_id.wh_iva_rate, context=context):
                if not self._get_valid_wh(cr, uid, tax.amount_ret, tax.amount, tax.wh_vat_line_id.wh_iva_rate, context=context):
                    if not res.get(wh_line.id, False):
                        note += _('\tInvoice: %s, %s, %s\n')%(wh_line.invoice_id.name,wh_line.invoice_id.number,wh_line.invoice_id.reference or '/')
                        res[wh_line.id] = True
                    note += '\t\t%s\n'%tax.name
        if res:
            raise osv.except_osv(_('Miscalculated Withheld Taxes'),note)
        return True

    def check_vat_wh(self, cr, uid, ids, context={}):
        print 'check_vat_wh'
        obj = self.browse(cr, uid, ids[0])
        res = {}
        for wh_line in obj.wh_lines:
            if not wh_line.tax_line:
                res[wh_line.id] = (wh_line.invoice_id.name,wh_line.invoice_id.number,wh_line.invoice_id.reference)
        if res:
            note = _('The Following Invoices Have not already been withheld:\n\n')
            for i in res:
                note += '* %s, %s, %s\n'%res[i]
            note += _('\nPlease, Load the Taxes to be withheld and Try Again')
            
            raise osv.except_osv(_('Invoices with Missing Withheld Taxes!'),note)
        return True
        
    def _check_partner(self, cr, uid, ids, context={}):
        agt = False
        obj = self.browse(cr, uid, ids[0])
        if obj.type in ('out_invoice', 'out_refund') and obj.partner_id.wh_iva_agent:
            agt = True
        if obj.type in ('in_invoice', 'in_refund') and obj.company_id.partner_id.wh_iva_agent:
            agt = True
        return agt

    _constraints = [
        (_check_partner, 'Error ! The partner must be withholding vat agent .', ['partner_id']),
    ]

    _sql_constraints = [
      ('ret_num_uniq', 'unique (number)', 'number must be unique !')
    ] 


    def wh_iva_seq_get(self, cr, uid, context=None):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='account.wh.iva' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        if obj_ret.type == 'in_invoice':
            cr.execute('SELECT id, number ' \
                    'FROM account_wh_iva ' \
                    'WHERE id IN ('+','.join(map(str,ids))+')')

            for (id, number) in cr.fetchall():
                if not number:
                    number = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.iva.%s' % obj_ret.type)
                cr.execute('UPDATE account_wh_iva SET number=%s ' \
                        'WHERE id=%s', (number, id))
        return True
    
    def action_date_ret(self,cr,uid,ids,context=None):
        for wh in self.browse(cr, uid, ids, context):
            wh.date_ret or self.write(cr, uid, [wh.id], {'date_ret':time.strftime('%Y-%m-%d')})
        return True


    def action_move_create(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        if context is None: context = {}

        ret = self.browse(cr, uid, ids[0], context)
        for line in ret.wh_lines:
            if line.move_id or line.invoice_id.wh_iva:
                raise osv.except_osv(_('Invoice already withhold !'),\
                _("You must omit the follow invoice '%s' !") %\
                (line.invoice_id.name,))

        acc_id = ret.account_id.id

        period_id = ret.period_id and ret.period_id.id or False
        journal_id = ret.journal_id.id
        if not period_id:
            per_obj = self.pool.get('account.period')
            period_id = per_obj.find(cr, uid,ret.date_ret or time.strftime('%Y-%m-%d'))
            period_id = per_obj.search(cr,uid,[('id','in',period_id),('special','=',False)])
            print 'period_id ',period_id
            if not period_id:
                raise osv.except_osv(_('Missing Periods!'),\
                _("There are not Periods created for the pointed day: %s!") %\
                (ret.date_ret or time.strftime('%Y-%m-%d')))
            period_id = period_id[0]
        print 'ANTES DE LAS wh_lines'
        if ret.wh_lines:
            print 'wh_lines 192'
            for line in ret.wh_lines:
                print 'wh_lines 194'
                writeoff_account_id,writeoff_journal_id = False, False
                amount = line.amount_tax_ret
                if line.invoice_id.type in ['in_invoice','in_refund']:
                    name = 'COMP. RET. IVA ' + ret.number + ' Doc. '+ (line.invoice_id.reference or '')
                else:
                    name = 'COMP. RET. IVA ' + ret.number + ' Doc. '+ (str(int(line.invoice_id.number)) or '')
                
                context.update({'vat_wh':True})
                ret_move = inv_obj.ret_and_reconcile(cr, uid, [line.invoice_id.id],
                        amount, acc_id, period_id, journal_id, writeoff_account_id,
                        period_id, writeoff_journal_id, ret.date_ret, name,line.tax_line, context)
                # make the withholding line point to that move
                rl = {
                    'move_id': ret_move['move_id'],
                }
                lines = [(1, line.id, rl)]
                self.write(cr, uid, [ret.id], {'wh_lines':lines, 'period_id':period_id})
    
        return True


    def onchange_partner_id(self, cr, uid, ids, type, partner_id,context=None):
        if context is None: context = {}
            
        acc_id = False
        res = {}
        inv_obj = self.pool.get('account.invoice')
        
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable and p.property_account_receivable.id or False
            else:
                acc_id = p.property_account_payable and p.property_account_payable.id or False
        #~ BEGIN DELETE
        #~ self._update_check(cr, uid, ids, partner_id)
        #~ END DELETE
        
        wh_line_obj = self.pool.get('account.wh.iva.line')
        wh_lines = ids and wh_line_obj.search(cr, uid, [('retention_id', '=', ids[0])]) or False
        print 'wh_lines ', wh_lines
        res_wh_lines = []
        if wh_lines:
            print 'UNLINKING'
            wh_line_obj.unlink(cr, uid, wh_lines)
        
        inv_ids = inv_obj.search(cr,uid,[('state', '=', 'open'), ('wh_iva', '=', False), ('partner_id','=',partner_id)],context=context)
        
        print 'inv_ids ', inv_ids
        if inv_ids:
            #~ Get only the invoices which are not in a document yet
            inv_ids = [i for i in inv_ids if not wh_line_obj.search(cr, uid, [('invoice_id', '=', i)])]
            
        if inv_ids:
            awil_obj = self.pool.get('account.wh.iva.line')
            res_wh_lines = [{
                        'invoice_id':   inv_brw.id,
                        'name':         inv_brw.name or _('N/A'),
                        'wh_iva_rate':  inv_brw.partner_id.wh_iva_rate,
                        #~ 'tax_line': [awil_obj._get_tax_lines(cr, uid, i, context=context) for i in inv_brw.tax_line if i.tax_id and i.tax_id.ret]
                        
                        } for inv_brw in inv_obj.browse(cr,uid,inv_ids,context=context)]
        
        res = {'value': {
            'account_id': acc_id,
            'wh_lines':res_wh_lines}
        }

        return res

    #~ ##########################################
    #~ BEGIN DELETE 
    #~ ##########################################
    #~ ESTO SE DEBE BORRAR SI EN EL ONCHANGE 
    #~ DEL DOCUMENTO YA SE ESTA CONSIDERANDO
    #~ EL BORRADO DE LOS DOCUMENTOS QUE ESTABAN
    #~ PREVIAMENTE
    #~ ##########################################
    
    def _update_check(self, cr, uid, ids, partner_id, context={}):
        if ids:
            ret = self.browse(cr, uid, ids[0])
            inv_str = ''
            for line in ret.wh_lines:
                if line.invoice_id.partner_id.id != partner_id:
                    inv_str+= line.invoice_id.name and '%s'% '\n'+line.invoice_id.name or ''

            if inv_str:
                raise osv.except_osv('Incorrect Invoices !',"The following invoices are not the selected partner: %s " % (inv_str,))

        return True

    #~ ##########################################
    #~ END DELETE 
    #~ ##########################################


    def _new_check(self, cr, uid, values, context={}):
        lst_inv = []

        if 'wh_lines' in values and values['wh_lines']:
            if 'partner_id' in values and values['partner_id']:
                for l in values['wh_lines']:
                    if 'invoice_id' in l[2] and l[2]['invoice_id']:
                        lst_inv.append(l[2]['invoice_id'])

        if lst_inv:
            invoices = self.pool.get('account.invoice').browse(cr, uid, lst_inv)
            inv_str = ''
            for inv in invoices:
                if inv.partner_id.id != values['partner_id']:
                    inv_str+= '%s'% '\n'+inv.name        

            if inv_str:
                raise osv.except_osv('Incorrect Invoices !',"The following invoices are not the selected partner: %s " % (inv_str,))

        return True


    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if not context:
            context={}
        ret = self.browse(cr, uid, ids[0])
        if update_check:
            if 'partner_id' in vals and vals['partner_id']:
                self._update_check(cr, uid, ids, vals['partner_id'], context)
            else:
                self._update_check(cr, uid, ids, ret.partner_id.id, context)

        return super(account_wh_iva, self).write(cr, uid, ids, vals, context=context)


    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        if check:
            self._new_check(cr, uid, vals, context)
            
        code = self.pool.get('ir.sequence').get(cr, uid, 'account.wh.iva')
        vals['code'] = code
        return super(account_wh_iva, self).create(cr, uid, vals, context)


    def compute_amount_wh(self, cr, uid, ids, context=None):
        res = {}
        if context is None:
            context = {}      
        awil_obj = self.pool.get('account.wh.iva.line')
        for retention in self.browse(cr, uid, ids, context):
            
            #~ res[retention.id] = {
                #~ 'tot_amount_base_wh': 0.0,
                #~ 'tot_amount_tax_wh': 0.0
            #~ }
            whl_ids = [line.id for line in retention.wh_lines]
            if whl_ids:
                awil_obj.load_taxes(cr, uid, whl_ids , context=context)
                
                #~ res[retention.id]['tot_amount_base_wh'] += line.amount_base_wh
                #~ res[retention.id]['tot_amount_tax_wh'] += line.amount_tax_wh
        #~ self.write(cr, uid, [retention.id], res[retention.id])        
        return True
    
account_wh_iva()
