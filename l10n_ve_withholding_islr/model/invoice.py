#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
import netsvc

class account_invoice_line(osv.osv):
    '''
    It adds a field that determines if a line has been retained or not
    '''
    _inherit = "account.invoice.line"
    _columns = {
        'apply_wh': fields.boolean('Withheld',help="Indicates whether a line has been retained or not, to accumulate the amount to withhold next month, according to the lines that have not been retained."),
        'concept_id': fields.many2one('islr.wh.concept','Withholding  Concept',help="Concept of Withholding Income asociate this rate",required=False),
    }
    _defaults = {
        'apply_wh': lambda *a: False,
    }

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id     =False, context=None, company_id=None):
        '''
        Onchange to show the concept of retention associated with the product at once in the line of the bill
        '''
        if context is None:
            context = {}
        data = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id     =False, context=None, company_id=None)
        if product:
            pro = self.pool.get('product.product').browse(cr, uid, product, context=context)
            data[data.keys()[1]]['concept_id'] = pro.concept_id.id
        return data
        
    
    def create(self, cr, uid, vals, context=None):
        
        if context is None :
            context = {}
        
        if context.get('new_key',False):

            vals.update({'wh_xml_id':False,
                         'apply_wh': False,
                
            })
        
        return super(account_invoice_line, self).create(cr, uid, vals, context=context)
    

