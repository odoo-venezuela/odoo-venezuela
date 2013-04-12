# -*- encoding: utf-8 -*-
##############################################################################
#    Company: Tecvemar, c.a.
#    Author: Juan Marquez
#    Creation Date: 13/09/2012
#    Version: 0.0.0.1
#
#    Description: This modules handles the l10n ve import declaration
#                 SENIAT Official FORM: Forma 99086  
#
##############################################################################
{
    "name" : "L10n ve - Import/Export",
    "version" : "0.1",
    "depends" : ["base", "account", "decimal_precision"],
    "author" : "Tecvemar - Juan Márquez",
    "description" : "Import/Export SENIAT Forma 99086",
    "website" : "https://code.launchpad.net/~jmarquez/openerp-tecvemar/l10n_ve_imex",
    "category" : "Custom",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'security/ir.model.access.csv',
                    'security/ir_rule.xml',    
                    'view/seniat_form_86_config.xml',         
                    'view/seniat_form_86.xml',         
                    'view/seniat_form_86_menus.xml',         
                    'view/invoice.xml',         
                    'workflow/seniat_form_86.xml',
                    ],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
