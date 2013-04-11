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

from osv import osv
from osv import fields

##---------------------------------------------------------------------------------------- inherited_invoice

class inherited_invoice(osv.osv):

    _inherit = "account.invoice"


    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ _internal methods

    ##------------------------------------------------------------------------------------ function fields

    _columns = {
        'num_import_form_id':fields.many2one('seniat.form.86', 'Import file number', change_default=True, required=False, readonly=True, 
                             states={'draft':[('readonly',False)]}, ondelete='restrict', 
                             domain = [('state','in',('draft','open'))], help="The related form 86 for this import invoice (only draft and open forms)"), 
        }

    ##------------------------------------------------------------------------------------

    ##------------------------------------------------------------------------------------ public methods

    ##------------------------------------------------------------------------------------ buttons (object)

    ##------------------------------------------------------------------------------------ on_change...
    
    def on_change_num_import_form_id(self, cr, uid, ids, num_import_form_id):
        res = {}
        if num_import_form_id:
            imp = self.pool.get('seniat.form.86').browse(cr,uid,num_import_form_id,context=None)
            res = {'value':{'num_import_form':imp.name,'import_invo':imp.date_liq}}
        return res

    ##------------------------------------------------------------------------------------ create write unlink

    ##------------------------------------------------------------------------------------ Workflow

inherited_invoice()

