
{
  'name' : "Sales Commissions Report",
  'version' : '1.0',
  'description' : """Sales Commissions Report
  Show the commissions based on the payments made by a particular salesman throughout the span of a specific period
  TODO:
  - Allow preparing the commisions to be paid (or been paid) to a particular salesman during certain period:
        * Ordered by Payments Number,
            + Show a Tree View
            + Allow to print a report
        * Grouped by Salesman,
            + Show a Tree View
            + Allow to print a report
  - Allow pay those commissions and make the regarding entries to the intended journal
  """,
  'update_xml' : ['salesman_commission_view.xml',],
  'init_xml' : [],
  'demo_xml' : [],
  # This line is used to bring in other Open ERP modules
  # You can leave a trailing ',' inside the list to make it easier when you're adding other modules later
  'depends' : ['account_invoice_salesman',],
  'installable' : True,
  'active' : False,
  # This line would be 'Profiles' to enable it to appear with other profiles during installation
  'category' : 'Generic Modules/Human Resources',
  'author' : 'Netquatro',
  'website' : 'http://openerp.netquatro.com',
}
