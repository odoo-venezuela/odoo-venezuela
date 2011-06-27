#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier.duran@netquatro.com>             
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import sys
import base64
import decimal_precision as dp

class islr_xml_wh_doc(osv.osv):
    _name = "islr.xml.wh.doc"

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for xml in self.browse(cr,uid,ids,context):
            res[xml.id]= 0.0
            for line in xml.xml_ids:
                res[xml.id] += line.wh
        return res

    def _get_amount_total_base(self,cr,uid,ids,name,args,context=None):
        res = {}
        for xml in self.browse(cr,uid,ids,context):
            res[xml.id]= 0.0
            for line in xml.xml_ids:
                res[xml.id] += line.base
        return res

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'state': fields.selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'State', select=True, readonly=True, help="Voucher state"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True, help="Fiscal year"),
        'period_id':fields.many2one('account.period','Period',required=True, domain="[('fiscalyear_id','=',fiscalyear_id)]", help="Period when the accounts entries were done"),
        'amount_total_ret':fields.function(_get_amount_total,method=True, digits=(16, 2), readonly=True, string='Withhold Income Amount Total', help="Total amount withhold"),
        'amount_total_base':fields.function(_get_amount_total_base,method=True, digits=(16, 2), readonly=True, string='Without Tax Amount Total', help="Total taxable"),
        'xml_ids':fields.one2many('islr.xml.wh.line','islr_xml_wh_doc','XML Document Lines', readonly=True ,domain="[('period_id','=',period_id), ('islr_xml_wh_doc','=',False)]",states={'draft':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft':[('readonly',False)]}),
    }
    _rec_rame = 'company_id'

    _defaults = {
        'state': lambda *a: 'draft',
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        'user_id': lambda s, cr, u, c: u,
    }

    def action_anular1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'draft'})

    def action_confirm1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirmed'})

    def action_done1(self, cr, uid, ids, context={}):
        root = self._xml(cr,uid,ids)
        self._write_attachment(cr,uid,ids,root,context)
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def _write_attachment(self, cr,uid,ids,root,context):
        '''
        Codificar el xml, para guardarlo en la bd y poder verlo en el cliente como attachment
        '''
        fecha = time.strftime('%Y_%m_%d')
        name = 'ISLR_' + fecha +'.'+ 'xml'
        self.pool.get('ir.attachment').create(cr, uid, {
            'name': name,
            'datas': base64.encodestring(root),
            'datas_fname': name,
            'res_model': 'islr.xml.wh.doc',
            'res_id': ids[0],
            }, context=context
        )
        cr.commit()


    def indent(self,elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


    def _xml(self, cr,uid,ids):
        root = ''
        for id in ids:
            wh_brw = self.browse(cr,uid,id)
            
            period = wh_brw.period_id.name.split('/')
            period2 = period[1]+period[0]

            root = Element("RelacionRetencionesISLR")
            root.attrib['RifAgente'] = wh_brw.company_id.partner_id.vat[2:]
            root.attrib['Periodo'] = period2.strip()
            for line in wh_brw.xml_ids:
                detalle = SubElement(root,"DetalleRetencion")
                SubElement(detalle, "RifRetenido").text = line.partner_vat
                SubElement(detalle, "NumeroFactura").text = line.invoice_number
                SubElement(detalle, "NumeroControl").text = line.control_number
                SubElement(detalle, "CodigoConcepto").text = line.concept_code
                SubElement(detalle, "MontoOperacion").text = str(line.base)
                SubElement(detalle, "PorcentajeRetencion").text = str(line.porcent_rete)
        #~ ElementTree(root).write("/home/gabriela/openerp/Gabriela/5.0/Helados Gilda/islr_withholding/xml.xml")
        self.indent(root)
        return tostring(root,encoding="ISO-8859-1")

islr_xml_wh_doc()


class islr_xml_wh_line(osv.osv):
    _name = "islr.xml.wh.line"
    
    _columns = {
        'concept_id': fields.many2one('islr.wh.concept','Withhold  Concept',help="Withhold concept associated with this rate",required=True, ondelete='cascade'),
        'period_id':fields.many2one('account.period','Period',required=True, help="Period when the accounts entries were done"),
        'partner_vat': fields.char('VAT', size=10, required=True, help="Partner VAT"),
        'invoice_number': fields.char('Invoice Number',size=10,required=True, help="Number of invoice"),
        'control_number': fields.char('Control Number',size=8,required=True, help="Reference"),
        'concept_code': fields.char('Concept Code', size=10, required=True, help="Concept code"),
        'base': fields.float('Without Tax Amount', required=True, help="Taxable", digits_compute= dp.get_precision('Withhold ISLR')),
        'porcent_rete': fields.float('% Withhold', required=True, help="Withhold percent", digits_compute= dp.get_precision('Withhold ISLR')),
        'wh':fields.float('Withhold Amount',required=True, help="Withhold amount", digits_compute= dp.get_precision('Withhold ISLR')),
        'rate_id':fields.many2one('islr.rates', 'Person Type',domain="[('concept_id','=',concept_id)]",required=True, help="Person type"),
        'islr_wh_doc_line_id':fields.many2one('islr.wh.doc.line','Withhold Income Document', help="Withhold income document"),
        'account_invoice_line_id':fields.many2one('account.invoice.line','Invoice Line', help="invoice line to hold"),
        'islr_xml_wh_doc': fields.many2one('islr.xml.wh.doc','ISLR XML Document', help="Income tax XML Doc"),
        'partner_id': fields.many2one('res.partner','Partner',required=True, help="Partner hold"),
        'sustract': fields.float('Subtrahend', help="Subtrahend", digits_compute= dp.get_precision('Withhold ISLR')),
    }
    _rec_name = 'partner_id'
    
    _defaults = {
        'invoice_number': lambda *a: '0',
        'control_number': lambda *a: '0',
    }

    def onchange_partner_vat(self, cr, uid, ids, partner_id, context={}):
        partner_brw = self.pool.get('res.partner').browse(cr,uid,partner_id)
        return {'value' : {'partner_vat':partner_brw.vat[2:]}} 
        
        
    def onchange_code_perc(self, cr, uid, ids, rate_id, context={}):
        rate_brw = self.pool.get('islr.rates').browse(cr,uid,rate_id)
        return {'value' : {'porcent_rete':rate_brw.wh_perc,'concept_code':rate_brw.code}} 

islr_xml_wh_line()


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    _columns = {
        'wh_xml_id':fields.many2one('islr.xml.wh.line','XML Id', help="XML withhold line id"),
    }
    _defaults = {
        'wh_xml_id': lambda *a: 0,
    }
account_invoice_line()






