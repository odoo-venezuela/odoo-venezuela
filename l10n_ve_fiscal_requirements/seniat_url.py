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
import tools
from tools.translate import _
from tools import config

class seniat_url(osv.osv):
    """
    OpenERP Model : seniat_url
    """
    
    _name = 'seniat.url'
    _description = __doc__
    _columns = {
         'name':fields.char('URL Seniat for Partner Information',size=64, required=True, readonly=False,help='In this field enter the URL from Seniat for search the fiscal information from partner'),
        'url_seniat':fields.char('URL Seniat for Retention Rate',size=64, required=True, readonly=False,help='In this field enter the URL from Seniat for search the retention rate from partner'),
    }
seniat_url()
