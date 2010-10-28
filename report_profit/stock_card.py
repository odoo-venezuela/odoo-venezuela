# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv
from tools.sql import drop_view_if_exists
import time
import datetime
from mx.DateTime import *
from tools import config



class stock_card(osv.osv):        
    _name = "stock.card"
    _description = "Move by Picking Line"
    _columns = {
        'name': fields.char('Name', size=64, select=True),
        'sc_line': fields.one2many('stock.card.line', 'stock_card_id', 'Stock Lines', readonly=True),        
    }


    def find_return(self, cr, uid, ids, *args):        
        cr.execute("SELECT scl.id FROM stock_card_line scl " \
                    "INNER JOIN stock_picking sp on sp.id=scl.picking_id " \
                    "WHERE sp.name ILIKE '%return%' ORDER BY scl.name")
                    
        res = [x[0] for x in cr.fetchall()]
        return res

    def find_parent(self, cr, uid, ids):
        sc_line_obj = self.pool.get('stock.card.line')
        sp_obj = self.pool.get('stock.picking')
        scl_ids = self.find_return(cr, uid, ids)
        print 'devoluciones: ',scl_ids
        for scl in sc_line_obj.browse(cr,uid,scl_ids):
            nb =scl.picking_id.name[:scl.picking_id.name.lower().find('return')-1].strip()
            print 'a buscar: ',nb
            sp_ids = sp_obj.search(cr, uid, [('name','=',nb)])
            print 'posible picking padre: ',sp_ids
            if sp_ids:
                scl_ids = sc_line_obj.search(cr, uid, [('picking_id','=',sp_ids[0]),('product_id','=',scl.product_id.id)])
                print 'linea padre: ',scl_ids
                if scl_ids:
                    sc_line_obj.write(cr,uid,[scl.id],{'parent_id':scl_ids[0]})

        return True    

    def action_confirm(self, cr, uid, ids, context={}):
        drop_view_if_exists(cr, 'report_profit_picking')
        cr.execute("""
            create or replace view report_profit_picking as (
            select
                sm.id as id,                
                to_char(sm.date_planned, 'YYYY-MM-DD:HH24:MI:SS') as name,
                sm.picking_id as picking_id,
                sp.type as type,                
                sm.purchase_line_id as purchase_line_id,
                sm.sale_line_id as sale_line_id,
                sm.product_id as product_id,
                sm.location_id as location_id,
                sm.location_dest_id as location_dest_id,                
                sm.id as stk_mov_id,
                sm.product_qty as picking_qty,
                sm.state as state
            from stock_picking sp
                right join stock_move sm on (sp.id=sm.picking_id)
                left join product_template pt on (pt.id=sm.product_id)
            where sm.state='done' and pt.type!='service'
            order by name
            )
        """)        
        rpp_obj = self.pool.get('report.profit.picking')
        sc_line_obj = self.pool.get('stock.card.line')
        rpp_ids = rpp_obj.search(cr, uid, [])
        for rpp in rpp_obj.browse(cr,uid,rpp_ids):
            vals = {}
            vals = {
            'stock_card_id': ids[0],            
            'name': rpp.name or False,
            'picking_id':rpp.picking_id and rpp.picking_id.id or False,
            'purchase_line_id':rpp.purchase_line_id and rpp.purchase_line_id.id or False,
            'sale_line_id': rpp.sale_line_id and rpp.sale_line_id.id or False,
            'product_id':rpp.product_id and rpp.product_id.id or False,
            'location_id':rpp.location_id and rpp.location_id.id or False,
            'location_dest_id':rpp.location_dest_id and rpp.location_dest_id.id or False,
            'stk_mov_id':rpp.stk_mov_id and rpp.stk_mov_id.id or False,
            'picking_qty':rpp.picking_qty or 0.0,
            'type':rpp.type or False,
            'state': rpp.state or False,
            'aml_cost_id': rpp.aml_cost_id and rpp.aml_cost_id.id or False,
            'invoice_line_id':rpp.invoice_line_id and rpp.invoice_line_id.id or False,
            'invoice_qty':rpp.invoice_qty or 0.0,
            'aml_cost_qty':rpp.aml_cost_qty or 0.0,
            'invoice_price_unit':rpp.invoice_price_unit or 0.0,
            'aml_cost_price_unit':rpp.aml_cost_price_unit or 0.0,
            'invoice_id':rpp.invoice_id and rpp.invoice_id.id or False,
            'stock_before': rpp.stock_before or 0.0,
            'stock_after': rpp.stock_after or False,
            'date_inv':rpp.date_inv or False,
            'stock_invoice':rpp.stock_invoice or 0.0,
            
            }
            sc_line_obj.create(cr,uid,vals)

        self.find_parent(cr, uid, ids)
        return True


    def action_unico(self, cr, uid, ids, *args):
        cr.execute('SELECT DISTINCT product_id FROM report_profit_picking')            
        res = [x[0] for x in cr.fetchall()]
        return res

    def action_sm_x_pd(self, cr, uid, ids, prd_id):        
        cr.execute('SELECT id FROM report_profit_picking ' \
                    'WHERE product_id=%s ORDER BY name', (prd_id,))
                    
        res = [x[0] for x in cr.fetchall()]
        return res

    def compute_compra(self, cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des):
        print 'q mov: ',q_mov
        print 'qda antes: ',q_des
        print 'subtotal antes: ',subtot
        print 'total antes: ',tot
        print 'avg antes: ',prom
        q_des+=q_mov                        
        print 'realizando calculo compra:'        
        subtot = scl_obj.invoice_price_unit*q_mov
        tot += subtot
        if q_des > 0:
            prom = tot/q_des
        else:
            prom = 0
        
        print 'subtotal despues: ',subtot
        print 'total despues: ',tot
        print 'avg despues: ',prom      
        print 'qda despues:',q_des
        res = (q_des,subtot,tot,prom)
        return res
    
    def compute_nc_vta(self, cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des):
        print 'q mov: ',q_mov
        print 'qda antes: ',q_des
        print 'subtotal antes: ',subtot
        print 'total antes: ',tot
        print 'avg antes: ',prom
        if scl_obj.parent_id and scl_obj.parent_id.avg:
            prom_pad = scl_obj.parent_id.avg
        else:
            print 'PADRE SIN PRECIO PROMEDIOOOOOO'
            prom_pad = 0.0
        
        
        print 'precio avg del padre:',prom_pad
        q_des+=q_mov
        print 'realizando calculo nc venta:'        
        subtot = prom_pad*q_mov
        tot += subtot
        if q_des > 0:
            prom = tot/q_des
        else:
            prom = 0
        
        print 'subtotal despues: ',subtot
        print 'total despues: ',tot
        print 'avg despues: ',prom      
        print 'qda despues:',q_des
        res = (q_des,subtot,tot,prom)
        return res

    def validate_nc_vta(self, cr, uid, ids, scl_obj,q_mov,subtot,tot,prom,q_des,no_cp,lst_org,act_sml_id,s_ord):        
        if scl_obj.parent_id:
            print 'validando padre NC VENTA: ',scl_obj.parent_id        
            if scl_obj.parent_id.id in lst_org or scl_obj.parent_id.id in no_cp:
                no_cp.append(act_sml_id)
            else:
                print 'procesoooo NC VTA padre procesado:'
                q_des,subtot,tot,prom = self.compute_nc_vta(cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des)
                #REALIZAR EL WRITE DE LA LINEA
                value = {
                    'subtotal':subtot,
                    'total':tot,
                    'avg':prom,
                    'stock_before':q_mov,
                    'stock_after':q_des
                }            
                s_ord=self.write_data(cr, uid, ids, scl_obj.id, value,s_ord)                                    
        else:                               
            print 'procesoooo NC VTA:'
            q_des,subtot,tot,prom = self.compute_nc_vta(cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des)
            #REALIZAR EL WRITE DE LA LINEA 
            value = {
                'subtotal':subtot,
                'total':tot,
                'avg':prom,
                'stock_before':q_mov,
                'stock_after':q_des
            }            
            s_ord=self.write_data(cr, uid, ids, scl_obj.id, value,s_ord)                    

        res = (q_des,subtot,tot,prom,no_cp,s_ord)

        return res
    
    def compute_venta(self, cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des):
        print 'q mov: ',q_mov
        print 'qda antes: ',q_des
        print 'subtotal antes: ',subtot
        print 'total antes: ',tot
        print 'avg antes: ',prom
        q_des-=q_mov                        
        print 'realizando calculo venta:'        
        subtot = prom*q_mov
        tot -= subtot
