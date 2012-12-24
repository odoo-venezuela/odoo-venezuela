#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha hbto@vauxoo.com
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
import decimal_precision as dp

class islr_wh_doc(osv.osv):

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type')
        type2journal = {'out_invoice': 'retislrSale', 'in_invoice': 'retislrPurchase', 'out_refund': 'retislrSale', 'in_refund': 'retislrPurchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'retislrPurchase'))], limit=1)
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

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for rete in self.browse(cr,uid,ids,context):
            res[rete.id]= 0.0
            for line in rete.concept_ids:
                res[rete.id] += line.amount
        return res

    def _get_period(self,cr,uid,ids,name,args,context={}):
        res = {}
        wh_doc_brw = self.browse(cr,uid,ids, context=None)
        for doc in wh_doc_brw:
            res[doc.id] = False
            if doc.date_ret:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',doc.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',doc.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                res[doc.id] = period_id
        return res

    def filter_lines_invoice(self,cr,uid,partner_id,context):
        inv_obj = self.pool.get('account.invoice')
        invoice_obj = self.pool.get('islr.wh.doc.invoices')
        inv_ids=[]
        
        inv_ids = inv_obj.search(cr,uid,[('state', '=', 'open'),('partner_id','=',partner_id)],context={})
        if inv_ids:
            #~ Get only the invoices which are not in a document yet
            inv_ids = [i.id for i in inv_obj.browse(cr,uid,inv_ids,context={})  if not i.islr_wh_doc_id]
            inv_ids = [i for i in inv_ids if not invoice_obj.search(cr, uid, [('invoice_id', '=', i)])]
            inv_ids = [i.id for i in inv_obj.browse(cr, uid, inv_ids, context={}) for d in i.invoice_line if d.concept_id.withholdable]
            inv_ids = list(set(inv_ids))
        return inv_ids
    
    _name = "islr.wh.doc"
    _description = 'Document Withholding Income'
    _columns= {
        'name': fields.char('Description', size=64,readonly=True, states={'draft':[('readonly',False)]}, required=True, help="Voucher description"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Voucher reference"),
        'number': fields.char('Withhold Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Voucher reference"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('in_refund','Supplier Invoice Refund'),
            ('out_refund','Customer Invoice Refund'),
            ],'Type', readonly=True, help="Voucher type"),
        'state': fields.selection([
            ('to_process','To Process'),
            ('progress','Progress'),
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'State', readonly=True, help="Voucher state"),
        'date_ret': fields.date('Accounting Date', help="Keep empty to use the current date"),
        'date_uid': fields.date('Withhold Date', readonly=True, states={'draft':[('readonly',False)]}, help="Voucher date"),
        'period_id': fields.function(_get_period, method=True, required=False, type='many2one',relation='account.period', string='Period', help="Period when the accounts entries were done"),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Account Receivable or Account Payable of partner"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Partner object of withholding"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency in which the transaction takes place"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal where accounting entries are recorded"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'amount_total_ret':fields.function(_get_amount_total,method=True, string='Amount Total', type='float', digits_compute= dp.get_precision('Withhold ISLR'),  help="Total Withheld amount"),
        'concept_ids': fields.one2many('islr.wh.doc.line','islr_wh_doc_id','Withholding Income Concept', readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_ids':fields.one2many('islr.wh.doc.invoices','islr_wh_doc_id','Withheld Invoices'),
        'invoice_id':fields.many2one('account.invoice','Invoice',readonly=False,help="Invoice to make the accounting entry"),
        'islr_wh_doc_id': fields.one2many('account.invoice','islr_wh_doc_id','Invoices',states={'draft':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft':[('readonly',False)]}),
    }

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('islr.wh.doc').retencion_seq_get(cr, uid, context),
        'type': _get_type,
        'state': 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        'user_id': lambda s, cr, u, c: u,
    }

    def validate(self, cr,uid,ids,*args):

        if args[0]in ['in_invoice','in_refund'] and args[1] and args[2]:
            return True

    def action_process(self,cr,uid,ids, context=None):
        inv_obj=self.pool.get('account.invoice')
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wh_doc_brw = self.browse(cr, uid, ids[0], context=context)
        inv_ids = []
        
        for wh_doc_line in wh_doc_brw.islr_wh_doc_id: 
            inv_ids.append(wh_doc_line.id)
        context["wh_doc_id"]=ids[0]
        inv_obj.action_ret_islr(cr, uid, inv_ids,context)
        return True

    def action_cancel_process(self,cr,uid,ids,context=None):
        if not context:
            context={}
        line_obj = self.pool.get('islr.wh.doc.line')
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        xml_obj = self.pool.get('islr.xml.wh.line')
        wh_doc_id = ids[0]
        
        
         #~ DELETED XML LINES
        islr_lines = line_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        xml_lines = islr_lines and xml_obj.search(cr,uid,[('islr_wh_doc_line_id','in',islr_lines)])
        xml_lines and xml_obj.unlink(cr,uid,xml_lines)
        
        wh_line_list = line_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        line_obj.unlink(cr,uid,wh_line_list)
        
        doc_inv_list = doc_inv_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        doc_inv_obj.unlink(cr,uid,doc_inv_list)
        
        inv_list = inv_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        #~ inv_obj.write(cr, uid, inv_list, {'status':'no_pro','islr_wh_doc_id':None}) REVISAR 
        inv_obj.write(cr, uid, inv_list, {'status':'no_pro'})
        
        
        
        inv_line_list = inv_line_obj.search(cr,uid,[('invoice_id','in',inv_list)])
        inv_line_obj.write(cr, uid, inv_line_list, {'apply_wh':False})
        
        return True

    def retencion_seq_get(self, cr, uid, context=None):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='islr.wh.doc' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._next(cr, uid, [res['id']])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def onchange_partner_id(self, cr, uid, ids, type, partner_id):
        acc_id = False
        inv_ids=[]

        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
                inv_ids = self.filter_lines_invoice(cr,uid,partner_id,context=None)
            else:
                acc_id = p.property_account_payable.id
        result = {'value': {'islr_wh_doc_id':inv_ids,'account_id': acc_id}}

        return result

    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        code = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc')
        vals['code'] = code
        return super(islr_wh_doc, self).create(cr, uid, vals, context)

    def action_confirm1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirmed'})


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        cr.execute('SELECT id, number ' \
                'FROM islr_wh_doc ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')

        for (id, number) in cr.fetchall():
            if not number:
                number = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc.%s' % obj_ret.type)
            cr.execute('UPDATE islr_wh_doc SET number=%s ' \
                    'WHERE id=%s', (number, id))
        return True

    def action_done1(self, cr, uid, ids, context={}):
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids)
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def action_cancel(self,cr,uid,ids,context={}):
        #~ if self.browse(cr,uid,ids)[0].type=='in_invoice':
            #~ return True
        self.cancel_move(cr,uid,ids)
        self.action_cancel_process(cr,uid,ids,context=context)
        return True
        
    


    def cancel_move (self,cr,uid,ids, *args):
        context={}
        ret_brw = self.browse(cr, uid, ids)
        account_move_obj = self.pool.get('account.move')
        for ret in ret_brw:
            if ret.state == 'done':
                for ret_line in ret.concept_ids:
                    account_move_obj.button_cancel(cr, uid, [ret_line.move_id.id])
                    delete = account_move_obj.unlink(cr, uid,[ret_line.move_id.id])
                if delete:
                    self.write(cr, uid, ids, {'state':'cancel'})
            else:
                self.write(cr, uid, ids, {'state':'cancel'})
        return True


    def action_cancel_draft(self,cr,uid,ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def action_move_create(self, cr, uid, ids, *args):
        wh_doc_obj = self.pool.get('islr.wh.doc.line')
        context = {}
        inv_id = None
        doc_brw = None
        
        for ret in self.browse(cr, uid, ids):
            if not ret.date_uid:
                self.write(cr, uid, [ret.id], {'date_uid':time.strftime('%Y-%m-%d')})

            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})
            
            period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                else:
                    raise osv.except_osv(_('Warning !'), _("Not found a fiscal period to date: '%s' please check!") % (ret.date_ret or time.strftime('%Y-%m-%d')))

            if ret.concept_ids:
                for line in ret.concept_ids:
                    if ret.type in ('in_invoice', 'in_refund'):
                        if line.concept_id.property_retencion_islr_payable:
                            acc_id = line.concept_id.property_retencion_islr_payable.id
                            inv_id = ret.invoice_id.id
                        else:
                            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the account for withholding of sale is not assigned to the Concept withholding '%s'!")% (line.concept_id.name))
                    else:
                        if  line.concept_id.property_retencion_islr_receivable:
                            acc_id = line.concept_id.property_retencion_islr_receivable.id
                            inv_id = line.invoice_id.id
                        else:
                            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the account for withholding of purchase is not assigned to the Concept withholding '%s'!") % (line.concept_id.name))

                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount

                    ret_move = self.wh_and_reconcile(cr, uid, [ret.id], inv_id,
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    #lines = [(op,id,values)] escribir en un one2many
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'concept_ids':lines})
                  
                    if lines:
                        message = _("Withholding income voucher '%s' validated and accounting entry generated.") % self.browse(cr, uid, ids[0]).name
                        self.log(cr, uid, ids[0], message) 
                  
                    for line in ret.concept_ids:
                        for xml in line.xml_ids:
                            if xml.islr_xml_wh_doc.state!='done':
                                if xml.period_id.id != period_id:
                                    self.pool.get('islr.xml.wh.line').write(cr,uid,xml.id,{'period_id':period_id, 'islr_xml_wh_doc':None})
                            else:
                                raise osv.except_osv(_('Invalid action !'),_("Impossible change the period accountig to a withholding that has already been declared."))
#                    inv_obj.write(cr, uid, line.invoice_id.id, {'retention':True}, context=context)
        return True


    def wh_and_reconcile(self, cr, uid, ids, invoice_id, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id,context=None, name=''):
        
        inv_obj = self.pool.get('account.invoice')
        ret = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        #~ assert len(invoice_ids)==1, "Can only pay one invoice at a time"
        invoice = inv_obj.browse(cr, uid, invoice_id)
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
       
        date=ret.date_ret
            
        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False,
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False, 
        }
        if not name:
            if invoice.type in ['in_invoice','in_refund']:
                name = 'COMP. RET. ISLR ' + ret.number + ' Doc. '+ (invoice.reference or '')
            else:
                name = 'COMP. RET. ISLR ' + ret.number + ' Doc. '+ (invoice.number or '')

        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        move = {'ref': invoice.number, 'line_id': lines, 'journal_id': pay_journal_id, 'period_id': period_id, 'date': date}
        move_id = self.pool.get('account.move').create(cr, uid, move, context=context)

        self.pool.get('account.move').post(cr, uid, [move_id])

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute('select id from account_move_line where move_id in ('+str(move_id)+','+str(invoice.move_id.id)+')')
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()) )
        for l in lines+invoice.payment_ids:
            if l.account_id.id==src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)
        if (not round(total,self.pool.get('decimal.precision').precision_get(cr, uid, 'Withhold ISLR'))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, invoice_id, {}, context=context)
        return {'move_id': move_id}


    def action_ret_islr(self, cr, uid, ids, context={}):
        #TODO: :
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        inv_obj = self.pool.get('account.invoice')
        invoices_brw = inv_obj.browse(cr, uid, ids, context)
        wh_doc_list = []
        for invoice in invoices_brw:
            wh_dict={}
            dict_rate={}
            dict_completo={}
            vendor, buyer, apply_wh = inv_obj._get_partners(cr,uid,invoice) # Se obtiene el (vendedor, el comprador, si el comprador es agente de retencion)
            concept_list = inv_obj._get_concepts(cr,uid,invoice)# Se obtiene la lista de conceptos de las lineas de la factura actual.
            if concept_list:  # 2.- Si existe algun concepto de retencion en las lineas de la factura.
                if apply_wh:  # 3.- Si el comprador es agente de retencion
                    wh_dict = inv_obj._get_service_wh(cr, uid, invoice, concept_list) # Se obtiene un dic con la lista de lineas de factura, si se aplico retencion alguna vez, el monto base total de las lineas.
                    residence = iwdi_obj._get_residence(cr, uid, vendor, buyer) # Retorna el tipo de residencia del vendedor
                    nature = iwdi_obj._get_nature(cr, uid, vendor) # Retorna la naturaleza del vendedor.
                    dict_rate = inv_obj._get_rate_dict(cr, uid, concept_list, residence, nature,context) # Retorna las tasas por cada concepto
                    inv_obj._pop_dict(cr,uid,concept_list,dict_rate,wh_dict) # Borra los conceptos y las lineas de factura que no tengan tasa asociada.
                    dict_completo = inv_obj._get_wh_apply(cr,uid,dict_rate,wh_dict,nature) # Retorna el dict con todos los datos de la retencion por linea de factura.
                    islr_wh_doc_id=inv_obj._logic_create(cr,uid,dict_completo,context.get('wh_doc_id',False))# Se escribe y crea en todos los modelos asociados al islr.
                else:
                    raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the supplier '%s' withholding agent is not!") % (buyer.name))
            else:
                raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the lines of the invoice has not concept withholding!"))
            #~ break
        return islr_wh_doc_id


