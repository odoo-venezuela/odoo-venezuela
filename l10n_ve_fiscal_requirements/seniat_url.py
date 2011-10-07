#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Miguel Delgado           <miguel@openerp.com.ve>
#############################################################################
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
##############################################################################

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
         'url_seniat1_company':fields.char('URL Seniat for Partner Information',size=64, required=True, readonly=False,help='In this field enter the URL from Seniat for search the fiscal information from partner'),
        'url_seniat2_company':fields.char('URL Seniat for Retention Rate',size=64, required=True, readonly=False,help='In this field enter the URL from Seniat for search the retention rate from partner'),
    }
    _defaults = {
        'url_seniat1_company':'http://contribuyente.seniat.gob.ve/getContribuyente/getrif?rif=',
        'url_seniat2_company':'http://contribuyente.seniat.gob.ve/BuscaRif/BuscaRif.jsp?p_rif=',
    }
seniat_url()