#        if q_des > 0:
#            prom = tot/q_des
#        else:
#            prom = 0
        
        print 'subtotal despues: ',subtot
        print 'total despues: ',tot
        print 'avg despues: ',prom      
        print 'qda despues:',q_des
        res = (q_des,subtot,tot,prom)
        return res

    def validate_venta(self, cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des,no_cp,lst_org,act_sml_id,s_ord):
        if not no_cp and q_des >= q_mov:
            print 'procesooo venta:'
            q_des,subtot,tot,prom = self.compute_venta(cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des)
            #REALIZAR EL WRITE DE LA LINEA
            value = {
                'subtotal':subtot,
                'total':tot,
                'avg':prom,
                'stock_before':q_mov,
                'stock_after':q_des
            }            
            s_ord=self.write_data(cr, uid, ids, scl_obj.id, value,s_ord)            
        else:
            print 'no procesoooo vta:'
            no_cp.append(act_sml_id)

        res = (q_des,subtot,tot,prom,no_cp,s_ord)
        
        return res


    def compute_nc_compra(self, cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des):        
        print 'q mov: ',q_mov
        print 'qda antes: ',q_des
        print 'subtotal antes: ',subtot
        print 'total antes: ',tot
        print 'avg antes: ',prom        
        if scl_obj.parent_id and scl_obj.parent_id.invoice_price_unit:
            cost_pad = scl_obj.parent_id.invoice_price_unit
        else:
            print 'PADRE SIN PRECIO UNITARIOOOO'
            cost_pad = 0.0
            
        
        print 'precio unitario del padre:',cost_pad
        
        q_des-=q_mov  
        print 'realizando calculo nc compra:'        
        subtot = cost_pad*q_mov
        tot -= subtot
        if q_des > 0:
            prom = tot/q_des
        else:
            prom = 0
        
        print 'subtotal despues: ',subtot
        print 'total despues: ',tot
        print 'avg despues: ',prom      
        print 'qda despues:',q_des
        res = (q_des,subtot,tot,prom)
        return res


    def validate_nc_compra(self,cr,uid, ids,scl_obj,q_mov,subtot,tot,prom,q_des,no_cp,lst_org,act_sml_id,s_ord):        
        if not no_cp and q_des >= q_mov:                           
            if scl_obj.parent_id:
                print 'validando padre NC compra: ',scl_obj.parent_id
                if scl_obj.parent_id.id in lst_org or scl_obj.parent_id.id in no_cp:
                    no_cp.append(act_sml_id)
                else:
                    print 'procesoooo NC COMPRA padre procesado:'
                    q_des,subtot,tot,prom = self.compute_nc_compra(cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des)
                    #REALIZAR EL WRITE DE LA LINEA
                    value = {
                        'subtotal':subtot,
                        'total':tot,
                        'avg':prom,
                        'stock_before':q_mov,
                        'stock_after':q_des
                    }            
                    s_ord=self.write_data(cr, uid, ids, scl_obj.id, value,s_ord)                    
            else:
                print 'procesoooo  NC COMPRA:'
                q_des,subtot,tot,prom = self.compute_nc_compra(cr, uid, ids, scl_obj, q_mov,subtot,tot,prom,q_des)
                #REALIZAR EL WRITE DE LA LINEA
                value = {
                    'subtotal':subtot,
                    'total':tot,
                    'avg':prom,
                    'stock_before':q_mov,
                    'stock_after':q_des
                }            
                s_ord=self.write_data(cr, uid, ids, scl_obj.id, value,s_ord)                
        else:
            print 'no procesoooo NC COMPRA:'
            no_cp.append(act_sml_id)

        res = (q_des,subtot,tot,prom,no_cp,s_ord)
        return res

    def write_data(self, cr, uid, ids, scl_id, vals, seq):
        sc_line_obj = self.pool.get('stock.card.line')        
        seq += 1
        vals.update({'sequence':seq})
        sc_line_obj.write(cr, uid, scl_id, vals)
        return seq

    def action_done(self, cr, uid, ids, context={}):
        sc_line_obj = self.pool.get('stock.card.line')
        rpp_obj = self.pool.get('report.profit.picking')
        prod_unic = self.action_unico(cr, uid, ids)
        loc_ids = 11
        for prod_id in prod_unic:
            def_code = self.pool.get('product.product').browse(cr,uid,prod_id).default_code.strip()
            print 'def_code: ',def_code
            sml_x_pd_id = []
            sml_x_pd_id = self.action_sm_x_pd(cr, uid, ids,prod_id)
            cont = False
            no_cump = []
            seq = 0
            while sml_x_pd_id:
                print 'movimientos: ',sml_x_pd_id
                sml_id = sml_x_pd_id.pop(0)
                if not cont:
                    cont = True
                    avg = 0.0
                    q = 0.0
                    total = 0.0
                    subtotal = 0.0
                    qda = 0.0
                    #se debe buscar el costo inicial
                    cr.execute('SELECT standard_price,product_qty FROM lst_cost ' \
                    'WHERE default_code=%s', (def_code,))
                    res = cr.fetchall()
                    if res:
                        avg,q = res[0]
                    else:
                        rpp = rpp_obj.browse(cr,uid,sml_id)
                        if rpp.location_dest_id.id == loc_ids and rpp.invoice_id.type == 'in_invoice':
                            q = rpp.picking_qty
                            avg = rpp.invoice_price_unit
                        else:
                            no_cump.append(sml_id)
                            continue
                    #avg = 1430.96
                    #q = 5.0
                    total = avg*q
                    subtotal = avg*q
                    qda = q
                    seq += 1
                    value = {
                        'subtotal':subtotal,
                        'total':total,
                        'avg':avg,
                        'stock_before':q,
                        'stock_after':qda,
                        'sequence':seq
                    }
                    scl_id = sc_line_obj.search(cr, uid, [('stk_mov_id','=',sml_id)])
                    sc_line_obj.write(cr, uid, scl_id, value)                    
                    print 'q inicial: ',q
                    print 'avg: ',avg
                    print 'qda inicial: ',qda
                    
                    
                else:
                    rpp = rpp_obj.browse(cr,uid,sml_id)
                    q = rpp.picking_qty
                    scl_id = sc_line_obj.search(cr, uid, [('stk_mov_id','=',sml_id)])
                    scl = sc_line_obj.browse(cr,uid,scl_id)[0]                    
                    print 'viene operac: ',sml_id
                    print 'packing: ',rpp.picking_id.name
                    #VENTA
                    if rpp.location_id.id == loc_ids and rpp.invoice_id.type == 'out_invoice':
                        print 'validando VENTA:'        
                        qda,subtotal,total,avg,no_cump,seq= \
                        self.validate_venta(cr, uid, ids,scl,q,subtotal,total,avg,qda,no_cump,sml_x_pd_id,sml_id,seq)
                    #NC COMPRA
                    if rpp.location_id.id == loc_ids and (rpp.invoice_id.type == 'in_refund' or rpp.invoice_id.type == 'in_invoice'):
                        print 'validando NC compra:'        
                        qda,subtotal,total,avg,no_cump,seq= \
                        self.validate_nc_compra(cr,uid,ids,scl,q,subtotal,total,avg,qda,no_cump,sml_x_pd_id,sml_id,seq)
                    #COMPRA
                    if rpp.location_dest_id.id == loc_ids and rpp.invoice_id.type == 'in_invoice':
                        print 'procesooo compra:'        
                        qda,subtotal,total,avg = self.compute_compra(cr, uid, ids,scl,q,subtotal,total,avg,qda)
                        #REALIZAR EL WRITE DE LA LINEA
                        value = {
                            'subtotal':subtotal,
                            'total':total,
                            'avg':avg,
                            'stock_before':q,
                            'stock_after':qda
                        }            
                        seq=self.write_data(cr, uid, ids, scl.id, value, seq)                        
                        if no_cump:
                            print 'agregando nuevamente las vta:'
                            #no_cump.append(sml_id)
                            no_cump.extend(sml_x_pd_id)
                            print 'no cumplioooo: ',no_cump
                            sml_x_pd_id = no_cump
                            print 'nueva listaaa: ',sml_x_pd_id
                            no_cump = []   
                    #NC VENTA
                    if rpp.location_dest_id.id == loc_ids and rpp.invoice_id.type == 'out_refund':
                        print 'validando NC VENTA:'        
                        qda,subtotal,total,avg,no_cump,seq= \
                        self.validate_nc_vta(cr, uid, ids,scl,q,subtotal,total,avg,qda,no_cump,sml_x_pd_id,sml_id,seq)
                            
                        if no_cump and not scl.parent_id:
                            print 'agregando nuevamente los movimientos:'
                            #no_cump.append(sml_id)
                            no_cump.extend(sml_x_pd_id)
                            print 'no cumplioooo: ',no_cump
                            sml_x_pd_id = no_cump
                            print 'nueva listaaa: ',sml_x_pd_id
                            no_cump = []                            
                                                     

                    #NO HAY MAS COMPRAS O NC VENTAS Y QUEDAN MOVIMIENTOS
                    if no_cump and not sml_x_pd_id:
                        while no_cump:
                            sml_id = no_cump.pop(0)
                            print 'procesando vtas y la NC COMPRAS faltantes:'