islr_wh_doc()


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Withhold Document',readonly=True,help="Document Withholding Income tax generated from this bill"),
    }
    _defaults = {
        'islr_wh_doc_id': lambda *a: 0,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'islr_wh_doc_id':0 })

        return super(account_invoice, self).copy(cr, uid, id, default, context)
        
account_invoice()
        
        
class islr_wh_doc_invoices(osv.osv):
    _name = "islr.wh.doc.invoices"
    _description = 'Document and Invoice Withheld Income'
    
    def _amount_all(self, cr, uid, ids, fieldname, args, context=None):
        res = {}
        for ret_line in self.browse(cr, uid, ids, context):
            res[ret_line.id] = {
                'amount_islr_ret': 0.0,
                'base_ret': 0.0
            }
            for line in ret_line.islr_xml_id:
                res[ret_line.id]['amount_islr_ret'] += line.wh
                res[ret_line.id]['base_ret'] += line.base

        return res

    _columns= {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Withhold Document', ondelete='cascade', help="Document Retention income tax generated from this bill"),
        'invoice_id':fields.many2one('account.invoice','Invoice', help="Withheld invoice"),
        'islr_xml_id':fields.one2many('islr.xml.wh.line','islr_wh_doc_inv_id','Withholding Lines'),
        'amount_islr_ret':fields.function(_amount_all, method=True, digits=(16,4), string='Withheld Amount', multi='all', help="Amount withheld from the base amount"),
        'base_ret': fields.function(_amount_all, method=True, digits=(16,4), string='Base Amount', multi='all', help="Amount where a withholding is going to be compute from"),
    }
    _rec_rame = 'invoice_id'
    
    def _get_concepts(self, cr, uid, ids, context=None):
        '''
        Gets a list of withholdable concepts (concept_id) from the invoice lines
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_obj = self.pool.get('account.invoice')
        concept_set = set()
        inv_brw = inv_obj.browse(cr, uid, ids[0], context=context)
        for ail in inv_brw.invoice_line:
            if ail.concept_id and ail.concept_id.withholdable:
                concept_set.add(ail.concept_id.id)
        return list(concept_set)

    def _get_wh(self, cr, uid, ids, concept_id, context=None):
        '''
        Returns a dictionary containing all the values ​​of the retention of an invoice line.
        '''
        context= context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj= self.pool.get('islr.xml.wh.line')
        iwdl_obj= self.pool.get('islr.wh.doc.line')
        iwdl_brw = iwdl_obj.browse(cr, uid, ids[0], context=context)

        vendor, buyer, wh_agent = self._get_partners(cr, uid, iwdl_brw.invoice_id)
        apply = not vendor.islr_exempt
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)

        #rate_base,rate_minimum,rate_wh_perc,rate_subtract,rate_code,rate_id,rate_name 
        rate_tuple = self._get_rate(cr, uid, concept_id, residence, nature, context=context)
        base = 0
        for line in iwdl_brw.xml_ids:
            base += line.account_invoice_line_id.price_subtotal
        apply = apply and base >= rate_tuple[0]*rate_tuple[1]/100.0
        wh = 0.0
        subtract = apply and rate_tuple[3] or 0.0
        subtract_write=0.0
        wh_concept = 0.0
        sb_concept = subtract 
        for line in iwdl_brw.xml_ids:
            if apply: 
                wh_calc = (rate_tuple[0]/100.0)*rate_tuple[2]*line.account_invoice_line_id.price_subtotal/100.0
                if subtract >= wh_calc:
                    wh = 0.0
                    subtract -= wh_calc
                else:
                    wh = wh_calc - subtract
                    subtract_write= subtract
                    subtract=0.0
            ixwl_obj.write(cr,uid,line.id,{'wh':wh, 'sustract':subtract or subtract_write},
                    context=context)
            wh_concept+=wh
        iwdl_obj.write(cr, uid, ids[0],{'amount':wh_concept,
            'subtract':sb_concept, 'base_amount': base},context=context)
        return True 


    def load_taxes(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        ret_line = self.browse(cr, uid, ids[0], context=context)
        lines = []
        rates = {}
        wh_perc= {}
        xmls = {}
        if ret_line.invoice_id:
            #~ Searching & Unlinking for xml lines from the current invoice
            xml_lines = ixwl_obj.search(cr, uid, [('islr_wh_doc_inv_id', '=', ret_line.id)],context=context)
            if xml_lines:
                ixwl_obj.unlink(cr, uid, xml_lines)

            #~ Creating xml lines from the current invoices again
            ail_brws= [i for i in ret_line.invoice_id.invoice_line if i.concept_id and i.concept_id.withholdable]
            for i in ail_brws:
                values = self._get_xml_lines(cr, uid, i, context=context)
                values.update({'islr_wh_doc_inv_id':ret_line.id,})
                #~ Vuelve a crear las lineas
                xml_id = ixwl_obj.create(cr, uid, values, context=context)
                lines.append(xml_id)
                #~ Keeps a log of the rate & percentage for a concept
                rates[i.concept_id.id]=values['rate_id']
                wh_perc[i.concept_id.id]=values['porcent_rete']
                if xmls.get(i.concept_id.id):
                    xmls[i.concept_id.id]+=[xml_id] 
                else:
                    xmls[i.concept_id.id]=[xml_id]

            #~ Searching & Unlinking for concept lines from the current invoice  
            iwdl_ids  = iwdl_obj.search(cr, uid, [('invoice_id', '=', ret_line.invoice_id.id)],context=context)
            if iwdl_ids:
                iwdl_obj.unlink(cr, uid, iwdl_ids)
                iwdl_ids=[]
            #~ Creating concept lines for the current invoice
            concept_list = self._get_concepts(cr, uid, ret_line.invoice_id.id, context=context)
            for concept_id in concept_list:
                iwdl_id=iwdl_obj.create(cr,uid,
                        {'islr_wh_doc_id':ret_line.islr_wh_doc_id.id,
                        'concept_id':concept_id,
                        'islr_rates_id':rates[concept_id], 
                        'invoice_id': ret_line.invoice_id.id,
                        'retencion_islr':wh_perc[concept_id], 
                        'xml_ids': [(6,0,xmls[concept_id])],
                        #'amount':dict_concept[key2], #TODO: TO BE SOUGHT
                        }, context=context)
                self._get_wh(cr, uid, iwdl_id, concept_id, context=context)
        return True
        
    def _get_partners(self, cr, uid, invoice):
        '''
        Se obtiene: el id del vendedor, el id del comprador de la factura y el campo booleano que determina si el comprador es agente de retencion.
        '''
        if invoice.type == 'in_invoice' or invoice.type == 'in_refund':
            vendor = invoice.partner_id
            buyer = invoice.company_id.partner_id
            ret_code = invoice
        else:
            buyer = invoice.partner_id
            vendor = invoice.company_id.partner_id
        return (vendor, buyer, buyer.islr_withholding_agent)
        
    def _get_residence(self, cr, uid, vendor, buyer):
        '''
        Se determina si la direccion fiscal del comprador es la misma que la del vendedor, con el fin de luego obtener la tasa asociada.
        Retorna True si es una persona domiciliada o residente. Retorna False si es, no Residente o No Domicialiado.
        '''
        vendor_address = self._get_country_fiscal(cr, uid, vendor)
        buyer_address = self._get_country_fiscal(cr, uid, buyer)
        if vendor_address and buyer_address:
            if vendor_address ==  buyer_address:
                return True
            else:
                return False
        return False

    def _get_nature(self, cr, uid, partner_id):
        '''
        Se obtiene la naturaleza del vendedor a partir del RIF, retorna True si es persona de tipo natural, y False si es juridica.
        '''
        if not partner_id.vat:
            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the partner '%s' has not vat associated!") % (partner_id.name))
            return False
        else:
            if partner_id.vat[2:3] in 'VvEe' or partner_id.spn:
                return True
            else:
                return False

    def _get_rate(self, cr, uid, concept_id, residence, nature,context):
        '''
        Se obtiene la tasa del concepto de retencion, siempre y cuando exista uno asociado a las especificaciones:
            La naturaleza del vendedor coincida con una tasa.
            La residencia del vendedor coindica con una tasa.
        '''
        ut_obj = self.pool.get('l10n.ut')
        rate_brw_lst = self.pool.get('islr.wh.concept').browse(cr, uid, concept_id).rate_ids
        for rate_brw in rate_brw_lst:
            if rate_brw.nature == nature and rate_brw.residence == residence:
                #~ (base,min,porc,sust,codigo,id_rate,name_rate)
                rate_brw_minimum = ut_obj.compute_ut_to_money(cr, uid, rate_brw.minimum, False, context)#metodo que transforma los UVT en pesos
                rate_brw_subtract = ut_obj.compute_ut_to_money(cr, uid, rate_brw.subtract, False, context)#metodo que transforma los UVT en pesos
                return (rate_brw.base, rate_brw_minimum, rate_brw.wh_perc, rate_brw_subtract,rate_brw.code,rate_brw.id,rate_brw.name)
        return ()

    def _get_country_fiscal(self,cr, uid, partner_id,context=None):
        '''
        Get the country of the partner
        '''
        #TODO: THIS METHOD SHOULD BE IMPROVED
        #DUE TO OPENER HAS CHANGED THE WAY PARTNER
        #ARE USED FOR ACCOUNT_MOVE
        context = context or {}
        if not partner_id.country_id:
            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the partner '%s' country has not been defined in the address!") % (partner_id.name))
        else:
            return partner_id.country_id.id
        
    def _get_xml_lines(self, cr, uid, ail_brw, context=None):
        context = context or {}
        vendor, buyer, wh_agent = self._get_partners(cr, uid, ail_brw.invoice_id)
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)
        rate_base,rate_minimum,rate_wh_perc,rate_subtract,rate_code,rate_id,rate_name = self._get_rate(cr, uid, ail_brw.concept_id.id, residence, nature,context=context)
        
        wh = ((rate_base * ail_brw.price_subtotal /100) * rate_wh_perc)/100.0
        
        return {
            'account_invoice_id':ail_brw.invoice_id.id,
            'islr_wh_doc_line_id':False,
            'islr_xml_wh_doc':False,
            'wh':wh, # Debo buscarlo
            'base':ail_brw.price_subtotal, # La consigo tambien pero desde el rate
            'period_id':False, # Debemos revisar la definicion porque esta en NOT NULL
            'invoice_number':ail_brw.invoice_id.reference,
            'rate_id':rate_id, # La consigo tambien pero desde el rate
            'partner_id':ail_brw.invoice_id.partner_id.id, #Warning Depende de si es cliente o proveedor
            'concept_id':ail_brw.concept_id.id,
            'partner_vat':vendor.vat[2:12], #Warning Depende si es cliente o proveedor
            'porcent_rete':rate_wh_perc, # La consigo tambien pero desde el rate
            'control_number':ail_brw.invoice_id.nro_ctrl,
            'sustract':rate_subtract,# La consigo tambien pero desde el rate
            'account_invoice_line_id':ail_brw.id,
            'concept_code':rate_code,# La consigo tambien pero desde el rate
        }

islr_wh_doc_invoices()


class islr_wh_doc_line(osv.osv):
    _name = "islr.wh.doc.line"
    _description = 'Lines of Document Withholding Income'

    def _retention_rate(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ret_line in self.browse(cr, uid, ids, context=context):
            if ret_line.invoice_id:
                pass
            else:
                res[ret_line.id] = 0.0
        return res

    _columns= {
        'name': fields.char('Description', size=64, help="Description of the voucher line"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete='set null', help="Invoice to withhold"),
        'amount':fields.float('Withheld Amount', digits_compute= dp.get_precision('Withhold ISLR'), help="Withheld amount"),
        'base_amount':fields.float('Base Amount', digits_compute= dp.get_precision('Withhold ISLR'), help="Base amount"),
        'subtract':fields.float('Subtract', digits_compute= dp.get_precision('Withhold ISLR'), help="Subtract"),
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Withhold Document', ondelete='cascade', help="Document Retention income tax generated from this bill"),
        'concept_id': fields.many2one('islr.wh.concept','Withholding Concept', help="Withholding concept associated with this rate"),
        'retencion_islr':fields.float('Percentage', digits_compute= dp.get_precision('Withhold ISLR'), help="Withholding percentage"),
        'retention_rate': fields.function(_retention_rate, method=True, string='Withholding Rate', type='float', help="Withhold rate has been applied to the invoice", digits_compute= dp.get_precision('Withhold ISLR')),
        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True, help="Accounting voucher"),
        'islr_rates_id': fields.many2one('islr.rates','Rates', help="Withhold rates"),
        'xml_ids':fields.one2many('islr.xml.wh.line','islr_wh_doc_line_id','XML Lines'),        
    }

islr_wh_doc_line()
