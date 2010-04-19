# -*- encoding: utf-8 -*-
class l10n_ut(osv.osv):
    """
    OpenERP Model : l10n_ut
    """
    
    _name = 'openerp.model'
    _description = __doc__
    
    _columns = {
        'name':fields.char('', size=64, required=False, readonly=False),
    }
    _defaults = {
        'name': lambda *a: None,
    }
l10n_ut()
