# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan V. Márquez L.
#    Creation Date: 10/04/2012
#    Version: 0.0.0.0
#
#    Description:
#
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields


##---------------------------------------------------------------------------------------- inherited_invoice

class inherited_invoice(osv.osv):

    _inherit = "account.invoice"


    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ _internal methods

    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'customs_form_id':fields.many2one('seniat.form.86', 'Import file number', change_default=True, required=False, readonly=True, 
                             states={'draft':[('readonly',False)]}, ondelete='restrict', 
                             domain = [('state','=',('draft'))], help="The related form 86 for this import invoice (only draft)"), 
        }

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...
    
    def on_change_customs_form_id(self, cr, uid, ids, customs_form_id):
        res = {}
        if customs_form_id:
            imp = self.pool.get('seniat.form.86').browse(cr,uid,customs_form_id,context=None)
            res = {'value':{'num_import_form':imp.name,'import_invo':imp.date_liq}}
        return res

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow
    
    def test_open(self, cr, uid, ids, *args):
        so_brw = self.browse(cr,uid,ids,context={})
        for item in so_brw:
            if item.customs_form_id and item.customs_form_id.state in ('draft','cancel'): 
                raise osv.except_osv(_('Error!'),_('Can\'t validate a invoice while the form 86 state\'s is cancel or draft (%s).\nPlease validate the form 86 first.')%item.customs_form_id.name)
        return super(account_invoice, self).test_open(cr, uid, ids, args)

inherited_invoice()

