# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 26/11/2012
#    Version: 0.0.0.0
#
#    Description: Gets a CSV file from data collector and import it to
#                 sale order
#
##############################################################################
#~ from datetime import datetime
from osv import fields, osv
from tools.translate import _
#~ import pooler
#~ import decimal_precision as dp
#~ import time
#~ import netsvc
#~ import csv
import base64
import libxml2
import functools

##---------------------------------------------------------- employee_income_wh


class employee_income_wh(osv.osv_memory):

    _name = 'employee.income.wh'

    _description = ''

    ##-------------------------------------------------------------------------

    ##------------------------------------------------------- _internal methods

    def _parse_xml_employee_income_wh(self, cr, uid, xml_file, context=None):
        res = []
        try:
            context = context or {}
            xmldoc = libxml2.parseDoc(xml_file)
            cntx = xmldoc.xpathNewContext()
            xpath = '/RelacionRetencionesISLR[@RifAgente="%s" ' \
                'and @Periodo="%s"]' \
                % (context.get('company_vat'), context.get('period_code'))
            varlist = cntx.xpathEval(xpath)
            if not varlist:
                return res
            xpath = '/RelacionRetencionesISLR/DetalleRetencion'
            varlist = cntx.xpathEval(xpath)
            xml_keys = ['RifRetenido',
                        'NumeroFactura',
                        'NumeroControl',
                        'CodigoConcepto',
                        'MontoOperacion',
                        'PorcentajeRetencion',
                        ]
            for item in varlist:
                values = {}
                for k in xml_keys:
                    attr = item.xpathEval(k) or []
                    values.update({k: attr and attr[0].get_content() or False})
                res.append(values)
        except:
            pass
        return res

    def _clear_xml_employee_income_wh(self, cr, uid, context=None):
        context = context or {}
        if context.get('islr_xml_wh_doc_id'):
            obj_ixwl = self.pool.get('islr.xml.wh.line')
            unlink_ids = obj_ixwl.search(
                cr, uid,
                [('islr_xml_wh_doc', '=', context['islr_xml_wh_doc_id']),
                 ('type', '=', 'employee')])
            if unlink_ids:
                obj_ixwl.unlink(cr, uid, unlink_ids, context=context)
        return True

    def _get_xml_employee_income_wh(self, cr, uid, xml_list, context=None):
        """"
                                                 \\\
                                                 ///
                                                 \\\
                                                 ///
                                                 \\\
                                                 ///
        ----------------------------------------#####
        ----------------------------------------#####

        Pro python Marty Alchin, Pag  75, Memoization
        """

        def memoize(func):
            cache = {}

            @functools.wraps(func)
            def wrapper(*args):
                if args in cache:
                    return cache[args]
                result = func(*args)
                cache[args] = result
                return result
            return wrapper

        @memoize
        def find_data(obj, field, operator, value):
            ids = obj.search(cr, uid, [(field, operator, value)])
            if len(ids) == 1:
                return ids[0]
            return False

        context = context or {}
        field_map = {'RifRetenido': 'partner_vat',
                     'NumeroFactura': 'invoice_number',
                     'NumeroControl': 'control_number',
                     'CodigoConcepto': 'concept_code',
                     'MontoOperacion': 'base',
                     'PorcentajeRetencion': 'porcent_rete',
                     }
        obj_pnr = self.pool.get('res.partner')
        obj_irt = self.pool.get('islr.rates')
        valid = []
        invalid = []
        for item in xml_list:
            data = {}
            for key, data_key in field_map.items():
                data[data_key] = item[key]
            pnr_id = find_data(
                obj_pnr, 'vat', '=', 'VE%s' % data.get('partner_vat'))
            if pnr_id:
                data.update({'partner_id': pnr_id})
            irt_id = find_data(
                obj_irt, 'code', '=', data.get('concept_code'))
            if irt_id:
                irt_brw = obj_irt.browse(cr, uid, irt_id, context=context)
                data.update({'concept_id': irt_brw.concept_id.id,
                             'rate_id': irt_id})
            data.update({
                'wh': float(data['base']) * float(data['porcent_rete']) / 100,
                'period_id': context.get('default_period_id'),
                'islr_xml_wh_doc': context.get('islr_xml_wh_doc_id'),
                'type': 'employee',
                })
            if pnr_id and irt_id:
                valid.append(data)
            else:
                invalid.append(data)

        return valid, invalid

    ##--------------------------------------------------------- function fields

    _columns = {
        'name': fields.char('File name', size=128, readonly=True),
        'obj_file': fields.binary('XML file', required=True, filters='*.xml',
                                  help=("XML file name with employee income "
                                        "withholding data")),
        }

    _defaults = {
        }

    _sql_constraints = [
        ]

    ##-------------------------------------------------------------------------

    ##---------------------------------------------------------- public methods

    ##-------------------------------------------------------- buttons (object)

    def process_employee_income_wh(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        eiw_brw = self.browse(cr, uid, ids, context={})[0]
        file = eiw_brw.obj_file
        xml_file = base64.decodestring(file)
        try:
            unicode(xml_file, 'utf8')
        except Exception:  # If we can not convert to UTF-8 maybe the file
                           # is codified in ISO-8859-15: We convert it.
            xml_file = unicode(xml_file, 'iso-8859-15').encode('utf-8')
        invalid = []
        values = self._parse_xml_employee_income_wh(
            cr, uid, xml_file, context=context)
        obj_ixwl = self.pool.get('islr.xml.wh.line')
        if values:
            self._clear_xml_employee_income_wh(cr, uid, context=context)
            valid, invalid = self._get_xml_employee_income_wh(
                cr, uid, values, context=context)
            for data in valid:
                obj_ixwl.create(cr, uid, data, context=context)
        if not values or invalid:
            msg = _('Not imported data:\n') if invalid else \
                _('Empty or Invalid XML File '
                  '(you should check both company vat and period too)')
            for item in invalid:
                msg += 'RifRetenido: %s\n' % item['partner_vat']
            raise osv.except_osv(_('Error!'), msg)

        return {'type': 'ir.actions.act_window_close'}

    ##------------------------------------------------------------ on_change...

    ##----------------------------------------------------- create write unlink

    ##---------------------------------------------------------------- Workflow

employee_income_wh()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
