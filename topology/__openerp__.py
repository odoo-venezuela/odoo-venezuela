# -*- encoding: utf-8 -*-
{
    "name" : "Opening balance Update",
    "version" : "0.2",
    "depends" : ["base"],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
    This module handles the topology according to the sectors of a city
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules/Topology",
    "init_xml" : [    ],
    "demo_xml" : [    ],
    "test": [
    "test/create_topology.yml",
    ],
    "update_xml" : [
                    "data/states_ve_data.xml",
                    "data/city_ve_data.xml",
                    "data/municipality_data.xml",
                    "data/parish_ve_data.xml",
                    "view/municipality_view.xml",
                    "view/city_view.xml",
                    "view/parish_view.xml",
                    "view/zipcode_view.xml",
                    "view/sector_view.xml",
                    "view/state_view.xml",
                    "security/ir.model.access.csv",
                    ],
    "active": False,
    "installable": True,
}
