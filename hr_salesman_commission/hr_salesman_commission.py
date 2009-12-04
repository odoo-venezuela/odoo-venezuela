import time
import netsvc
from osv import fields, osv
from tools.translate import _

import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import tools
from tools import config
from tools.misc import currency

   
class salesman_commission_payment(osv.osv):
    _name='salesman.commission.payment'
    _description='Salesman Commissions due to effective payments'
    _columns={
        'commission_number': fields.char('Number', size=64),
        'company_id': fields.many2one('res.company', 'Company', required=True, states={'draft':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Salesman',required=True,states={'draft':[('readonly',False)]}),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True,states={'draft':[('readonly',False)]}),
        'period_ids': fields.many2one('account.period','Periods', required=True, states={'draft':[('readonly',False)]}),
        'payment_ids': fields.many2many('account.move.line','hr_salesman_commission_payment','line_id','payment_id','Payments',states={'draft':[('readonly',False)]}),
        'state': fields.selection([
            ('draft','Draft'),
            ('open','Open'),
            ('done','Done'),
            ('cancel','Cancelled')
        ],'State', select=True, readonly=True),
        'commission_rate' :  fields.float('Rate(%)', digits=(16, int(config['price_accuracy'])),readonly=False),
        'commission_amount': fields.float('Commission', digits=(16, int(config['price_accuracy'])),),
        #'date_created': fields.date('Created Date'),
        #'date_due': fields.date('Due Date'),
        #'date_commissioned' : fields.date('Commissioned Date'),
        #'date_modified' fields.date('Last Modification Date'),
        #REVISAR CON MUCHO DETENIMIENTO
        #'move_line' : fields.many2one(),
        'commission_line_id': fields.one2many('salesman.commission.payment.line', 'commission_id', 'Commission Lines', readonly=True, states={'draft':[('readonly',False)]}),
    }

# Copied from account.py (line 297)
    def _default_company(self, cr, uid, context={}):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
                
    _defaults = {
        'company_id': _default_company,
        'state': lambda *a: 'draft',
    }
    
    def payment_ids_change(self, cr, uid, ids, payment_ids,commission_rate = 0):
        commission_amount = 0
        # payment_ids is a list which contains a tuple which although contains anothe list
        # with the following structure [(a,b,[x,y,z])]
        # so payment_ids[0] yields a tuple (a,b,[x,y,z])
        # and payment_ids[0][2] yields a list with [x,y,z] 
        # which contains the ids of the payments involved 
        if payment_ids[0][2]:
            account = self.pool.get('account.move.line')
            # Retrieving from account.move.line list of debit's entries with the following payment_ids
            for each_pay_ids in payment_ids[0][2]:
                debit_account = account.browse(cr, uid, each_pay_ids)
                commission_amount += debit_account.debit * commission_rate / 100
        return {'value' : {'commission_amount' : commission_amount}}


    def commission_prepare(self, cr, uid, ids, context=None):
        ###############################
        # DELETE THIS AFTER DEBUGGING #
        ###############################
        print 'ESTO ES IDS: ',
        print ids,
        ###############################
        # context: is dictionary where a pair fields vs. value are store to be used afterwards
        if not context:
            context = {}
        # retrieving the lines from the table in the object salesman.commission.payment.line
        tscpl = self.pool.get('salesman.commission.payment.line')
        taml = self.pool.get('account.move.line')
        
        for idx in ids:
            
            # Deleting all those line which complies the commission_id in ids
            cr.execute("DELETE FROM salesman_commission_payment_line WHERE commission_id=%s", (idx,))
            cr.execute("SELECT payment_id FROM hr_salesman_commission_payment WHERE line_id=%s", (idx,))
            payment_ids = cr.fetchall()
            ###############################
            print 'payment_ids: ',
            print payment_ids,
            ###############################
            for id in payment_ids:
                ###############################
                print 'id[0]: ',
                print id[0],
                ###############################
                each_line ={}
                
                each_line['commission_id'] = self.browse(cr,uid,idx,context=context).id
                each_line['date_effective'] = taml.browse(cr,uid,id[0]).date
                each_line['fiscalyear_id'] = taml.browse(cr,uid,id[0]).period_id.fiscalyear_id.id
                each_line['period_id'] = taml.browse(cr,uid,id[0]).period_id.id
                each_line['partner_id'] = taml.browse(cr,uid,id[0]).partner_id.id
                each_line['ref'] = taml.browse(cr,uid,id[0]).ref
                each_line['name'] = taml.browse(cr,uid,id[0]).name
                each_line['journal_id'] = taml.browse(cr,uid,id[0]).journal_id.id
                each_line['debit'] = taml.browse(cr,uid,id[0]).debit
                each_line['commission_rate'] = self.browse(cr,uid,idx,context=context).commission_rate
                each_line['commissioned_amount_line'] = each_line['debit'] * each_line['commission_rate']/100.0
                each_line['user_id'] = self.browse(cr,uid,idx,context=context).user_id.id
                each_line['commission_paid'] = False
                
                ###############################
                print 'each_line: ',
                print each_line,
                ###############################
                tscpl.create(cr, uid, each_line)
        self.pool.get('salesman.commission.payment').write(cr, uid, ids, {'state':'draft'}, context=context)    
            
        return True
salesman_commission_payment()

class salesman_commission_payment_line(osv.osv):
    _name='salesman.commission.payment.line'
    _columns={
        'commission_id' : fields.many2one('salesman.commission.payment','Commission Lines', required=True),
        'date_effective' : fields.date('Effective of the Payment', required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True,states={'draft':[('readonly',False)]}),
        'period_id': fields.many2one('account.period', 'Period', required=True, select=2),
        'partner_id': fields.many2one('res.partner', 'Partner Ref.'),
        'ref': fields.char('Ref.', size=32),
        'name': fields.char('Name', size=64, required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, select=1),
        'debit': fields.float('Debit', digits=(16,2)),
        'commission_rate' :  fields.float('Rate(%)', digits=(16, int(config['price_accuracy'])),readonly=True),
        'commissioned_amount_line' :  fields.float('Commission', digits=(16, int(config['price_accuracy'])),readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman',required=True,states={'draft':[('readonly',False)]}),
        'commission_paid' : fields.boolean('Paid Commission'),
    }
salesman_commission_payment_line()

#domain=[('code','<>','view'), ('code', '<>', 'closed')]
#        'payment_ids': fields.many2many('account.move.line','hr_salesman_commission_payment','move_id','payment_id','Payments'),
#[('account_id.type','=','receivable'), ('invoice','&lt;&gt;',False), ('reconcile_id','=',False)]