#        self.action_move_create(cr, uid, ids)
#        self.write(cr, uid, ids, {'state':'done'})
        return True
    
#    def action_move_create(self, cr, uid, ids, *args):
#        inv_obj = self.pool.get('account.invoice')
#        context = {}

#        for ret in self.browse(cr, uid, ids):

#            acc_id = ret.account_id.id
#            if not ret.date_ret:
#                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})

#            period_id = ret.period_id and ret.period_id.id or False
#            journal_id = ret.journal_id.id
#            if not period_id:
#                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
#                if len(period_ids):
#                    period_id = period_ids[0]
#                else:
#                    raise osv.except_osv(_('Warning !'), _("No se encontro un periodo fiscal para esta fecha: '%s' por favor verificar.!") % (ret.date_ret or time.strftime('%Y-%m-%d')))

#            if ret.islr_line_ids:
#                for line in ret.islr_line_ids:
#                    writeoff_account_id = False
#                    writeoff_journal_id = False
#                    amount = line.amount
#                    ret_move = self.ret_and_reconcile(cr, uid, [ret.id], [line.invoice_id.id],
#                            amount, acc_id, period_id, journal_id, writeoff_account_id,
#                            period_id, writeoff_journal_id, context)

#                    # make the retencion line point to that move
#                    rl = {
#                        'move_id': ret_move['move_id'],
#                    }
#                    lines = [(1, line.id, rl)]
#                    self.write(cr, uid, [ret.id], {'islr_line_ids':lines, 'period_id':period_id})
##                    inv_obj.write(cr, uid, line.invoice_id.id, {'retention':True}, context=context)
#    

