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
{
    "name" : "Topology for Venezuela",
    "version" : "0.3",
    "depends" : ["base","l10n_ve_fiscal_requirements"],
    "author" : "Vauxoo",
    "description" : """This module handles the topology according to the sectors of a city.

Obtain information and managed all states, municipalities, parishes and sectors of Venezuela with their zip codes and city codes.

Adds new information sectors of the state, municipality, parish and city to which he belongs. 
""",
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules/Localization",
    "init_xml" : [
                    "data/states_ve_data.xml",
                    "data/city_ve_data.xml",
                    "data/municipality_data.xml",
                    "data/parish_ve_data.xml",
        ],
    "demo_xml" : [    ],
    "test": [
    ],
    "update_xml" : [
                    
                    "view/municipality_view.xml",
                    "view/city_view.xml",
                    "view/parish_view.xml",
                    "view/zipcode_view.xml",
                    "view/sector_view.xml",
                    "view/state_view.xml",
                    "security/ir.model.access.csv",
                    "data/zip_code_data.xml"
                    ],
    "active": False,
    "installable": True,
}
