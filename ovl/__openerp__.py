# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    OVL : Openerp Venezuelan Localization
#    Copyleft (Cl) 2008-2021 Vauxoo, C.A. (<http://vauxoo.com>)
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
{   "name" : "OpenERP Venezuelan Localization",
    "version" : "2.0",
    "depends" : ["l10n_ve_topology",
                 "l10n_ve_imex",
                 "l10n_ve_fiscal_requirements", 
                 "l10n_ve_split_invoice", 
                 "l10n_ve_withholding", 
                 "l10n_ve_withholding_iva" ,
                 "l10n_ve_withholding_muni",
                 "l10n_ve_withholding_src",
                 "l10n_ve_fiscal_reports_V3",
                 #Optionals, uncomment if you want to use them
                 #"l10n_ve_sale_purchase", #Install if you want be able set islr 
                 #concepts from Sales and Purchase
                 #"l10n_ve_fiscal_reports", #First Version, a little less 
                 #automated cool if you have so much manual process
                 #"l10n_ve_fiscal_reports_V2", #Second Version, several bugs 
                 #solved and already audited, will not be mantained
                 #"l10n_ve_topology", # A generic chart of account, 
                 #usefull when you want test or dont use accounting, 
                 #in production enviroments try of audit this accounts 
                 #created with an accountant
                 ],
    "author" : "Vauxoo",
    "description" : """
Install all apps needed to comply with Venezuelan laws
======================================================

This module will install for you:

 - "l10n_ve_topology"

 - "l10n_ve_imex",

 - "l10n_ve_fiscal_requirements", 

 - "l10n_ve_split_invoice", 

 - "l10n_ve_withholding", 

 - "l10n_ve_withholding_iva" ,

 - "l10n_ve_fiscal_reports_V3",

 - "l10n_ve_withholding_muni",

 - "l10n_ve_withholding_src",

 - "l10n_ve_withholding_muni",

Optionals (Not installed by default), uncomment on your/addons/path/ovl/__openerp__.py file this dependencies if you want to use them

 - "l10n_ve_sale_purchase", #Install if you want be able set islr 

Concepts from Sales and Purchase

 - "l10n_ve_fiscal_reports", First Version, a little less Automated cool if you have so much manual process

 - "l10n_ve_fiscal_reports_V2", Second Version, several bugs solved and already audited, will not be mantained it is depreciated

 - "l10n_ve_topology", A generic chart of account, usefull when you want test or dont use accounting, in production enviroments try of audit this accounts created with an accountant
                    """,
    "website" : "http://openerp.org.ve",
    "category" : "Localization/Application",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "test" : [],
    "images" : [],
    "auto_install": False,
    "application": True,
    "installable": True,
}