account_invoice_line()


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    _columns = {
        'status': fields.selection([
            ('pro','Processed withholding, xml Line generated'),
            ('no_pro','Withholding no processed'),
            ('tasa','Not exceed the rate,xml Line generated'),
            ],'Status',readonly=True,
            help=' * The \'Processed withholding, xml Line generated\' state is used when a user is a withhold income is processed. \
            \n* The \'Withholding no processed\' state is when user create a invoice and withhold income is no processed. \
            \n* The \'Not exceed the rate,xml Line generated\' state is used when user create invoice,a invoice no exceed the minimun rate.'),
    }
    _defaults = {
        'status': lambda *a: "no_pro",
    }

    def copy(self, cr, uid, id, default=None, context=None):
        
        if default is None:
            default = {}
        
        if context is None :
            context = {}
            
        default = default.copy()
        default.update({'islr_wh_doc':0,
                        'status': 'no_pro',
        })
        
        context.update({'new_key':True})
        
        return super(account_invoice, self).copy(cr, uid, id, default, context)


    def _refund_cleanup_lines(self, cr, uid, lines):
        data = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        list = []
        for x,y,res in data:
            if 'concept_id' in res:
                res['concept_id'] = res.get('concept_id', False) and res['concept_id']
            if 'apply_wh' in res:
                res['apply_wh'] = False
            if 'wh_xml_id' in res:
                res['wh_xml_id'] = 0
            list.append((x,y,res))
        return list

    def _get_partners(self, cr, uid, invoice):
        '''
        Get the seller id, the buyer id from the invoice, and the boolean field that determines whether the buyer is the withholding agent
        '''
        if invoice.type == 'in_invoice' or invoice.type == 'in_refund':
            vendor = invoice.partner_id
            buyer = invoice.company_id.partner_id
        else:
            buyer = invoice.partner_id
            vendor = invoice.company_id.partner_id
        return (vendor, buyer, buyer.islr_withholding_agent)

    def _get_concepts(self, cr, uid, invoice):
        '''
        Gets a list of concepts (cocenpt_id) from the invoice lines
        '''
        service_list = []
        for invoice_line in invoice.invoice_line:
            if invoice_line.concept_id and invoice_line.concept_id.withholdable:
                service_list.append(invoice_line.concept_id.id)
            else:
                pass
        return list(set(service_list))
        
    def _get_service_wh(self, cr, uid, invoice, concept_list):
        '''
        Gets all the vendor invoice lines, filtering by the period of the current invoice and the invoice state equal to {done, onpen}
        The lines are stored in a dictionary, where the first key is the list of lines obtained, the second key is the field that indicates wheter any of these line was withholding, and the third key is the sum of the base of all the lines that have not withholding applied
        A search in the lines is done seeking for lines that have withholding concepts equals to the current invoice. This is done to verify:
            1.- If exist the same concepts in another invoice line that have not been withholding cause the amount have no exceeded the minimum value therefore this amount its taken to perform the sum and verification. If the amount exceeds the minimun then withholding is applied to the associated invoices.
            2.- Verify if is the first time that a withholding is applied on that concept, If is true then the subtrahend is applied in the second key "wf" of the dictionary

        '''
        dict={}
        for key in concept_list:
            dict[key]={'lines':[],'wh':False,'base':0.0}
        #~ inv_obj = self.pool.get('account.invoice')
        #~ inv_lst = inv_obj.search(cr, uid,[('partner_id', '=', invoice.partner_id.id),('period_id','=',invoice.period_id.id),('state','in',['done','open'])]) # Lista de  facturas asociadas al proveedor actual, al periodo actual y al estado de las facturas: donde, open.
        #~ 
        #~ inv_line_lst=[]
        #~ for id in inv_lst:
            #~ inv_line_brw = inv_obj.browse(cr, uid, id).invoice_line #lista de lineas de facturas
        for line in invoice.invoice_line:
            if line.concept_id and  line.concept_id.id in concept_list: # Se verifica si el concepto de la linea en la que estoy buscando coincide con alguno de los conceptos de la factura actual.
                if not line.apply_wh: # Se verifica si a la linea no se le ha aplicado retencion, de ser asi se almacena el id de la linea y la base.
                    dict[line.concept_id.id]['lines'].append(line.id)
                    dict[line.concept_id.id]['base']+= line.price_subtotal
                else:  # Si ya se le aplico retencion, no se guarda el id porque no hace falta pero se indica que ya se le aplico retencion.
                    dict[line.concept_id.id]['wh']=True
        #~ dict[key]={'lines':[],'wh':False,'base':0.0}
        return dict

    def _get_country_fiscal(self,cr, uid, partner_id):
        '''
        Gets depending on the parameters the country of the seller or buyer from the fiscal address.
        '''
        for i in partner_id.address:
            if i.type == 'invoice':
                if not i.country_id:
                    raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the partner '%s' country has not defined direction in fiscal!") % (partner_id.name))
                    return False
                else:
                    return i.country_id.id
        raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the partner '%s' has not fiscal direction set!.") % (partner_id.name))
        return False

    def _get_residence(self, cr, uid, vendor, buyer):
        '''
        Determines whether the buyer fiscal address is the same that the seller. with the objective of later get the associated rate.
        Return True if is a domiciled or resident person, False if is not
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
        Gets the nature of the seller from RIF. Return True if is a natural person type, False if is a legal entity.
        '''
        if not partner_id.vat:
            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the partner '%s' has not vat associated!") % (partner_id.name))
            return False
        else:
            if partner_id.vat[2:3] in 'VvEe':
                return True
            else:
                return False

    def _get_rate(self, cr, uid, concept_id, residence, nature,context):
        '''
        Gets the withholding concept rate, provided if is associated to the below specifications:
           - the nature of the seller match with a rate
           - the residence of the seller match with a rate
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
    
    def _get_rate_dict(self, cr, uid, concept_list, residence, nature,context):
        '''
        Returns a dictionary with the rate of each withholding concept.
        '''
        dictd = {}
        cont = 0
        for concept_id in concept_list:
            dictd[concept_id] = self._get_rate(cr, uid, concept_id, residence, nature,context)
            if dictd[concept_id]:
                cont += 1
        if not cont:
            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the Concept of Withholding associated with the line has not rate for the type of customer!"))
        return dictd


    def _pop_dict(self,cr,uid,concept_list,dict_rate,wh_dict):
        '''
        Method to delete all the elements where the withholding concept does not have a rate associated, in the dictionary of concept with rates and in the dictionary of invoice lines.
        '''
        for concept in concept_list:
            if not dict_rate[concept]:
                dict_rate.pop(concept)
                wh_dict.pop(concept)

    def _get_wh_calc(self,cr,uid,line,dict_rate_concept):
        base = self.pool.get('account.invoice.line').browse(cr,uid,line).price_subtotal
        return (base * (dict_rate_concept[0]/100) * (dict_rate_concept[2]/100), base)

    def _get_number(self,cr,uid,number,long):
        num1 = number[::-1]
        result= ''
        for i in num1:
            if i.isdigit():
                if len(result)<long:
                    result = i + result
                else:
                    break
            else:
                break
        return result.strip()


    def _get_inv_data(self,cr, uid, line):
        '''
        Gets the RIF of the supplier, the invoice number and the control number of the invoice. Data required for XML, among others.
        '''
        inv_brw = self.pool.get('account.invoice.line').browse(cr, uid, line).invoice_id
        vat = inv_brw.partner_id.vat[2:]
        if inv_brw.type == 'in_invoice' or inv_brw.type == 'in_refund':
            #~ number = inv_brw.reference.strip() 
            if not inv_brw.reference:
                raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income,because the invoice number: '%s' has not number reference free!") % (inv_brw.number))
                number = 0
            else:
                number = self._get_number(cr,uid,inv_brw.reference.strip(),10)
        else:
            if not inv_brw.number:
                number = 0
            else:
                number = self._get_number(cr,uid,inv_brw.number.strip(),10)
        if not inv_brw.nro_ctrl:
            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the invoice number: '%s' has not control number associated!") % (inv_brw.number))
        else:
            control = self._get_number(cr,uid,inv_brw.nro_ctrl.strip(),8)

        return (vat, number, control)

    def _write_wh_apply(self,cr, uid,line,dict,apply,type):
        '''
        If wh_xml_id field in the invoice line has an associated xml id:
            Write over the boolean field in the invoice line True o False depending on whether it holds withholding or not.
            Write over the xml line the value of the withholding. This happens because it could be created the xml line with a 0.0 withholding (doesnt apply at that time) but if the amount of the withholding exceeds in another invoice, will be override the value with the new withholding amount.
        Otherwise:
            Create a new xml line.
            Write True or False value on the invoice line, and assigns the xml id created in the previuos step.
        '''
        il_ids = self.pool.get('account.invoice.line').browse(cr, uid,line)

        if il_ids.wh_xml_id:
            self.pool.get('account.invoice.line').write(cr, uid, line, {'apply_wh': apply})
            self.pool.get('islr.xml.wh.line').write(cr,uid,il_ids.wh_xml_id.id,{'wh':dict['wh']})
        else:
            if type in ('out_invoice', 'out_refund'):
                self.pool.get('account.invoice.line').write(cr, uid, line, {'apply_wh': apply})
            else:
                self.pool.get('account.invoice.line').write(cr, uid, line, {'apply_wh': apply,'wh_xml_id':self._create_islr_xml_wh_line(cr, uid,line,dict)})
                message = _("Withholding income xml line generated.")
                self.log(cr, uid, line, message)
                
    def _create_islr_xml_wh_line(self,cr, uid, line, dict):
        '''
        Create a new xml line
        '''
        inv_id = self.pool.get('account.invoice.line').browse(cr, uid,line).invoice_id
        return self.pool.get('islr.xml.wh.line').create(cr, uid, {'name': dict['name_rate'],
        'concept_id': dict['concept'], 
        'period_id':  inv_id.period_id.id,
        'partner_vat':dict['vat'],
        'invoice_number': dict['number'],
        'control_number': dict['control'],
        'concept_code':dict['code'],
        'base': dict['subtotal'],
        'porcent_rete':dict['perc'],
        'wh':dict['wh'],
        'rate_id': dict['rate_id'],
        'account_invoice_line_id': line,
        'account_invoice_id': inv_id.id,
        'partner_id': inv_id.partner_id.id,
        })

    def _get_wh(self,cr, uid, subtract,concept, wh_dict, dict_rate, apply,context=None):
        '''
        Returns a dictionary containing all the values ​​of the retention of an invoice line.
        '''
        if context is None:
            context={}
        res= {}
        inv_obj= self.pool.get('account.invoice')
        if apply: # Si se va a aplicar retencion.
            for line in wh_dict[concept]['lines']:
                wh_calc, subtotal = self._get_wh_calc(cr,uid,line,dict_rate[concept]) # Obtengo el monto de retencion y el monto base sobre el cual se retiene
                if subtract >= wh_calc:
                    wh = 0.0
                    subtract -= wh_calc
                else:
                    wh = wh_calc - subtract
                    subtract_write= subtract
                    subtract=0.0
                inv_id = self.pool.get('account.invoice.line').browse(cr, uid,line).invoice_id.id
                type = inv_obj.browse(cr,uid,inv_id).type
                res[line]={ 'vat': self._get_inv_data(cr, uid, line)[0],
                            'number': self._get_inv_data(cr, uid, line)[1],
                            'control': self._get_inv_data(cr, uid, line)[2],
                            'concept': concept, 
                            'code':dict_rate[concept][4],
                            'subtotal': subtotal, 
                            'perc':dict_rate[concept][2],
                            'wh':wh,
                            'apply':apply,
                            'rate_id':dict_rate[concept][5],
                            'name_rate': dict_rate[concept][6]}
                if not context.get('test_from_wkf',False):
                    self._write_wh_apply(cr,uid,line,res[line],apply,type)
                    inv_obj.write(cr, uid, inv_id, {'status': 'pro'})
        else: # Si no aplica retencion
            for line in wh_dict[concept]['lines']:
                subtotal = self._get_wh_calc(cr,uid,line,dict_rate[concept])[1]
                inv_id = self.pool.get('account.invoice.line').browse(cr, uid,line).invoice_id.id
                type = inv_obj.browse(cr,uid,inv_id).type
                res[line]={ 'vat': self._get_inv_data(cr, uid, line)[0],
                            'number': self._get_inv_data(cr, uid, line)[1],
                            'control': self._get_inv_data(cr, uid, line)[2],
                            'concept': concept, 
                            'code':dict_rate[concept][4],
                            'subtotal': subtotal, 
                            'perc':dict_rate[concept][2],
                            'wh':0.0,
                            'apply':apply,
                            'rate_id':dict_rate[concept][5],
                            'name_rate': dict_rate[concept][6]}
                if not context.get('test_from_wkf',False):
                    self._write_wh_apply(cr,uid,line,res[line],apply,type)
                    inv_obj.write(cr, uid, inv_id, {'status': 'pro'})
        return res


    def _get_wh_apply(self,cr,uid,dict_rate,wh_dict,nature,context=None):
        '''
        Returns a dictionary containing all data for the withholding. Each item is an invoice line.
        '''
        if context is None:
            context={}
        res = {}
        for concept in wh_dict:
            if not wh_dict[concept]['wh']:  #Si nunca se ha aplicado retencion con este concepto.
                if wh_dict[concept]['base'] >= dict_rate[concept][1]: # Si el monto base que suman todas las lineas de la factura es mayor o igual al monto minimo de la tasa.
                    subtract = dict_rate[concept][3]  # Obtengo el sustraendo a aplicar. Existe sustraendo porque es la primera vez.
                    res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, True,context=context))# El True sirve para asignar al campo booleano de la linea de la factura True, para asi marcar de una vez que ya fue retenida, para una posterior busqueda.
                else: # Si el monto base no supera el monto minimo de la tasa(de igual forma se deb declarar asi no supere.)
                    subtract = 0.0
                    res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, False,context=context))
            else: #Si ya se aplico alguna vez la retencion, se aplica rete de una vez, sobre la base sin chequear monto minimo.(Dentro de este periodo)
                if nature:
                    subtract = dict_rate[concept][3]
                    res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, True,context=context))
                else:
                    subtract = 0.0
                    res.update(self._get_wh(cr, uid, subtract,concept, wh_dict, dict_rate, True,context=context))# El True sirve para indicar que la linea si se va a retener.
        return res


    def _get_amount(self,cr,uid,dict):
        '''
        Get the sum of the withholding amount by concept.
        '''
        dict_concept = {}
        for key in dict:
            x = dict[key]['concept']
            y = dict[key]['wh']
            if not dict_concept.get(x,False):
                dict_concept[x] = y
            else:
                dict_concept[x]+= y
        return dict_concept


    def _get_dict_concepts(self,cr,uid,dict):
        '''
        Get a dictionary grouped by concept:  
        {1:[{64: {'control': '', 'perc': 0.050000000000000003, 'concept': 1, 'number': False, 'wh': 0.0, 'code': u'A', 'rate_id': 1, 'apply': True, 'subtotal': 500.0, 'vat': u'J123456789'}}, 
            {65: {'control': '', 'perc': 0.050000000000000003, 'concept': 1, 'number': False, 'wh': 0.0, 'code': u'A', 'rate_id': 1, 'apply': True, 'subtotal': 300.0, 'vat': u'J123456789'}}
           ], 
         2:[{63: {'control': '', 'perc': 0.029999999999999999, 'concept': 2, 'number': False, 'wh': 0.0, 'code': u'002', 'rate_id': 2, 'apply': True, 'subtotal': 1000.0, 'vat': u'J123456789'}}
            ]}
        '''
        dict_concepts = {}
        for key in dict:
            x = dict[key]['concept']
            y = dict[key]
            if not dict_concepts.get(x,False):
                if dict[key]['apply']:
                    dict_concepts[x]=[]
                    dict_concepts[x].append({key:y})
            else:
                if dict[key]['apply']:
                    dict_concepts[x].append({key:y})
        return dict_concepts


    def get_journal(self,cr,uid,inv_brw):
        '''
        Assign the corresponding journal according to each type of withholding (purchase, sale). The journal types are created in retencion_iva
        '''
        tipo='Sale'
        tipo2='islr_sale'
        journal_id = None
        journal_obj = self.pool.get('account.journal')
        if inv_brw.type == 'out_invoice' or inv_brw.type =='out_refund':
            journal_id = journal_obj.search(cr, uid, [('type', '=', 'islr_sale')], limit=1)
        else:
            journal_id = journal_obj.search(cr, uid, [('type', '=', 'islr_purchase')], limit=1)
            tipo = 'Purchase'
            tipo2 = 'islr_purchase'
        if not journal_id:
            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the journal of withholding income for the '%s' has not been created with the type '%s'") % (tipo,tipo2))
        
        return journal_id[0] or None

    def button_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def _create_islr_wh_doc(self,cr,uid,inv_brw,dict):
        '''
        To create in the islr_wh_doc model
        '''
        islr_wh_doc_id=0 
        wh_doc_obj = self.pool.get('islr.wh.doc')
        inv_obj =self.pool.get('account.invoice.line')
        inv_brw = inv_brw.invoice_id
        inv_brw2 = inv_obj.browse(cr,uid,dict.keys())
        islr_wh_doc_id = wh_doc_obj.create(cr,uid,
        {'name': wh_doc_obj.retencion_seq_get(cr, uid),
        'partner_id': inv_brw.partner_id.id,
        'invoice_id': inv_brw.id,
        'period_id': inv_brw.period_id.id,
        'account_id': inv_brw.account_id.id,
        'type': inv_brw.type,
        'journal_id': self.get_journal(cr,uid,inv_brw),
        'islr_wh_doc_id': [(6,0,[i.invoice_id.id for i in inv_brw2])]
        })
        
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'islr.wh.doc', islr_wh_doc_id, 'button_confirm', cr)
#        wf_service.trg_write(uid, 'islr.wh.doc', islr_wh_doc_id, cr)
        return islr_wh_doc_id


    def _create_doc_line(self,cr,uid, inv_brw,key2,islr_wh_doc_id,dictt,dictc):
        '''
        To create in the islr_wh_doc_line model
        '''
        doc_line_obj = self.pool.get('islr.wh.doc.line')
        rate_obj = self.pool.get('islr.rates')
        dict_concept = self._get_amount(cr,uid,dictt)
        inv_line_id = dictc[key2][0].keys()[0]
        rate_id = dictc[key2][0][inv_line_id]['rate_id']

        islr_wh_doc_line_id = doc_line_obj.create(cr,uid,
        {'islr_wh_doc_id':islr_wh_doc_id,
        'concept_id':key2,
        'islr_rates_id':rate_id,
        'invoice_id': inv_brw.invoice_id.id,
        'retencion_islr': rate_obj.browse(cr,uid,rate_id).wh_perc,
        'amount':dict_concept[key2],})

        return islr_wh_doc_line_id

    def _create_doc_invoices(self,cr,uid,key,islr_wh_doc_id):
        '''
        To create in the islr_wh_doc_invoices model
        '''
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        inv_id = key
        islr_wh_doc_invoices_id = doc_inv_obj.create(cr,uid,{'invoice_id':inv_id,'islr_wh_doc_id':islr_wh_doc_id})


    def _write_wh_xml(self,cr,uid,key,islr_wh_doc_line_id):
        '''
        Write in the xml_wh_line model
        '''
        inv_obj =self.pool.get('account.invoice.line')
        xml_obj = self.pool.get('islr.xml.wh.line')
        xml_id = inv_obj.browse(cr,uid,key).wh_xml_id.id
        xml_obj.write(cr, uid, xml_id, {'islr_wh_doc_line_id':islr_wh_doc_line_id})


    def _get_inv_id(self,cr,uid,dict):
        '''
        Get the invoice obj_browse
        '''
        inv_obj =self.pool.get('account.invoice.line')
        line_ids = [key for key in dict if dict[key]['apply']]
        line_ids.sort()
        return line_ids and inv_obj.browse(cr,uid,line_ids[-1]) or False


    def _logic_create(self,cr,uid,dict,wh_doc_id):
        '''
        Handling of all the logic for generating lines on models.
        '''
        dictc = self._get_dict_concepts(cr,uid,dict)
        inv_brw = self._get_inv_id(cr,uid,dict)
        inv_obj =self.pool.get('account.invoice.line')
        islr_wh_doc_id=None

        if inv_brw:
            if dictc and not wh_doc_id:
                islr_wh_doc_id = self._create_islr_wh_doc(cr,uid,inv_brw,dict)
            else:
                islr_wh_doc_id = wh_doc_id
            key_lst = []
            if islr_wh_doc_id:
                for key2 in dictc:
                    inv_line_id = dictc[key2][0].keys()[0]
                    islr_wh_doc_line_id = self._create_doc_line(cr,uid,inv_brw,key2,islr_wh_doc_id,dict,dictc)
                    for line in dictc[key2]:
                        inv_line_id2 = dictc[key2][0].keys()[0]
                        for key in line:
                            key_lst.append(inv_obj.browse(cr,uid,key).invoice_id.id)
                            if not wh_doc_id:
                                self._write_wh_xml(cr,uid,key,islr_wh_doc_line_id)
                for key in set(key_lst):
                    self._create_doc_invoices(cr,uid,key,islr_wh_doc_id)
                        
                self.pool.get('account.invoice').write(cr,uid,inv_brw.invoice_id.id,{'islr_wh_doc_id':islr_wh_doc_id})
                
                message = _("Withholding income voucher '%s' generated.") % self.pool.get('islr.wh.doc').browse(cr,uid,islr_wh_doc_id).name
                self.log(cr, uid, islr_wh_doc_id, message)
            else:
                pass
        else:
            pass
        return islr_wh_doc_id

    def action_ret_islr(self, cr, uid, ids, context={}):
        return self.pool.get('islr.wh.doc').action_ret_islr(cr,uid,ids,context)

    def _check_wh_islr(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        
        wh_apply=[]
        # The two function being called below should undergo overhauling
        # right now it takes an object as and argument instead of an integer
        invoice = self.browse(cr, uid, ids[0], context=context)
        vendor, buyer, wh = self._get_partners(cr, uid, invoice)
        concept_list = self._get_concepts(cr, uid, invoice)
        wh_apply.append(wh)
        wh_apply.append(concept_list)
        
        return invoice, vendor, buyer, concept_list, all(wh_apply)

    def _check_do_wh(self, cr, uid, ids, invoice, vendor, buyer, concept_list, context=None):
        if context is None:
            context={}
        wh_dict = self._get_service_wh(cr, uid, invoice, concept_list)
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)
        dict_rate = self._get_rate_dict(cr, uid, concept_list, residence, nature,context=context)
        self._pop_dict(cr,uid,concept_list,dict_rate,wh_dict)
        dict_completo = self._get_wh_apply(cr,uid,dict_rate,wh_dict,nature,context=context)
        inv_brw = self._get_inv_id(cr,uid,dict_completo)
        
        return bool(inv_brw)
        
    def check_wh_islr_apply(self, cr, uid, ids, context=None):
        '''
        This Method test if given certain conditions it is
        possible to create a new withholding document
        '''
        #TODO: Este metodo deberia devolver true ya que es un metodo "check"
        if context is None:
            context={}
        
        invoice, vendor, buyer, concept_list, wh_apply = self._check_wh_islr(cr, uid, ids, context=context)
        
        do_wh = False
        if wh_apply:
            context.update({'test_from_wkf':True})
            do_wh = self._check_do_wh(cr, uid, ids, invoice, vendor, buyer, concept_list, context=context)
            
        return all([wh_apply,do_wh])

    def check_wh_islr_xml(self, cr, uid, ids, context=None):
        '''
        This Method test if given certain conditions it is
        __not__ possible to create a new withholding document
        but the xml elements needed to create a legal report
        '''
        if context is None:
            context={}
        
        invoice, vendor, buyer, concept_list, wh_apply = self._check_wh_islr(cr, uid, ids, context=context)
        
        do_wh = True
        if wh_apply:
            context.update({'test_from_wkf':True})
            do_wh = self._check_do_wh(cr, uid, ids, invoice, vendor, buyer, concept_list, context=context)
            
        return all([wh_apply,not do_wh])

    def action_islr_xml(self, cr, uid, ids, context=None):
        '''
        This Method creates the xml elements needed to provide a legal report
        '''
        if context is None:
            context={}
        
        invoice, vendor, buyer, concept_list, wh_apply = self._check_wh_islr(cr, uid, ids, context=context)
        
        if wh_apply:
            self._check_do_wh(cr, uid, ids, invoice, vendor, buyer, concept_list, context=context)
            
        return True

    def check_invoice_type(self, cr, uid, ids, context=None):
        '''
        This method test the invoice types to create a new withholding document
        '''
        #TODO: change on workflow
        if context is None:
            context={}
        obj = self.browse(cr, uid, ids[0],context=context)
        if obj.type in ('in_invoice', 'in_refund'):
            return True 
        return False

    def validate_wh_income_done(self, cr, uid, ids, context=None):
        """
        Method that check if wh income is validated in invoice refund.
        @params: ids: list of invoices.
        return: True: the wh income is validated.
                False: the wh income is not validated.
        """
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice', 'out_refund') and not inv.islr_wh_doc_id:
                rislr = True
            else:
                rislr = not inv.islr_wh_doc_id and True or inv.islr_wh_doc_id.state in ('done') and True or False
                if not rislr:
                    raise osv.except_osv(_('Error !'), \
                                     _('The Document you are trying to refund has a income withholding "%s" which is not yet validated!' % inv.islr_wh_doc_id.code ))
                    return False
        return True

account_invoice()









