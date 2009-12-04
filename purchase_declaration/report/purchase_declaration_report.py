import time
import pooler
import copy
from report import report_sxw
import pdb
import re

class purchase_declaration_report( report_sxw.rml_parse ):

    def __init__(self,cr,uid,name,context):
        super(purchase_declaration_report,self).__init__(cr,uid,name,context)

        self.localcontext.update({
            'time': time,
            'get_period': self._get_period,
            'get_invoices': self._get_invoices,
            'get_taxes': self._get_taxes,
        })
        
# hbto
# Retrieve all the periods been selected in the wizard
#
    def _get_period(self, period_id):
        return self.pool.get('account.period').browse(self.cr, self.uid, period_id).name


    
    def _get_invoices(self, base_on, period_list, company_id):
        # Getting access to the table
        tai = self.pool.get('account.invoice')
        
        # Verifying the existance of the periods
        # CAUTION / AUCHTUNG / CUIDADO
        # This part of code has not been optimize due to some
        # irregular behavoir that will be describe in a forecoming
        # bug report (the code regarding this behavior spans from
        # this line below through the following 9 lines)
        if period_list[0][2] :
            pass
        else :
            today = time.strftime('%Y-%m-%d')
            # With this it is being dealt with the issue of the current year
            self.cr.execute ("select id from account_fiscalyear where date_stop > '%s' and date_start < '%s'"%(today,today))
            fy = self.cr.fetchall()
            self.cr.execute ("select id from account_period where fiscalyear_id = %d"%(fy[0][0]))
            periods = self.cr.fetchall()
            for p in periods :
                period_list[0][2].append(p[0])
        
        invoices = []
        
        states = ['open','paid']
        
        for period_id in period_list[0][2]:
            for state in states:
                criteria = [('company_id','=',company_id),
                             ('state','=',state),
                             ('period_id','=',period_id)]
                tai_ids = tai.search(self.cr, self.uid, criteria)
                
                if base_on == 'in_invoice':
                    for each_invoice in tai.browse(self.cr, self.uid, tai_ids):
                        if (each_invoice.type == 'in_invoice' or each_invoice.type == 'in_refund'):
                            invoices.append(each_invoice)
                else:
                    for each_invoice in tai.browse(self.cr, self.uid, tai_ids):
                        if (each_invoice.type == 'out_invoice' or each_invoice.type == 'out_refund'):
                            invoices.append(each_invoice)
        return invoices
        
    def _get_taxes(self,invoice_id):
        tai_tax = self.pool.get('account.invoice.tax')
        tai_tax_ids = tai_tax.search(self.cr, self.uid, [('invoice_id','=',invoice_id)])
        taxes = []
        
        for each_tax in tai_tax.browse(self.cr, self.uid, tai_tax_ids):
            taxes.append(each_tax)
        
        return taxes
        
report_sxw.report_sxw('report.account.purchase.declaration', 
                      'account.invoice', 
                      'addons/purchase_declaration/report/purchase_declaration_report.rml',
                        parser = purchase_declaration_report,
                        header = True )
