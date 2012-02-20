#~ # -*- coding: utf-8 -*-
from report import report_sxw
import time
from datetime import datetime, timedelta
import datetime as dt


class wh_src_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        
        super(wh_src_report, self).__init__(cr, uid, name, context)
        self.localcontext.update(
        {
            'get_empresa':self.get_empresa,
           
                    })
        self.context= context
        

    def get_empresa(self, partner_id):
        obj_addr = self.pool.get('res.partner.address')
        addr_id =obj_addr.search(self.cr, self.uid, [('type','=','invoice'),('partner_id','=',partner_id)])
        res = {}
        for row in obj_addr.browse(self.cr, self.uid, addr_id):
            res = {
            'street':row.street,
            'phone':row.phone,
            'fax':row.fax,
            'email':row.email,
            'city':row.city,
            'name':row.name,
            'country':row.country_id.name,
            } 
        return res

report_sxw.report_sxw('report.wh.src.report',
                    'account.wh.src',
                     parser= wh_src_report,
                    #~ header= 'internal',
                    rml= 'l10n_ve_withholding_src/report/wh_src_report.rml'
                    )
