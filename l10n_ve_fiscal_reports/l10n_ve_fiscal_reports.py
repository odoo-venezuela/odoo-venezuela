# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar.hernandez@netquatro.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config

class fiscal_reports_purchase(osv.osv):
    _name = "fiscal.reports.purchase"
    _description = "Purchase by period"
    _auto = False
    _rec_name = 'ai_nro_ctrl'
    _columns = {
        'ai_date_invoice': fields.date('Date'),
        'rp_vat':fields.char('VAT Number', size=24, required=False, readonly=True),
        'rp_id':fields.many2one('res.partner', 'Partner Name', required=True),
        'ai_nro_ctrl':fields.char('Control No.', size=128, required=False, readonly=True),
        'ai_reference':fields.char('Invoice Number', size=128, required=False, readonly=True),
        'ai_amount_total': fields.float('Amount Total', digits=(16, int(config['price_accuracy']))),
        'ai_amount_untaxed': fields.float('Untaxed Amount', digits=(16, int(config['price_accuracy']))),
        'ai_amount_tax': fields.float('Tax Amount', digits=(16, int(config['price_accuracy']))),
        'ai_type':fields.char('Document Type', size=64, required=False, readonly=False),
        'rp_retention': fields.float('Whitholding Rate', digits=(16, int(config['price_accuracy']))),
        'ai_id':fields.many2one('account.invoice', 'Invoice Description', required=False),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view fiscal_reports_purchase as (
            SELECT
                 ai."date_invoice" AS ai_date_invoice,
                 rp."vat" AS rp_vat,
                 rp."id" AS rp_id,
                 ai."nro_ctrl" AS ai_nro_ctrl,
                 ai."reference" AS ai_reference,
                 ai."amount_total" AS ai_amount_total,
                 ai."amount_untaxed" AS ai_amount_untaxed,
                 ai."amount_tax" AS ai_amount_tax,
                 ai."type" AS ai_type,
                 rp."retention" AS rp_retention,
                 ai."id" AS id,
                 ai."id" AS ai_id
            FROM
                 "res_partner" rp INNER JOIN "account_invoice" ai ON rp."id" = ai."partner_id"
            WHERE
                 (ai.type = 'in_refund'
              OR ai.type = 'in_invoice')
             AND (ai.state = 'open'
              OR ai.state = 'paid'
              OR ai.state = 'done')
            ORDER BY
                 ai_date_invoice ASC,
                 ai."number" ASC )
        """)
fiscal_reports_purchase()  

class fiscal_reports_sale(osv.osv):
    _name = "fiscal.reports.sale"
    _description = "Sale by period"
    _auto = False
    _rec_name = 'ai_nro_ctrl'
    _columns = {
    'ai_date_invoice': fields.date('Date'),
    'rp_vat':fields.char('VAT Number', size=64, required=False, readonly=False),
    'rp_id':fields.many2one('res.partner', 'Partner Name', required=True),
    'ai_number':fields.char('Invoice Number', size=64, required=False, readonly=False),
    'ai_nro_ctrl':fields.char('Control No.', size=64, required=False, readonly=False),
    'ai_amount_total': fields.float('Amount Total', digits=(16, int(config['price_accuracy']))),
    'ai_amount_untaxed': fields.float('Untaxed amount', digits=(16, int(config['price_accuracy']))),
    'ai_amount_tax': fields.float('Tax Amount', digits=(16, int(config['price_accuracy']))),
    'ai_type':fields.char('Type', size=64, required=False, readonly=False),
    'rp_retention': fields.float('Withholding', digits=(16, int(config['price_accuracy']))),
    'ai_id':fields.many2one('account.invoice', 'Invoice Description', required=False),
    }
    def init(self, cr):    
        cr.execute("""
            create or replace view fiscal_reports_sale as (
                SELECT
                ai."date_invoice" AS ai_date_invoice,
                rp."vat" AS rp_vat,
                rp."id" AS rp_id,
                ai."number" AS ai_number,
                ai."nro_ctrl" AS ai_nro_ctrl,
                ai."amount_total" AS ai_amount_total,
                ai."amount_untaxed" AS ai_amount_untaxed,
                ai."amount_tax" AS ai_amount_tax,
                ai."type" AS ai_type,
                rp."retention" AS rp_retention,
                ai."id" AS id,
                ai."id" AS ai_id
                FROM
                "res_partner" rp INNER JOIN "account_invoice" ai ON rp."id" = ai."partner_id"
                WHERE
                (ai.type = 'out_refund'
                OR ai.type = 'out_invoice')
                AND (ai.state = 'open'
                OR ai.state = 'paid'
                OR ai.state = 'done')
                ORDER BY
                ai_date_invoice ASC,
                ai."number" ASC
                )
        """)
fiscal_reports_sale()
  
