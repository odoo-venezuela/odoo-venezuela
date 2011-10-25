#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
################################################################################

from osv import fields, osv

'''
List document for link with account entry
'''
def _models_retencion_get(self, cr, uid, context={}):
    obj = self.pool.get('ir.model.fields')
    wh_doc_obj = self.pool.get('account.wh.doc')
    wh_doc_ids = wh_doc_obj.search(cr, uid, [])
    wh_doc_reads = wh_doc_obj.read(cr, uid, wh_doc_ids, ['model_parent'])
    wh_doc_lst = [x['model_parent'] for x in wh_doc_reads]
    ids = obj.search(cr, uid, [('model','in',wh_doc_lst)])
    res = []
    done = {}
    for o in obj.browse(cr, uid, ids, context=context):
        if o.model_id.id not in done:
            res.append( [o.model_id.model, o.model_id.name])
            done[o.model_id.id] = True
    return res


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    
    '''
    Link document with account entry
    '''
    def _document_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        obj = self.pool.get('ir.model.fields')

        wh_doc_obj = self.pool.get('account.wh.doc')
        wh_doc_ids = wh_doc_obj.search(cr, uid, [])
        wh_doc_reads = wh_doc_obj.read(cr, uid, wh_doc_ids, ['model_parent', 'model_child'])
        model_lst = [(x['model_parent'], x['model_child']) for x in wh_doc_reads]
        
        for aml in self.browse(cr, uid, ids, context=context):
            res[aml.id] = ''
            for model in model_lst:
                record = False
                if model[1]:
                    model_ids = obj.search(cr, uid, [('relation','=',model[0]),('model','=',model[1])])
                    model_field = model_ids and obj.browse(cr, uid, model_ids, context=context)[0]
                    model2_ids = obj.search(cr, uid, [('relation','=','account.move'),('model','=',model[1])])
                    model2_field = model2_ids and obj.browse(cr, uid, model2_ids, context=context)[0]
                    if model_field and model2_field:
                        sql ='''                
                                select
                                    l.%s as id
                                from %s l
                                    inner join account_move m on (m.id=l.%s)
                                    inner join account_move_line u on (m.id=u.move_id)
                                where u.id=%s
                            ''' % (model_field.name,model[1].replace('.','_'),model2_field.name,aml.id)
                        
                        cr.execute(sql)
                        record = cr.fetchone()
                else:
                    model_ids = obj.search(cr, uid, [('relation','=','account.move'),('model','=',model[0])])
                    model_field = model_ids and obj.browse(cr, uid, model_ids, context=context)[0]
                    if model_field:                    
                        sql ='''                
                                select
                                    l.id as id
                                from %s l
                                    inner join account_move m on (m.id=l.%s)
                                    inner join account_move_line u on (m.id=u.move_id)
                                where u.id=%s
                            ''' % (model[0].replace('.','_'),model_field.name,aml.id)

                        cr.execute(sql)
                        record = cr.fetchone()                 
                if record:
                    doc_str = "%s,%s" % (model[0],record[0])
                    res[aml.id] = doc_str
                    continue

        return res

    _columns = {
        'res_id': fields.function(_document_get, method=True, string='Document', size=128,
            type='reference', selection=_models_retencion_get),
    }


account_move_line()

