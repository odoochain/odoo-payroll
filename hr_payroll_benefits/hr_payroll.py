# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


import logging
_logger = logging.getLogger(__name__)

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    benefit_ids = fields.One2many(comodel_name="hr.contract.benefit",inverse_name='contract_id')

    @api.multi
    def benefit_value(self,code):
        return sum(self[0].benefit_ids.filtered(lambda b: b.name == code).mapped('value'))


class hr_contract_benefit(models.Model):
    _name = 'hr.contract.benefit'

    contract_id = fields.Many2one(comodel_name="hr.contract")
    name = fields.Char(string="Code")
    desc = fields.Char(string="Description")
    value = fields.Float(string="Value",digits_compute=dp.get_precision('Payroll'),)



class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def benefit_value(self,code):
        return sum(self.employee_id.contract_id.benefit_ids.filtered(lambda b: b.name == code).mapped('value'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: