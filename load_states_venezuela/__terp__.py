# module_name/__terp__.py
{
  'name' : 'States Venezuela',
  'version' : '0.1',
  'author' : 'Netquatro',
  'website' : 'http://wiki.openerp.org.ve/index.php?title=Boceto_estados_municipios',
  'category' : 'Localisation/Venezuela',
  'description' : 
'''
This Module only load Venezuela's States on object res.country.state
Este Módulo solo carga los estados de venezuela en la base de datos llenando el objeto res.country.state
''',
  'depends' : ['base'],
  'init_xml' : [],
  'demo_xml' : [],
  'update_xml' : ['load_states_venezuela_data.xml'],
  'installable' : True,
  'active' : False,
}

