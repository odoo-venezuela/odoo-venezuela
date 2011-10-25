#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Javier Duran <javier@vauxoo.com>     
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

{
	"name" : "Retenciones Municipales",
	"version" : "0.1",
	"author" : "Vauxoo",
	"category" : "Generic Modules",
	"website": "http://wiki.openerp.org.ve/",
	"description": '''
Administración de las retenciones aplicadas a tributos municipales.
''',
	"depends" : ["base","account","retencion_iva"],
	"init_xml" : [],
	"demo_xml" : [

    ], 
	"update_xml" : [
            "security/ir.model.access.csv",
#            "retention_workflow.xml",
            "retencion_munici_view.xml",
            "retencion_munici_sequence.xml",
            "account_invoice_view.xml",
#            "account_view.xml", 
            "partner_view.xml",
#            "stock_view.xml", 
            "retencion_munici_report.xml",
            "retencion_munici_wizard.xml",
    ],
	"active": False,
	"installable": True
}
