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
from osv import osv
from osv import fields
from tools.translate import _

class parish(osv.osv):

    _name ='res.parish'
    _description='Model to manipulate Parish'
    
    _columns = {
        'name':fields.char(size=128, required=True, readonly=False, string="Parish", help="In this field enter the name of the Parish \n"),
        'municipalities_id':fields.many2one('res.municipality','Municipality',required=True, help="In this field enter the name of the municipality which is associated with the parish\n"),
        'sector_ids':fields.one2many('res.sector','parish','Sector',required=True, help="In this field enter the name of sectors associated with the parish"),
    }
    _defaults = {
        'name': lambda *a: None,
    }
parish()
