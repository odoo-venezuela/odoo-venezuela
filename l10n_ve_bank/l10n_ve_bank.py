# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
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
#
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
import time

class res_partner_bank_checkbook(osv.osv):
    """
    OpenERP Model : res.partner.bank.checkbook
    """
    
    _name = 'res.partner.bank.checkbook'
    _description = 'Control for checkbooks'
    
    _columns = {
        'name':fields.char('Serial', size=64, required=True, readonly=False),
        'date': fields.date('Printed date'),
        'account_id':fields.many2one('res.partner.bank', 'Bank Account', required=False),
        'check_ids':fields.one2many('res.partner.bank.check', 'checkbook_id', 'Label', required=False),
    }

res_partner_bank_checkbook()

class res_partner_bank_check(osv.osv):
    """
    OpenERP Model : res_partner_bank_check
    """
    
    _name = 'res.partner.bank.check'
    _description = 'Control for Checks'
    
    _columns = {
        'name':fields.char('Number', size=64, required=True, readonly=False),
        'checkbook_id':fields.many2one('openerp.model', 'Label', required=False),
    }
res_partner_bank_check()
