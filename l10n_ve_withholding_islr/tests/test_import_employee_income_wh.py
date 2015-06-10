#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Written to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

from openerp.tests.common import TransactionCase


class test_import_csv_employee_income_wh(TransactionCase):
    def setUp(self):
        super(test_import_csv_employee_income_wh, self).setUp()
        ap_obj = self.registry('account.period')
        self.period_id = ap_obj.find(self.cr, self.uid, dt=None,
                                     # exception=False, context=None
                                     )
        self.ixwd_obj = self.registry('islr.xml.wh.doc')
        self.eiw_obj = self.registry('employee.income.wh')

    def _create_ixwd(self):
        cr, uid = self.cr, self.uid
        values = dict(
            name='Importing CSV File',
            period_id=self.period_id[0],
            user_id=uid,
        )
        self.ixwd_id = self.ixwd_obj.create(cr, uid, values)

    def _create_eiw(self):
        cr, uid = self.cr, self.uid
        values = dict(
            type='csv',
            obj_file=None,  # create obj_file as a binary file
        )
        self.eiw_id = self.eiw_obj.create(cr, uid, values)

    def test_import_csv(self):
        self._create_ixwd()
        self._create_eiw()

# EOF
