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

from osv import fields, osv
from openerp.tools.translate import _

class islr_wh_change_concept(osv.osv_memory):

    _name = 'islr.wh.change.concept'
    _columns = {
        'sure': fields.boolean('Are you Sure?'),
        'new_concept_id': fields.many2one('islr.wh.concept', 'New Income Wh Concept', required=True),
    }

    def income_wh_change(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        iwcc_brw = self.browse(cr, uid, ids[0], context=context)
        if not iwcc_brw.sure:
            raise osv.except_osv(_('Warning!'), _('You have to tick the "Are you Sure" Check'))
        ail_obj = self.pool.get('account.invoice.line')
        ail_brw = ail_obj.browse(cr, uid, context.get('active_id'), context={})
        ail_brw.write({'concept_id': iwcc_brw.new_concept_id.id})
        if ail_brw.invoice_id.islr_wh_doc_id:
            if ail_brw.invoice_id.islr_wh_doc_id.state=='draft':
                ail_brw.invoice_id.islr_wh_doc_id.compute_amount_wh()
            else:
                raise osv.except_osv(_('Warning!'), _('Income Withholding from this invoice must be cancelled prior to change concept'))

        return {'type': 'ir.actions.act_window_close'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
