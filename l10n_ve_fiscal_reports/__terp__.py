{
    "name" : "Fiscal Report For Venezuela",
    "version" : "0.1",
    "depends" : ["account","retencion_iva","retencion_municipal","retencion_islr",],
    "author" : "Netquatro",
    "description" : """
    What this module does:
    Build all Fiscal Reports for Law in Venezuela.
    -- Purchase Report.
    -- Sales Report.
    -- Withholding Report.
        Sales, Purchase, ISLR and Munic.
                    """,
    "website" : "http://openerp.netquatro.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "fiscal_report_purchase_view.xml",
        "fiscal_report_sale_view.xml",
        "fiscal_report_whp.xml",
        "fiscal_report_whs.xml",
        "report/fiscal_report_report.xml"
    ],
    "active": False,
    "installable": True,
}
