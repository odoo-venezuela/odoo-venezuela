# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    nhomar.hernandez@netquatro.com
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
from tools import config
from tools.translate import _

class res_partner(osv.osv):
    """
    To calc the condition of the partner. And in future make decisions about ISLR
    """
    
    _inherit = 'res.partner'
    _columns = {
        'situation':fields.selection([
            ('PNR','Persona Natural Residente'),
            ('PNNR','Persona Natural No Residente'),
            ('PJD','Persona Jurídica Domiciliada'),
            ('PJND','Persona Jurídica No Domiciliada'),
            ('PJNCD','Persona Jurídica No Constituida Domiciliada')
        ],'Situation', select=True, readonly=False),
    }
res_partner()
