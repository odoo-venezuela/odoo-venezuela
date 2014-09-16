#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
#              Yanina Aular              <yanina.aular@vauxoo.com>
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
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp.tools import config
import time
import datetime
from openerp.addons import decimal_precision as dp


class islr_wh_doc(osv.osv):

    def name_get(self,cr, uid, ids, context):
        if not len(ids):
            return []
        res = []
        for item in self.browse(cr, uid, ids, context):
            if item.number and item.state=='done':
                res.append((item.id, '%s (%s)'%(item.number,item.name)))
            else:
                res.append((item.id, '%s'%(item.name)))
        return res

    def _get_type(self, cr, uid, context=None):
        """ Return type of invoice or returns in_invoice
        """
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context=None):
        """ Return a islr journal depending on the type of bill
        """
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        if context.get('type') in ('out_invoice', 'out_refund'):
            res = journal_obj.search(cr, uid, [(
                'type', '=', 'islr_sale')], limit=1)
        else:
            res = journal_obj.search(cr, uid, [(
                'type', '=', 'islr_purchase')], limit=1)
        if res:
            return res[0]
        else:
            raise osv.except_osv(_('Configuration Incomplete.'),
                _("""I couldn't find a journal to execute the Witholding ISLR
                automatically, please create one in Accounting > Configuration > Journals, contact
                to the account manager if you don't have access to this menu.!!!"""))

            return False

    def _get_currency(self, cr, uid, context):
        """ Return the currency of the current company
        """
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate', '=', 1.0)])[0]

    def _get_amount_total(self, cr, uid, ids, name, args, context=None):
        """ Return the cumulative amount of each line
        """
        res = {}
        for rete in self.browse(cr, uid, ids, context):
            res[rete.id] = 0.0
            for line in rete.concept_ids:
                res[rete.id] += line.amount
        return res

    _name = "islr.wh.doc"
    _order = 'date_ret desc, number desc'
    _description = 'Document Income Withholding'
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft': [('readonly', False)]}, required=True, help="Voucher description"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft': [('readonly', False)]}, help="Voucher reference"),
        'number': fields.char('Withhold Number', size=32, readonly=True, states={'draft': [('readonly', False)]}, help="Voucher reference"),
        'type': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('in_refund', 'Supplier Invoice Refund'),
            ('out_refund', 'Customer Invoice Refund'),
        ], 'Type', readonly=True, help="Voucher type"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'State', readonly=True, help="Voucher state"),
        'date_ret': fields.date('Accounting Date', readonly=True, states={'draft': [('readonly', False)]}, help="Keep empty to use the current date"),
        'date_uid': fields.date('Withhold Date', readonly=True, states={'draft': [('readonly', False)]}, help="Voucher date"),
        'period_id': fields.many2one('account.period', 'Period', readonly=True, states={'draft': [('readonly', False)]}, help="Period when the accounts entries were done"),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Account Receivable or Account Payable of partner"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft': [('readonly', False)]}, help="Partner object of withholding"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Currency in which the transaction takes place"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Journal where accounting entries are recorded"),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, help="Company"),
        'amount_total_ret': fields.function(_get_amount_total, method=True, string='Amount Total', type='float', digits_compute=dp.get_precision('Withhold ISLR'),  help="Total Withheld amount"),
        'concept_ids': fields.one2many('islr.wh.doc.line', 'islr_wh_doc_id', 'Income Withholding Concept', readonly=True, states={'draft': [('readonly', False)]}, help='concept of income withholding'),
        'invoice_ids': fields.one2many('islr.wh.doc.invoices',
            'islr_wh_doc_id', 'Withheld Invoices', readonly=True,
            states={'draft': [('readonly', False)]}, help='invoices to be\
            withheld'),
        'islr_wh_doc_id': fields.one2many('account.invoice', 'islr_wh_doc_id', 'Invoices', states={'draft': [('readonly', False)]}, help='refers to document income withholding tax generated in the bill'),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft': [('readonly', False)]}, help="Vendor user"),
        'automatic_income_wh': fields.boolean('Automatic Income Withhold',
                                              help='When the whole process will be check automatically, '
                                              'and if everything is Ok, will be set to done'),
    }

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('islr.wh.doc').retencion_seq_get(cr, uid, context),
        'type': _get_type,
        'state': 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context:
        self.pool.get('res.users').browse(cr, uid, uid,
                                          context=context).company_id.id,
        'user_id': lambda s, cr, u, c: u,
        'automatic_income_wh': False,
    }

    def _check_partner(self, cr, uid, ids, context={}):
        """ Determine if a given partner is a Income Withholding Agent
        """
        rp_obj = self.pool.get('res.partner')
        obj = self.browse(cr, uid, ids[0])
        if obj.type in ('out_invoice', 'out_refund') and \
                rp_obj._find_accounting_partner(obj.partner_id).islr_withholding_agent:
                    return True
        if obj.type in ('in_invoice', 'in_refund') and \
                rp_obj._find_accounting_partner(obj.company_id.partner_id).islr_withholding_agent:
                    return True
        return False

    _constraints = [
        (_check_partner, 'Error! The partner must be income withholding agent.', ['partner_id']),
    ]

    def check_income_wh(self, cr, uid, ids, context=None):
        """ Check invoices to be retained and have
        their fair share of taxes.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj = self.browse(cr, uid, ids[0], context=context)
        res = {}
        #Checks for available invoices to Withhold
        if not obj.invoice_ids:
            raise osv.except_osv(_('Missing Invoices!!!'),
                _('You need to Add Invoices to Withhold Income Taxes!!!'))

        for wh_line in obj.invoice_ids:
            #Checks for xml_id elements when withholding to supplier
            #Otherwise just checks for withholding concepts if any
            if not (wh_line.islr_xml_id or wh_line.iwdl_ids):
                res[wh_line.id] = (wh_line.invoice_id.name,
                                   wh_line.invoice_id.number, wh_line.invoice_id.supplier_invoice_number)
        if res:
            note = _('The Following Invoices Have not yet been withheld:\n\n')
            for i in res:
                note += '* %s, %s, %s\n' % res[i]
            note += _('\nPlease, Load the Taxes to be withheld and Try Again')
            raise osv.except_osv(_(
                'Invoices with Missing Withheld Taxes!'), note)
        return True

    def check_auto_wh(self, cr, uid, ids, context=None):
        """ Tell us if the process already checked and everything was fine.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        obj = self.browse(cr, uid, ids[0], context=context)
        return obj.automatic_income_wh or False

    def check_auto_wh_by_type(self, cr, uid, ids, context=None):
        """ Tell us if the process already checked and everything was
        fine in case of a in_invoice or in_refund
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        brw = self.browse(cr, uid, ids[0], context=context)
        if brw.type in ('out_invoice', 'out_refund'):
            return False
        return brw.automatic_income_wh or False

    def compute_amount_wh(self, cr, uid, ids, context=None):
        """ Calculate the total withholding each invoice
        associated with this document
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        iwdl_obj = self.pool.get('islr.wh.doc.line')

        #~ Searching & Unlinking for concept lines from the current withholding
        iwdl_ids = iwdl_obj.search(cr, uid, [('islr_wh_doc_id', '=', ids[0])],
                context=context)
        if iwdl_ids:
            iwdl_obj.unlink(cr, uid, iwdl_ids,context=context)

        iwd_brw = self.browse(cr, uid, ids[0], context=context)
        for iwdi_brw in iwd_brw.invoice_ids:
            iwdi_obj.load_taxes(cr, uid, iwdi_brw.id, context=context)
        return True

    def validate(self, cr, uid, ids, *args):
        if args[0] in ['in_invoice', 'in_refund'] and args[1] and args[2]:
            return True
        return False

    def action_done(self, cr, uid, ids, context=None):
        """ Call the functions in charge of preparing the document
        to pass the state done
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        self.action_number(cr, uid, ids, context=context)
        self.action_move_create(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def action_process(self, cr, uid, ids, context=None):
        # TODO: ERASE THE REGARDING NODE IN THE WORKFLOW
        # METHOD HAVE BEEN LEFT FOR BACKWARD COMPATIBILITY
        return True

    def action_cancel_process(self, cr, uid, ids, context=None):
        """ Delete all withholding lines and reverses the process of islr
        """
        if not context:
            context = {}
        line_obj = self.pool.get('islr.wh.doc.line')
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        xml_obj = self.pool.get('islr.xml.wh.line')
        wh_doc_id = ids[0]

         #~ DELETED XML LINES
        islr_lines = line_obj.search(cr, uid, [
                                     ('islr_wh_doc_id', '=', wh_doc_id)])
        xml_lines = islr_lines and xml_obj.search(cr, uid, [
                                                  ('islr_wh_doc_line_id', 'in', islr_lines)])
        xml_lines and xml_obj.unlink(cr, uid, xml_lines)

        wh_line_list = line_obj.search(cr, uid, [
                                       ('islr_wh_doc_id', '=', wh_doc_id)])
        line_obj.unlink(cr, uid, wh_line_list)

        doc_inv_list = doc_inv_obj.search(cr, uid, [
                                          ('islr_wh_doc_id', '=', wh_doc_id)])
        doc_inv_obj.unlink(cr, uid, doc_inv_list)

        inv_list = inv_obj.search(cr, uid, [
                                  ('islr_wh_doc_id', '=', wh_doc_id)])
        inv_obj.write(cr, uid, inv_list, {'status': 'no_pro'})

        inv_line_list = inv_line_obj.search(
            cr, uid, [('invoice_id', 'in', inv_list)])
        inv_line_obj.write(cr, uid, inv_line_list, {'apply_wh': False})

        return True

    def retencion_seq_get(self, cr, uid, context=None):
        """ Determinate the next sequence for islr withhold and returns.
        """
        pool_seq = self.pool.get('ir.sequence')
        cr.execute(
            "select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='islr.wh.doc' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._next(cr, uid, [res['id']])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def onchange_partner_id(self, cr, uid, ids, type, partner_id, context=None):
        """ Unlink all taxes when change the partner in the document.
        @param type: invoice type
        @param partner_id: partner id was changed
        """
        context = context or {}
        acc_id = False
        res = {}
        res_wh_lines = []
        rp_obj = self.pool.get('res.partner')
        inv_obj = self.pool.get('account.invoice')

        # Unlink previous iwdi
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        iwdi_ids = ids and iwdi_obj.search(cr, uid,
                                           [('islr_wh_doc_id', '=', ids[0])], context=context)
        if iwdi_ids:
            iwdi_obj.unlink(cr, uid, iwdi_ids, context=context)
            iwdi_ids = []

        # Unlink previous line
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        iwdl_ids = ids and iwdl_obj.search(cr, uid,
                                           [('islr_wh_doc_id', '=', ids[0])], context=context)
        if iwdl_ids:
            iwdl_obj.unlink(cr, uid, iwdl_ids, context=context)
            iwdl_ids = []

        if partner_id:
            acc_part_id = rp_obj._find_accounting_partner(rp_obj.browse(cr, uid, partner_id))
            args = [('state', '=', 'open'),
                    ('islr_wh_doc_id', '=', False),
                    '|',
                    ('partner_id', '=', acc_part_id.id),
                    ('partner_id', 'child_of', acc_part_id.id),
                    ]
            if type in ('out_invoice', 'out_refund'):
                acc_id = acc_part_id.property_account_receivable and \
                    acc_part_id.property_account_receivable.id
                args += [('type', 'in', ('out_invoice', 'out_refund'))]
            else:
                acc_id = acc_part_id.property_account_payable and \
                    acc_part_id.property_account_payable.id
                args += [('type', 'in', ('in_invoice', 'in_refund'))]

            inv_ids = inv_obj.search(cr, uid, args, context=context)
            inv_ids = iwdi_obj._withholdable_invoices(cr, uid, inv_ids,
                                                      context=None)

            for inv_brw in inv_obj.browse(cr, uid, inv_ids, context=context):
                res_wh_lines += [{'invoice_id': inv_brw.id}]

        return {'value': {
            'account_id': acc_id,
            'invoice_ids': res_wh_lines}}

    def on_change_date_ret(self, cr, uid, ids, date_ret, date_uid):
        res = {}
        if date_ret:
            if not date_uid:
                res.update({'date_uid': date_ret})
            obj_per = self.pool.get('account.period')
            per_id = obj_per.find(cr, uid, date_ret)
            res.update({'period_id': per_id and per_id[0]})
        return {'value':res}

    def create(self, cr, uid, vals, context=None, check=True):
        """ When you create a new document, this function is responsible
        for generating the sequence code for the field
        """
        if not context:
            context = {}
        code = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc')
        vals['code'] = code
        return super(islr_wh_doc, self).create(cr, uid, vals, context)

    def action_confirm(self, cr, uid, ids, context=None):
        """ This checking if the provider allows retention is
        automatically verified and checked
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        check_auto_wh = self.browse(cr, uid, ids[0],
                                    context=context).company_id.automatic_income_wh
        return self.write(cr, uid, ids[0], {'state': 'confirmed',
                                            'automatic_income_wh': check_auto_wh}, context=context)

    def action_number(self, cr, uid, ids, context=None):
        """ Is responsible for generating a number for the document
        if it does not have one
        """
        context = context or {}
        obj_ret = self.browse(cr, uid, ids)[0]
        cr.execute('SELECT id, number '
                   'FROM islr_wh_doc '
                   'WHERE id IN ('+','.join(map(str, ids))+')')

        for (id, number) in cr.fetchall():
            if not number:
                number = self.pool.get('ir.sequence').get(
                    cr, uid, 'islr.wh.doc.%s' % obj_ret.type)
            if not number:
                raise osv.except_osv( _("Missing Configuration !"),
                    _('No Sequence configured for Supplier Income Withholding'))
            cr.execute('UPDATE islr_wh_doc SET number=%s '
                       'WHERE id=%s', (number, id))
        return True

    def action_cancel(self, cr, uid, ids, context={}):
        """ The operation is canceled and not allows automatic retention
        """
        #~ if self.browse(cr,uid,ids)[0].type=='in_invoice':
            #~ return True
        self.pool.get('islr.wh.doc').write(
            cr, uid, ids, {'automatic_income_wh': False})

        self.cancel_move(cr, uid, ids)
        self.action_cancel_process(cr, uid, ids, context=context)
        return True

    def cancel_move(self, cr, uid, ids, *args):
        """ Retention cancel documents
        """
        context = {}
        account_move_obj = self.pool.get('account.move')
        for ret in self.browse(cr, uid, ids):
            if ret.state == 'done':
                for ret_line in ret.invoice_ids:
                    ret_line.move_id and account_move_obj.button_cancel(
                        cr, uid, [ret_line.move_id.id])
                    ret_line.write({'move_id':False})
                    ret_line.move_id and account_move_obj.unlink(
                        cr, uid, [ret_line.move_id.id])
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def action_cancel_draft(self, cr, uid, ids, *args):
        """ Back to draft status
        """
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_move_create(self, cr, uid, ids, context=None):
        """ Build account moves related to withholding invoice
        """
        wh_doc_obj = self.pool.get('islr.wh.doc.line')
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_id = None
        doc_brw = None
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        ret = self.browse(cr, uid, ids[0], context=context)
        context.update({'income_wh': True,
                          'company_id': ret.company_id.id})
        acc_id = ret.account_id.id
        if not ret.date_uid:
            self.write(cr, uid, [ret.id], {
                       'date_uid': time.strftime('%Y-%m-%d')})

        if not ret.date_ret:
            self.write(cr, uid, [ret.id], {
                       'date_ret': time.strftime('%Y-%m-%d')})

        # Reload the browse because there have been changes into it
        ret = self.browse(cr, uid, ids[0], context=context)

        period_id = ret.period_id and ret.period_id.id or False
        journal_id = ret.journal_id.id

        if not period_id:
            period_ids = self.pool.get('account.period').search(cr, uid, [('date_start', '<=', ret.date_ret or time.strftime(
                '%Y-%m-%d')), ('date_stop', '>=', ret.date_ret or time.strftime('%Y-%m-%d'))])
            if len(period_ids):
                period_id = period_ids[0]
            else:
                raise osv.except_osv(_('Warning !'), _("Not found a fiscal period to date: '%s' please check!") % (
                    ret.date_ret or time.strftime('%Y-%m-%d')))

        for line in ret.invoice_ids:
            if ret.type in ('in_invoice', 'in_refund'):
                name = 'COMP. RET. ISLR ' + ret.number + \
                    ' Doc. ' + (line.invoice_id.supplier_invoice_number or '')
            else:
                name = 'COMP. RET. ISLR ' + ret.number + \
                    ' Doc. ' + (line.invoice_id.number or '')
            writeoff_account_id = False
            writeoff_journal_id = False
            amount = line.amount_islr_ret
            ret_move = line.invoice_id.ret_and_reconcile(
                amount, acc_id, period_id, journal_id, writeoff_account_id,
                period_id, writeoff_journal_id, ret.date_ret, name,
                line.iwdl_ids, context=context)

            if line.invoice_id.currency_id.id != line.invoice_id.company_id.currency_id.id:
                move_obj = self.pool.get('account.move')
                move_line_obj = self.pool.get('account.move.line')
                move_brw = move_obj.browse(cr, uid, ret_move['move_id'])
                for ml in move_brw.line_id:
                    move_line_obj.write(cr, uid, ml.id,
                            {'currency_id': line.invoice_id.currency_id.id})

                    if ml.credit:

                        amount_currency = line.exchange(
                        ml.credit,
                        line.invoice_id.company_id.currency_id.id,
                        line.invoice_id.currency_id.id,
                        line.invoice_id.date_invoice,
                        )

                        move_line_obj.write(cr, uid, ml.id,
                                {'amount_currency': amount_currency*-1  } )

                    elif ml.debit:

                        amount_currency = line.exchange(
                        ml.debit,
                        line.invoice_id.company_id.currency_id.id,
                        line.invoice_id.currency_id.id,
                        line.invoice_id.date_invoice,
                        )

                        move_line_obj.write(cr, uid, ml.id,
                                {'amount_currency': amount_currency  } )

            # make the withholding line point to that move
            rl = {
                'move_id': ret_move['move_id'],
            }
            # lines = [(op,id,values)] escribir en un one2many
            lines = [(1, line.id, rl)]
            self.write(cr, uid, [ret.id], {
                       'invoice_ids': lines, 'period_id': period_id})

        xml_ids = []
        for line in ret.concept_ids:
            xml_ids += [xml.id for xml in line.xml_ids]
        ixwl_obj.write(cr, uid, xml_ids, {
                       'period_id': period_id}, context=context)
        self.write(cr, uid, ids, {'period_id': period_id}, context=context)
        return True

    def wh_and_reconcile(self, cr, uid, ids, invoice_id, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context=None, name=''):
        """ retain, reconcile and create corresponding journal items
        @param invoice_id: invoice to retain and reconcile
        @param pay_amount: amount payable on the invoice
        @param pay_account_id: payment account
        @param period_id: period for the journal items
        @param pay_journal_id: payment journal
        @param writeoff_acc_id: account for reconciliation
        @param writeoff_period_id: period for reconciliation
        @param writeoff_journal_id: journal for reconciliation
        @param name: withholding voucher name
        """
        inv_obj = self.pool.get('account.invoice')
        rp_obj = self.pool.get('res.partner')
        ret = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        # TODO check if we can use different period for payment and the writeoff line
        #~ assert len(invoice_ids)==1, "Can only pay one invoice at a time"
        invoice = inv_obj.browse(cr, uid, invoice_id)
        acc_part_id = rp_obj._find_accounting_partner(invoice.partner_id)
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice':
                 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]

        date = ret.date_ret

        l1 = {
            'debit': direction * pay_amount > 0 and direction * pay_amount,
            'credit': direction * pay_amount < 0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': acc_part_id.id,
            'ref': invoice.number,
            'date': date,
            'currency_id': False,
        }
        l2 = {
            'debit': direction * pay_amount < 0 and - direction * pay_amount,
            'credit': direction * pay_amount > 0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': acc_part_id.id,
            'ref': invoice.number,
            'date': date,
            'currency_id': False,
        }
        if not name:
            if invoice.type in ['in_invoice', 'in_refund']:
                name = 'COMP. RET. ISLR ' + ret.number + \
                    ' Doc. ' + (invoice.supplier_invoice_number or '')
            else:
                name = 'COMP. RET. ISLR ' + ret.number + \
                    ' Doc. ' + (invoice.number or '')

        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        move = {'ref': invoice.number, 'line_id': lines, 'journal_id':
                pay_journal_id, 'period_id': period_id, 'date': date}
        move_id = self.pool.get('account.move').create(
            cr, uid, move, context=context)

        self.pool.get('account.move').post(cr, uid, [move_id])

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute('select id from account_move_line where move_id in ('+str(
            move_id)+','+str(invoice.move_id.id)+')')
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()))
        for l in lines+invoice.payment_ids:
            if l.account_id.id == src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)
        if (not round(total, self.pool.get('decimal.precision').precision_get(cr, uid, 'Withhold ISLR'))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(
                cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(
                cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger
        # recompute
        self.pool.get('account.invoice').write(
            cr, uid, invoice_id, {}, context=context)
        return {'move_id': move_id}

    def unlink(self, cr, uid, ids, context=None):
        """ Overwrite the unlink method to throw an exception if the
        withholding is not in cancel state."""
        context = context or {}
        for islr_brw in self.browse(cr, uid, ids, context=context):
            if islr_brw.state != 'cancel':
                raise osv.except_osv(_("Invalid Procedure!!"),
                    _("The withholding document needs to be in cancel state to be deleted."))
            else:
                super(islr_wh_doc, self).unlink(cr, uid, islr_brw.id, context=context)
        return True



    def _dummy_cancel_check(self, cr, uid, ids, context=None):
        '''
        This will be the method that another developer should use to create new
        check on Withholding Document
        Make super to this method and create your own cases
        '''
        return True

    def _check_xml_wh_lines(self, cr, uid, ids, context=None):
        """Check if this ISLR WH DOC is being used in a XML ISLR DOC"""
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwd_ids = []
        ixwd_obj = self.pool.get('islr.xml.wh.doc')
        for iwd_brw in self.browse(cr, uid, ids, context=context):
            for iwdi_brw in iwd_brw.invoice_ids:
                for ixwl_brw in iwdi_brw.islr_xml_id:
                    if ixwl_brw.islr_xml_wh_doc and ixwl_brw.islr_xml_wh_doc.state != 'draft':
                        ixwd_ids += [ixwl_brw.islr_xml_wh_doc.id]

        if not ixwd_ids: return True

        note = _('The Following ISLR XML DOC should be set to Draft before Cancelling this Document\n\n')
        for ixwd_brw in ixwd_obj.browse(cr, uid, ixwd_ids, context = context):
            note += '%s\n'%ixwd_brw.name
        raise osv.except_osv( _("Invalid Procedure!"), note)
        return True

    def cancel_check(self, cr, uid, ids, context=None):
        '''
        Unique method to check if we can cancel the Withholding Document
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        if not self._check_xml_wh_lines(cr, uid, ids, context=context):
            return False
        if not self._dummy_cancel_check(cr, uid, ids, context=context):
            return False
        return True

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def _get_inv_from_iwdi(self, cr, uid, ids, context=None):
        '''
        Returns a list of invoices which are recorded in VAT Withholding Docs
        '''
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        iwdi_brws = iwdi_obj.browse(cr, uid, ids, context=context)
        return [i.invoice_id.id for i in iwdi_brws if i.invoice_id]

    def _get_inv_from_iwd(self, cr, uid, ids, context=None):
        '''
        Returns a list of invoices which are recorded in VAT Withholding Docs
        '''
        res = []
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwd_obj = self.pool.get('islr.wh.doc')
        iwd_brws = iwd_obj.browse(cr, uid, ids, context=context)
        for iwd_brw in iwd_brws:
            for iwdl_brw in iwd_brw.invoice_ids:
                iwdl_brw.invoice_id and res.append(iwdl_brw.invoice_id.id)
        return res

    def _fnct_get_wh_income_id(self, cr, uid, ids, name, args, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwdi_obj = self.pool.get('islr.wh.doc.invoices')
        iwdi_ids = iwdi_obj.search(cr, uid, [('invoice_id','in',ids)], context=context)

        iwdi_brws = iwdi_obj.browse(cr, uid, iwdi_ids, context=context)
        res = {}.fromkeys(ids,False)
        for i in iwdi_brws:
            if i.invoice_id:
                res[i.invoice_id.id]=i.islr_wh_doc_id.id or False
        return res

    _columns = {
        'islr_wh_doc_id': fields.function(_fnct_get_wh_income_id, method=True,
            type='many2one', relation='islr.wh.doc',
            string='Income Withholding Document',
            store={
                'islr.wh.doc':(_get_inv_from_iwd, ['invoice_ids'], 50),
                'islr.wh.doc.invoices':(_get_inv_from_iwdi, ['invoice_id'], 50),
            }, help="Document Income Withholding tax generated from this Invoice"),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """ Initialized id by duplicating
        """
        if default is None:
            default = {}
        default = default.copy()
        default.update({'islr_wh_doc_id': 0})

        return super(account_invoice, self).copy(cr, uid, id, default, context)

class islr_wh_doc_invoices(osv.osv):
    _name = "islr.wh.doc.invoices"
    _description = 'Document and Invoice Withheld Income'

    def _amount_all(self, cr, uid, ids, fieldname, args, context=None):
        """ Return all amount relating to the invoices lines
        """
        res = {}
        for ret_line in self.browse(cr, uid, ids, context):
            res[ret_line.id] = {
                'amount_islr_ret': 0.0,
                'base_ret': 0.0
            }
            if ret_line.invoice_id.type in ('in_invoice', 'in_refund'):
                for line in ret_line.islr_xml_id:
                    res[ret_line.id]['amount_islr_ret'] += line.wh
                    res[ret_line.id]['base_ret'] += line.base
            else:
                for line in ret_line.iwdl_ids:
                    res[ret_line.id]['amount_islr_ret'] += line.amount
                    res[ret_line.id]['base_ret'] += line.base_amount

        return res

    _columns = {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc', 'Withhold Document', ondelete='cascade', help="Document Retention income tax generated from this bill"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', help="Withheld invoice"),
        'supplier_invoice_number':fields.related('invoice_id', 'supplier_invoice_number', type='char', string='Supplier inv. #', size=64, store=False, readonly=True),
        'islr_xml_id': fields.one2many('islr.xml.wh.line', 'islr_wh_doc_inv_id', 'Withholding Lines'),
        'amount_islr_ret': fields.function(_amount_all, method=True, digits=(16, 4), string='Withheld Amount', multi='all', help="Amount withheld from the base amount"),
        'base_ret': fields.function(_amount_all, method=True, digits=(16, 4), string='Base Amount', multi='all', help="Amount where a withholding is going to be compute from"),
        'iwdl_ids': fields.one2many('islr.wh.doc.line', 'iwdi_id', 'Withholding Concepts', help='withholding concepts of this withheld invoice'),
        'move_id': fields.many2one('account.move', 'Journal Entry', ondelete='restrict',
                                   readonly=True, help="Accounting voucher"),
    }

    _rec_rame = 'invoice_id'

    def _check_invoice(self, cr, uid, ids, context=None):
        """ Determine if the given invoices are in Open State
        """
        #import pdb; pdb.set_trace()
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_str = ''
        for iwdi_brw in self.browse(cr, uid, ids):
            if iwdi_brw.invoice_id.state != 'open':
                return False
        return True

    _constraints = [
        (_check_invoice, 'Error! The invoice must be in Open State.', ['invoice_id']),
    ]

    def _get_concepts(self, cr, uid, ids, context=None):
        """ Get a list of withholdable concepts (concept_id) from the invoice lines
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        inv_obj = self.pool.get('account.invoice')
        concept_set = set()
        inv_brw = inv_obj.browse(cr, uid, ids[0], context=context)
        for ail in inv_brw.invoice_line:
            if ail.concept_id and ail.concept_id.withholdable:
                concept_set.add(ail.concept_id.id)
        return list(concept_set)

    def _withholdable_invoices(self, cr, uid, ids, context=None):
        """ Given a list of invoices return only those
        where there are withholdable concepts
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res_ids = []
        for id in ids:
            id = self._get_concepts(cr, uid, id, context=context) and id
            if id:
                res_ids += [id]
        return res_ids

    def exchange(self, cr, uid, ids, from_amount, from_currency_id, to_currency_id, exchange_date, context=None):
        if context is None:
            context = {}
        if from_currency_id == to_currency_id:
            return from_amount
        curr_obj = self.pool.get('res.currency')
        context['date'] = exchange_date
        return curr_obj.compute(cr, uid, from_currency_id, to_currency_id, from_amount, context=context)

    def _get_wh(self, cr, uid, ids, concept_id, context=None):
        """ Return a dictionary containing all the values of the retention of an invoice line.
        @param concept_id: Withholding reason
        """
        # TODO: Change the signature of this method
        # This record already has the concept_id built-in
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        iwdl_brw = iwdl_obj.browse(cr, uid, ids[0], context=context)

        vendor, buyer, wh_agent = self._get_partners(
            cr, uid, iwdl_brw.invoice_id)
        apply = not vendor.islr_exempt
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)

        concept_id = iwdl_brw.concept_id.id
        # rate_base,rate_minimum,rate_wh_perc,rate_subtract,rate_code,rate_id,rate_name
        # Add a Key in context to store date of ret fot U.T. value determination
        # TODO: Future me, this context update need to be checked with the other date in the withholding in order to take into account the customer income withholding.
        context.update({'wh_islr_date_ret':iwdl_brw.islr_wh_doc_id.date_ret or False})
        rate_tuple = self._get_rate(
            cr, uid, concept_id, residence, nature, context=context)
        base = 0
        wh_concept = 0.0

        if iwdl_brw.invoice_id.type in ('in_invoice', 'in_refund'):
            for line in iwdl_brw.xml_ids:
                base_line = self.exchange(cr,
                            uid,
                            ids,
                            line.account_invoice_line_id.price_subtotal,
                            line.account_invoice_line_id.invoice_id.currency_id.id,
                            line.account_invoice_line_id.company_id.currency_id.id,
                            line.account_invoice_line_id.invoice_id.date_invoice
                            )
                base += base_line
            apply = apply and base >= rate_tuple[0]*rate_tuple[1]/100.0
            wh = 0.0
            subtract = apply and rate_tuple[3] or 0.0
            subtract_write = 0.0
            sb_concept = subtract
            for line in iwdl_brw.xml_ids:
                if apply:
                    base_line = self.exchange(cr,
                            uid,
                            ids,
                            line.account_invoice_line_id.price_subtotal,
                            line.account_invoice_line_id.invoice_id.currency_id.id,
                            line.account_invoice_line_id.company_id.currency_id.id,
                            line.account_invoice_line_id.invoice_id.date_invoice
                            )

                    wh_calc = (rate_tuple[0]/100.0)*rate_tuple[
                        2]*base_line/100.0
                    if subtract >= wh_calc:
                        wh = 0.0
                        subtract -= wh_calc
                    else:
                        wh = wh_calc - subtract
                        subtract_write = subtract
                        subtract = 0.0
                ixwl_obj.write(
                    cr, uid, line.id, {
                        'wh': wh, 'sustract': subtract or subtract_write},
                    context=context)
                wh_concept += wh
        else:
            for line in iwdl_brw.invoice_id.invoice_line:
                if line.concept_id.id == concept_id:
                    base_line = self.exchange(cr,
                            uid,
                            ids,
                            line.price_subtotal,
                            line.invoice_id.currency_id.id,
                            line.company_id.currency_id.id,
                            line.invoice_id.date_invoice
                            )
                    base += base_line

            apply = apply and base >= rate_tuple[0]*rate_tuple[1]/100.0
            sb_concept = apply and rate_tuple[3] or 0.0
            if apply:
                wh_concept = (rate_tuple[0]/100.0)*rate_tuple[2]*base/100.0
                wh_concept -= sb_concept
        values = {
            'amount': wh_concept,
            'subtract': sb_concept,
            'base_amount': base,
            'retencion_islr': rate_tuple[2],
            'islr_rates_id': rate_tuple[5],
        }
        iwdl_obj.write(cr, uid, ids[0], values, context=context)
        return True

    def load_taxes(self, cr, uid, ids, context=None):
        """ Load taxes to the current invoice,
        and if already loaded, it recalculates and load.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        ret_line = self.browse(cr, uid, ids[0], context=context)
        lines = []
        rates = {}
        wh_perc = {}
        xmls = {}

        if not ret_line.invoice_id:
            return True

        concept_list = self._get_concepts(cr, uid, ret_line.invoice_id.id,
                                          context=context)

        if ret_line.invoice_id.type in ('in_invoice', 'in_refund'):
            #~ Searching & Unlinking for xml lines from the current invoice
            xml_lines = ixwl_obj.search(cr, uid, [(
                'islr_wh_doc_inv_id', '=', ret_line.id)], context=context)
            if xml_lines:
                ixwl_obj.unlink(cr, uid, xml_lines)

            #~ Creating xml lines from the current invoices again
            ail_brws = [
                i for i in ret_line.invoice_id.invoice_line if i.concept_id and i.concept_id.withholdable]
            for i in ail_brws:
                values = self._get_xml_lines(cr, uid, i, context=context)
                values.update({'islr_wh_doc_inv_id': ret_line.id, })
                if not values.get('invoice_number'):
                    raise osv.except_osv(_("Error on Human Process"),
                    _("Please fill the Invoice number to continue, without this number will be"
                      " imposible form the system make the withholding"))

                #~ Vuelve a crear las lineas
                xml_id = ixwl_obj.create(cr, uid, values, context=context)
                #~ Write back the new xml_id into the account_invoice_line
                i.write({'wh_xml_id': xml_id}, context=context)
                lines.append(xml_id)
                #~ Keeps a log of the rate & percentage for a concept
                rates[i.concept_id.id] = values['rate_id']
                wh_perc[i.concept_id.id] = values['porcent_rete']
                if xmls.get(i.concept_id.id):
                    xmls[i.concept_id.id] += [xml_id]
                else:
                    xmls[i.concept_id.id] = [xml_id]

            #~ Searching & Unlinking for concept lines from the current invoice
            iwdl_ids = iwdl_obj.search(cr, uid, [(
                'invoice_id', '=', ret_line.invoice_id.id)], context=context)
            if iwdl_ids:
                iwdl_obj.unlink(cr, uid, iwdl_ids)
                iwdl_ids = []
            #~ Creating concept lines for the current invoice
            for concept_id in concept_list:
                iwdl_id = iwdl_obj.create(cr, uid,
                                          {'islr_wh_doc_id': ret_line.islr_wh_doc_id.id,
                                           'concept_id': concept_id,
                                           'islr_rates_id': rates[concept_id],
                                           'invoice_id': ret_line.invoice_id.id,
                                           'retencion_islr': wh_perc[concept_id],
                                           'xml_ids': [(6, 0, xmls[concept_id])],
                                           'iwdi_id': ret_line.id,
                                           }, context=context)
                self._get_wh(cr, uid, iwdl_id, concept_id, context=context)
        else:
            #~ Searching & Unlinking for concept lines from the current withholding
            iwdl_ids = iwdl_obj.search(
                cr, uid, [('iwdi_id', '=', ret_line.id)],
                context=context)
            if iwdl_ids:
                iwdl_obj.unlink(cr, uid, iwdl_ids)
                iwdl_ids = []

            for concept_id in concept_list:
                iwdl_id = iwdl_obj.create(cr, uid,
                                          {'islr_wh_doc_id': ret_line.islr_wh_doc_id.id,
                                           'concept_id': concept_id,
                                           'invoice_id': ret_line.invoice_id.id,
                                           }, context=context)
                iwdl_ids += [iwdl_id]
                self._get_wh(cr, uid, iwdl_id, concept_id, context=context)
            self.write(cr, uid, ids[0], {'iwdl_ids': [(6, 0, iwdl_ids)]})
        return True

    def _get_partners(self, cr, uid, invoice):
        """ Is obtained: the seller's id, the buyer's id
        invoice and boolean field that determines whether the buyer is
        retention agent.
        """
        rp_obj = self.pool.get('res.partner')
        inv_part_id = rp_obj._find_accounting_partner(invoice.partner_id)
        comp_part_id = rp_obj._find_accounting_partner(invoice.company_id.partner_id)
        if invoice.type in ('in_invoice', 'in_refund'):
            vendor = inv_part_id
            buyer = comp_part_id
        else:
            buyer = inv_part_id
            vendor = comp_part_id
        return (vendor, buyer, buyer.islr_withholding_agent)

    def _get_residence(self, cr, uid, vendor, buyer):
        """It determines whether the tax form buyer address is the same
        that the seller, then in order to obtain the associated rate.
        Returns True if a person is resident. Returns
        False if is not resident.
        """
        vendor_address = self._get_country_fiscal(cr, uid, vendor)
        buyer_address = self._get_country_fiscal(cr, uid, buyer)
        if vendor_address and buyer_address:
            if vendor_address == buyer_address:
                return True
            else:
                return False
        return False

    def _get_nature(self, cr, uid, partner_id):
        """ It obtained the nature of the seller from VAT, returns
        True if natural person, and False if is legal.
        """
        rp_obj = self.pool.get('res.partner')
        acc_part_id = rp_obj._find_accounting_partner(partner_id)
        if not acc_part_id.vat:
            raise osv.except_osv(_('Invalid action !'), _(
                "Impossible income withholding, because the partner '%s' has not vat associated!") % (acc_part_id.name))
            return False
        else:
            if acc_part_id.vat[2:3] in 'VvEe' or acc_part_id.spn:
                return True
            else:
                return False

    def _get_rate(self, cr, uid, concept_id, residence, nature, context):
        """ Rate is obtained from the concept of retention, provided
        if there is one associated with the specifications:
        The vendor's nature matches a rate.
        The vendor's residence matches a rate.
        """
        ut_obj = self.pool.get('l10n.ut')
        concept_brw = self.pool.get('islr.wh.concept').browse(cr, uid, concept_id)
        rate_brw_lst = concept_brw.rate_ids
        for rate_brw in rate_brw_lst:
            if rate_brw.nature == nature and rate_brw.residence == residence:
                #~ (base,min,porc,sust,codigo,id_rate,name_rate)
                rate_brw_minimum = ut_obj.compute_ut_to_money(
                    cr, uid, rate_brw.minimum, context.get('wh_islr_date_ret',False), context)  # Method that transforms the UVT in pesos
                rate_brw_subtract = ut_obj.compute_ut_to_money(
                    cr, uid, rate_brw.subtract, context.get('wh_islr_date_ret',False), context)  # Method that transforms the UVT in pesos
                return (rate_brw.base, rate_brw_minimum, rate_brw.wh_perc, rate_brw_subtract, rate_brw.code, rate_brw.id, rate_brw.name)
        msg_nature = nature and 'Natural' or u'Jurídica'
        msg_residence = residence and 'Domiciliada' or 'No Domiciliada'
        msg = _(u'No Available Rates for "Persona %s %s" in Concept: "%s"')%(msg_nature, msg_residence, concept_brw.name)
        raise osv.except_osv(_('Missing Configuration'), msg)

    def _get_country_fiscal(self, cr, uid, partner_id, context=None):
        """ Get the country of the partner
        @param partner_id: partner id whom consult your country
        """
        # TODO: THIS METHOD SHOULD BE IMPROVED
        # DUE TO OPENER HAS CHANGED THE WAY PARTNER
        # ARE USED FOR ACCOUNT_MOVE
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        acc_part_id = rp_obj._find_accounting_partner(partner_id)
        if not acc_part_id.country_id:
            raise osv.except_osv(_('Invalid action !'), _(
                "Impossible income withholding, because the partner '%s' country has not been defined in the address!") % (acc_part_id.name))
        else:
            return acc_part_id.country_id.id

    def _get_xml_lines(self, cr, uid, ail_brw, context=None):
        """ Extract information from the document to generate xml lines
        @param ail_brw: invoice of the document
        """
        context = context or {}
        rp_obj = self.pool.get('res.partner')
        acc_part_id = rp_obj._find_accounting_partner(ail_brw.invoice_id.partner_id)
        vendor, buyer, wh_agent = self._get_partners(
            cr, uid, ail_brw.invoice_id)
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)
        rate_base, rate_minimum, rate_wh_perc, rate_subtract, rate_code, rate_id, rate_name = self._get_rate(
            cr, uid, ail_brw.concept_id.id, residence, nature, context=context)

        wh = ((rate_base * ail_brw.price_subtotal / 100) * rate_wh_perc)/100.0

        base_currency = self.exchange(cr,
                uid,
                [],
                ail_brw.price_subtotal,
                ail_brw.invoice_id.currency_id.id,
                ail_brw.company_id.currency_id.id,
                ail_brw.invoice_id.date_invoice
                )

        return {
            'account_invoice_id': ail_brw.invoice_id.id,
            'islr_wh_doc_line_id': False,
            'islr_xml_wh_doc': False,
            'wh': wh,  # I must to look
            'base': base_currency,  # I get it too but from the rate
            'period_id': False,  # We review the definition because it is in NOT NULL
            'invoice_number': ail_brw.invoice_id.supplier_invoice_number,
            'rate_id': rate_id,  # I get it too but from the rate
            'partner_id': acc_part_id.id,  # Warning Depends if is a customer or supplier
            'concept_id': ail_brw.concept_id.id,
            'partner_vat': vendor.vat[2:12],  # Warning Depends if is a customer or supplier
            'porcent_rete': rate_wh_perc,  # I get it too but from the rate
            'control_number': ail_brw.invoice_id.nro_ctrl,
            'sustract': rate_subtract,  # I get it too but from the rate
            'account_invoice_line_id': ail_brw.id,
            'concept_code': rate_code,  # I get it too but from the rate
        }

class islr_wh_doc_line(osv.osv):
    _name = "islr.wh.doc.line"
    _description = 'Lines of Document Income Withholding'

    def _retention_rate(self, cr, uid, ids, name, args, context=None):
        """ Return the retention rate of each line
        """
        res = {}
        for ret_line in self.browse(cr, uid, ids, context=context):
            if ret_line.invoice_id:
                pass
            else:
                res[ret_line.id] = 0.0
        return res

    _columns = {
        'name': fields.char('Description', size=64, help="Description of the voucher line"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete='set null', help="Invoice to withhold"),
        'amount': fields.float('Withheld Amount', digits_compute=dp.get_precision('Withhold ISLR'), help="Withheld amount"),
        'base_amount': fields.float('Base Amount', digits_compute=dp.get_precision('Withhold ISLR'), help="Base amount"),
        'subtract': fields.float('Subtract', digits_compute=dp.get_precision('Withhold ISLR'), help="Subtract"),
        'islr_wh_doc_id': fields.many2one('islr.wh.doc', 'Withhold Document', ondelete='cascade', help="Document Retention income tax generated from this bill"),
        'concept_id': fields.many2one('islr.wh.concept', 'Withholding Concept', help="Withholding concept associated with this rate"),
        'retencion_islr': fields.float('Withholding Rate', digits_compute=dp.get_precision('Withhold ISLR'), help="Withholding Rate"),
        'retention_rate': fields.function(_retention_rate, method=True, string='Withholding Rate', type='float', help="Withhold rate has been applied to the invoice", digits_compute=dp.get_precision('Withhold ISLR')),
        'islr_rates_id': fields.many2one('islr.rates', 'Rates', help="Withhold rates"),
        'xml_ids': fields.one2many('islr.xml.wh.line', 'islr_wh_doc_line_id', 'XML Lines', help='XML withhold invoice line id'),
        'iwdi_id': fields.many2one('islr.wh.doc.invoices', 'Withheld Invoice',
        ondelete='cascade', help="Withheld Invoices"),
    }

