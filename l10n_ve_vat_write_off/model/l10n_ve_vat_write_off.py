from openerp.osv import fields, osv
from datetime import datetime, timedelta

class vat_write_off(osv.osv):
    _description = ''
    _name = 'vat.write.off'
    _columns = {
        'company_id':fields.many2one('res.company','Company',
            help='Company',required=True),
        'period_id':fields.many2one('account.period','Period',
            help="Book's Fiscal Period",required=True),
        'state': fields.selection([('draft','Getting Ready'),
            ('open','Approved by Manager'),('done','Seniat Submitted')],
            string='Status', required=True),          
        'purchase_fb_id':fields.many2one('fiscal.book', 'Purchase Fiscal Book',
            help='Purchase Fiscal Book'), 
        'sale_fb_id':fields.many2one('fiscal.book', 'Sale Fiscal Book',
            help='Sale Fiscal Book'),
        'start_date' : fields.date(string='Start date'),
        'vat' : fields.related('company_id',
							   'partner_id',
							   'vat',
							   type='char',
							   string='TIN',
							   readonly=True,
							   store=True),
							   
        
    }
    _defaults = {
        'state': 'draft',
        'company_id': lambda s,c,u,ctx: \
            s.pool.get('res.users').browse(c,u,u,context=ctx).company_id.id,
        'start_date': fields.date.today, 
    }
