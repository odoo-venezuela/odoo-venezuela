# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
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

import time
import wizard
import pooler
#creo el o los formularios
dates_form = '''<?xml version="1.0"?>
<form string="Purchase Report Generator Wizard - Select period(s)">
	<field name="company_id"/>
	<newline/>
	<field name="based_on"/>
	<field name="periods" colspan="4"/>
</form>'''
## En un Diccionario definimos los campos en la vista.
dates_fields = {
#Este es un campo many2one el nombre debe ser el mismo del campo destino en res.company
	'company_id': {'string': 'Company', 'type': 'many2one',
		'relation': 'res.company', 'required': True},
#Es un campo para Pre-seleccionar  si es uno u otro texto en la tupla veo 'field:String'
	'based_on':{'string':'Base on', 'type':'selection', 'selection':[
			('out_invoice','Sales'),
			('in_invoice','Purchase'),
			], 'required':True, 'default': lambda *a: 'in_invoice'},
#fume de humberto para hacerlo por periodos
	'periods': {'string': 'Periods',
                'type': 'many2many', 
                'relation': 'account.period', 
                'help': 'If empty, all periods\n of the current Fiscal Year'},
}

#Creo una clase para ejecutar un wizard igualito que con las tablas de la base de datos.
class wizard_report(wizard.interface):
#Defino un Metodo
	def _get_defaults(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		period_obj = pool.get('account.period')

		user = pool.get('res.users').browse(cr, uid, uid, context=context)
		if user.company_id:
			company_id = user.company_id.id
		else:
			company_id = pool.get('res.company').search(cr, uid,
					[('parent_id', '=', False)])[0]
		data['form']['company_id'] = company_id

		return data['form']

	states = {
		'init': {
			'actions': [_get_defaults],
			'result': {
				'type': 'form',
				'arch': dates_form,
				'fields': dates_fields,
				'state': [
					('end', 'Cancel'),
					('report', 'Print Report')
				]
			}
		},
		'report': {
			'actions': [],
			'result': {
				'type': 'print',
				'report': 'account.purchase.declaration',
				'state':'end'
			}
		}
	}

wizard_report('account.purchase.declaration.wz')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
