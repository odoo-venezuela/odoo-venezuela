#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#              Nhomar Hernandez          <nhomar@vauxoo.com>
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

import time
from report import report_sxw
from osv import osv
import pooler

class rep_comprobante(report_sxw.rml_parse):
    #Variables Globales----------------------------------------------------
    ttcompra        = 0
    ttcompra_sdcf   = 0
    ttretencion     = 0
    ttbase          = 0
    ttiva           = 0

    #---------------------------------------------------------------------

    def __init__(self, cr, uid, name, context):
        super(rep_comprobante, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_company_addr': self._get_company_addr,
            'get_partner_addr': self._get_partner_addr,
            'get_partner_addr2': self._get_partner_addr2,
            'get_tipo_doc': self._get_tipo_doc,
            'get_totales': self._get_totales,
            'get_tot_gral_compra': self._get_tot_gral_compra,
            'get_tot_gral_compra_scf': self._get_tot_gral_compra_scf,
            'get_tot_gral_base': self._get_tot_gral_base,
            'get_tot_gral_iva': self._get_tot_gral_iva,
            'get_tot_gral_retencion': self._get_tot_gral_retencion,
            'get_rif': self._get_rif,
            'get_tot_linea': self._get_tot_linea,
            '_get_user': self._get_user
        })

    def _get_user(self):
        
        return self.pool.get('res.users').browse(self.cr, self.uid, self.uid)


    def _get_partner_addr2(self, idp=None):
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        addr_inv={}
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv =(addr.street and ('%s, '%addr.street.title()) or '')    + \
            (addr.zip and ('Codigo Postal: %s, '%addr.zip) or '')        +\
            (addr.state_id and ('%s, '%addr.state_id.name.title()) or '')+ \
            (addr.city and ('%s, '%addr.city.title()) or '')+ \
            (addr.country_id and ('%s '%addr.country_id.name.title()) or '')
            #~ addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv 

    def _get_tipo_doc(self, tipo=None):
        if not tipo:
            return []

        types = {'out_invoice': '1', 'in_invoice': '1', 'out_refund': '2', 'in_refund': '2'}

        return types[tipo]



    def _get_totales(self, comp_id):        
        if not comp_id:
            return []

        types = {'out_invoice': 's', 'in_invoice': 's', 'out_refund': 'r', 'in_refund': 'r'}
        tot_comp = {}
        tot_comp_sdc = {}
        tot_base_imp = {}
        tot_imp_iva = {}
        tot_iva_ret = {}

        comp_obj = self.pool.get('account.wh.iva')
        comp = comp_obj.browse(self.cr,self.uid, comp_id)
        res = {}
        ttal = {}
        lst_comp = []

        dic_inv = {}
        for rl in comp.wh_lines:
            lst_tmp = []
            k=1
            no_fac_afe = rl.invoice_id.origin or ''
            if rl.invoice_id.type in ['in_refund', 'out_refund']:
                k=-1
                no_fac_afe = rl.invoice_id.parent_id and rl.invoice_id.parent_id.reference or ''

            #~ Codigo para cumplir los cambios en el nuevo uso del campo ret, 
            #~ y la relacion nueva en account.invoice.tax
            
            for txl in rl.invoice_id.tax_line:
                #~ Aqui se esta revisando son los impuestos que estan
                #~ en la factura solo con el fin de poder obtener
                #~ solo los impuestos que no son objeto de retencion

                a= (txl.name and txl.name.find('SDCF')!=-1)
                b= (txl.tax_id and not txl.tax_id.ret)
                if not any([a,b]):
                    continue
                
                sdcf = False
                tot_base_imp[types[rl.invoice_id.type]] = tot_base_imp.get(types[rl.invoice_id.type],0.0) + txl.base
                tot_imp_iva[types[rl.invoice_id.type]] = tot_imp_iva.get(types[rl.invoice_id.type],0.0) + txl.amount
                tot_iva_ret[types[rl.invoice_id.type]] = tot_iva_ret.get(types[rl.invoice_id.type],0.0) + txl.amount_ret

                if any([a,b]):
                    tot_comp_sdc[types[rl.invoice_id.type]] = tot_comp_sdc.get(types[rl.invoice_id.type],0.0) + (txl.base+txl.amount)
                    sdcf = True
                else:
                    tot_comp[types[rl.invoice_id.type]] = tot_comp.get(types[rl.invoice_id.type],0.0) + (txl.base+txl.amount)

                d1 = {
                    'fecha': rl.invoice_id.date_invoice,
                    'nro_fact': rl.invoice_id.reference,
                    'nro': rl.invoice_id.number,
                    'nro_ctrl': rl.invoice_id.nro_ctrl,
                    'nro_ncre': rl.invoice_id.reference,
                    'nro_ndeb': rl.invoice_id.reference,
                    'porcenta': rl.invoice_id.wh_iva_rate,
                    'tip_tran': self._get_tipo_doc(rl.invoice_id.type),
                    'nro_fafe': no_fac_afe,
                    'tot_civa': not sdcf and k*(txl.base+txl.amount) or 0.0,
                    'cmp_sdcr': sdcf and k*(txl.base+txl.amount) or 0.0,
                    'bas_impo': k*txl.base,
                    'alic': txl.tax_id.amount and txl.tax_id.amount * 100.0 or 0.0,
                    'iva': k*txl.amount,
                    'iva_ret': k*txl.amount_ret,
                    'inv_type': rl.invoice_id.type
                }
                lst_tmp.append(d1)
                dic_inv[rl.invoice_id.id] = lst_tmp
            
            for txl in rl.tax_line:
                a= (txl.name and txl.name.find('SDCF')!=-1)
                b= (txl.tax_id and not txl.tax_id.ret)
                if any([a,b]):
                    continue
                sdcf = False
                tot_base_imp[types[rl.invoice_id.type]] = tot_base_imp.get(types[rl.invoice_id.type],0.0) + txl.base
                tot_imp_iva[types[rl.invoice_id.type]] = tot_imp_iva.get(types[rl.invoice_id.type],0.0) + txl.amount
                tot_iva_ret[types[rl.invoice_id.type]] = tot_iva_ret.get(types[rl.invoice_id.type],0.0) + txl.amount_ret
                
                #~ TODO: ESTO SE DEBE SOLUCIONAR, MEDIANTE EL USO DEL CAMPO RET 
                #~ EN EL MODELO ACCOUNT.TAX, DE TAL MANERA QUE SI EL IMPUESTO APARECE
                #~ CON EL VALOR EN FALSE, Y DADO QUE AHORA CONTAMOS CON UN TAX_ID EN ACCOUNT.INVOICE.TAX
                #~ PODEMOS HACER EL RASTREO HASTA EL ACCOUNT.TAX
                if txl.name.find('SDCF')!=-1:
                    tot_comp_sdc[types[rl.invoice_id.type]] = tot_comp_sdc.get(types[rl.invoice_id.type],0.0) + (txl.base+txl.amount)
                    sdcf = True
                else:
                    tot_comp[types[rl.invoice_id.type]] = tot_comp.get(types[rl.invoice_id.type],0.0) + (txl.base+txl.amount)

                d1 = {
                    'fecha': rl.invoice_id.date_invoice,
                    'nro_fact': rl.invoice_id.reference,
                    'nro': rl.invoice_id.number,
                    'nro_ctrl': rl.invoice_id.nro_ctrl,
                    'nro_ncre': rl.invoice_id.reference,
                    'nro_ndeb': rl.invoice_id.reference,
                    'porcenta': rl.invoice_id.wh_iva_rate,
                    'tip_tran': self._get_tipo_doc(rl.invoice_id.type),
                    'nro_fafe': no_fac_afe,
                    'tot_civa': not sdcf and k*(txl.base+txl.amount) or 0.0,
                    'cmp_sdcr': sdcf and k*(txl.base+txl.amount) or 0.0,
                    'bas_impo': k*txl.base,
                    'alic': txl.tax_id.amount and txl.tax_id.amount * 100.0 or 0.0,
                    'iva': k*txl.amount,
                    'iva_ret': k*txl.amount_ret,
                    'inv_type': rl.invoice_id.type
                }
                lst_tmp.append(d1)
                dic_inv[rl.invoice_id.id] = lst_tmp
        
        
        for inv_id in dic_inv.keys():
            i=0
            cf = False
            acum = dic_inv[inv_id][:]
            for inv_tax in dic_inv[inv_id]:
                if inv_tax['cmp_sdcr']:
                    cf = True
                    break
                i+=1
            if cf:
                acum.pop(i)
                if acum:
                    acum[0]['cmp_sdcr'] = dic_inv[inv_id][i]['cmp_sdcr']
                    acum[0]['tot_civa'] += dic_inv[inv_id][i]['cmp_sdcr']
            
            dic_inv[inv_id] = acum
                
        for inv_id in dic_inv.keys():
            lst_comp+=dic_inv[inv_id]
                  
        self.ttcompra = tot_comp.get('s',0.0) - tot_comp.get('r',0.0)
        self.ttcompra_sdcf = tot_comp_sdc.get('s',0.0) - tot_comp_sdc.get('r',0.0)
        self.ttbase = tot_base_imp.get('s',0.0) - tot_base_imp.get('r',0.0)
        self.ttiva = tot_imp_iva.get('s',0.0) - tot_imp_iva.get('r',0.0)
        self.ttretencion = tot_iva_ret.get('s',0.0) - tot_iva_ret.get('r',0.0)
        return lst_comp

    def _get_tot_gral_compra(self): 
        return self.ttcompra

    def _get_tot_gral_compra_scf(self): 
        return self.ttcompra_sdcf

    def _get_tot_gral_base(self): 
        return self.ttbase 
        
    def _get_tot_gral_iva(self): 
        return self.ttiva

    def _get_tot_gral_retencion(self): 
        return self.ttretencion 

    def _get_rif(self, vat=''):
        if not vat:
            return []
        return vat[2:].replace(' ', '')

    def _get_tot_linea(self, base, iva): 
        return base + iva


report_sxw.report_sxw(
    'report.account.wh.iva',
    'account.wh.iva',
    'addons/l10n_ve_withholding_iva/report/withholding_vat_report.rml',
    parser=rep_comprobante,
    header=False
)      