#        return True    

stock_card()








class stock_card_line(osv.osv):        
    _name = "stock.card.line"
    _description = "Move by Picking Line"
    _columns = {
        'stock_card_id':fields.many2one('stock.card', 'Stock card', readonly=True, select=True),
        'name': fields.char('Date', size=20, readonly=True, select=True),
        'picking_id':fields.many2one('stock.picking', 'Picking', readonly=True, select=True),
        'purchase_line_id': fields.many2one('purchase.order.line', 'Purchase Line', readonly=True, select=True),
        'sale_line_id': fields.many2one('sale.order.line', 'Sale Line', readonly=True, select=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True, select=True),
        'location_id':fields.many2one('stock.location', 'Source Location', readonly=True, select=True),
        'location_dest_id':fields.many2one('stock.location', 'Dest. Location', readonly=True, select=True),                
        'stk_mov_id':fields.many2one('stock.move', 'Picking line', readonly=True, select=True),
        'picking_qty': fields.float('Picking quantity', digits=(16, int(config['price_accuracy'])), readonly=True),        
        'type': fields.selection([
            ('out', 'Sending Goods'),
            ('in', 'Getting Goods'),
            ('internal', 'Internal'),
            ('delivery', 'Delivery')
            ],'Type', readonly=True, select=True),        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ],'Status', readonly=True, select=True),
        'aml_cost_id': fields.many2one('account.move.line', string='Cost entry', readonly=True, select=True),
        'invoice_line_id': fields.many2one('account.invoice.line', string='Invoice line', readonly=True, select=True),
        'invoice_qty': fields.float(string='Invoice quantity', digits=(16, int(config['price_accuracy'])), readonly=True),
        'aml_cost_qty': fields.float(string='Cost entry quantity', digits=(16, int(config['price_accuracy'])), readonly=True),
        'invoice_price_unit': fields.float(string='Invoice price unit', digits=(16, int(config['price_accuracy'])), readonly=True),
        'aml_cost_price_unit': fields.float(string='Cost entry price unit', digits=(16, int(config['price_accuracy'])), readonly=True), 
        'invoice_id': fields.many2one('account.invoice', string='Invoice', readonly=True, select=True),
        'stock_before': fields.float(string='Stock before', digits=(16, int(config['price_accuracy'])), readonly=True),
        'stock_after': fields.float(string='Stock after', digits=(16, int(config['price_accuracy'])), readonly=True),
        'date_inv': fields.char(string='Date invoice', size=20, readonly=True, select=True),
        'stock_invoice': fields.float(string='Stock invoice', digits=(16, int(config['price_accuracy'])), readonly=True),
        'subtotal': fields.float(string='Subtotal', digits=(16, int(config['price_accuracy'])), readonly=True),
        'total': fields.float(string='Total', digits=(16, int(config['price_accuracy'])), readonly=True),
        'avg': fields.float(string='Price Avg', digits=(16, int(config['price_accuracy'])), readonly=True),
        'parent_id':fields.many2one('stock.card.line', 'Parent', readonly=True, select=True),
        'sequence': fields.integer('Sequence', readonly=True),
        
    }



stock_card_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

