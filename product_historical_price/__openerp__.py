# -*- encoding: utf-8 -*-
{
    "name" : "Product Historical Price",
    "version" : "0.2",
    "depends" : ["product","decimal_precision"],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
    This module gets the historical price of a product
                    """,
    "website" : "http://Vauxoo.com",
    "category" : "Generic Modules/Product",
    "init_xml" : [],
    "update_xml" : ["view/product_view.xml",
                    "data/product_data.xml",
#                    "security/groups.xml",
                    "security/ir.model.access.csv",
                    ],
    "active": False,
    "installable": True,
}
