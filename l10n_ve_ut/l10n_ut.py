# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
from tools import config
from tools.translate import _
import time

class l10n_ut(osv.osv):
    """
    OpenERP Model : l10n_ut
    """
    
    _name = 'l10n.ut'
    _description = __doc__
    
    _columns = {
        'name':fields.char('Law Number Reference', size=64, required=False, readonly=False),
        'date': fields.date('Date'),
        'amount': fields.float('Amount', digits=(16, int(config['price_accuracy'])), help="Amount Bs per UT."),
    }
    _defaults = {
        'name': lambda *a: None,
    }
l10n_ut()
