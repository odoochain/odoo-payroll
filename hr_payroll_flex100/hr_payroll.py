# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2016- Vertel AB (<http://vertel.se>).
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

from openerp import tools
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def _holiday_ids(self):
        self.holiday_ids = self.env['hr.holidays.status'].search([('active','=',True),('limit','=',False)])
        self.holiday_ids += self.env['hr.holidays.status'].search([('id','in',[self.env.ref('l10n_se_hr_payroll.sick_leave_qualify').id,self.env.ref('l10n_se_hr_payroll.sick_leave_214').id,self.env.ref('l10n_se_hr_payroll.sick_leave_100').id])])
    
        
    holiday_ids = fields.Many2many(comodel_name="hr.holidays.status",compute="_holiday_ids")
    @api.one
    def _flextime(self):
        self.flextime = sum(self.env['hr_timesheet_sheet.sheet'].search([('employee_id','=',self.employee_id.id),('date_from','>=',self.date_from),('date_to','<=',self.date_to)]).mapped("total_difference_schema"))
    flextime = fields.Float(string='Flex Time',compute="_flextime")
    @api.one
    def _compensary_leave(self):
        holidays = self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('holiday_status_id','=',self.env.ref("hr_payroll_flex100.compensary_leave").id)])
        self.compensary_leave = sum(holidays.filtered(lambda h: h.type == 'add').mapped("number_of_days_temp")) - sum(holidays.filtered(lambda h: h.type == 'remove').mapped("number_of_days_temp"))
        self.total_compensary_leave = self.compensary_leave + self.flextime
    compensary_leave = fields.Float(string='Compensary Leave',compute="_compensary_leave")
    total_compensary_leave = fields.Float(string='Total Compensary Leave',compute="_compensary_leave")
    
    
    #~ @api.model
    #~ def get_worked_day_lines(self,contract_ids, date_from, date_to, context=None):
        #~ return super(hr_payslip,self).get_worked_day_lines(contract_ids,date_from,date_to)

    @api.one
    def hr_verify_sheet(self):
        number_of_days = self.flextime
        self.env['hr.holidays'].create({
            'holiday_status_id': self.env.ref("hr_payroll_flex100.compensary_leave").id,
            'employee_id': self.employee_id.id,
            'type': 'add' if number_of_days > 0.0 else 'remove' ,
            'state': 'validate',
            'number_of_days_temp': number_of_days,
            #~ 'date_from': self.date_from,
            #~ 'date_to': self.date_to,
            })
        return super(hr_payslip,self).hr_verify_sheet()        

    #~ def refund_sheet(self, cr, uid, ids, context=None):
        #~ mod_obj = self.pool.get('ir.model.data')
        #~ for payslip in self.browse(cr, uid, ids, context=context):
            #~ id_copy = self.copy(cr, uid, payslip.id, {'credit_note': True, 'name': _('Refund: ')+payslip.name}, context=context)
            #~ self.signal_workflow(cr, uid, [id_copy], 'hr_verify_sheet')
            #~ self.signal_workflow(cr, uid, [id_copy], 'process_sheet')
            
        #~ form_id = mod_obj.get_object_reference(cr, uid, 'hr_payroll', 'view_hr_payslip_form')
        #~ form_res = form_id and form_id[1] or False
        #~ tree_id = mod_obj.get_object_reference(cr, uid, 'hr_payroll', 'view_hr_payslip_tree')
        #~ tree_res = tree_id and tree_id[1] or False
        #~ return {
            #~ 'name':_("Refund Payslip"),
            #~ 'view_mode': 'tree, form',
            #~ 'view_id': False,
            #~ 'view_type': 'form',
            #~ 'res_model': 'hr.payslip',
            #~ 'type': 'ir.actions.act_window',
            #~ 'nodestroy': True,
            #~ 'target': 'current',
            #~ 'domain': "[('id', 'in', %s)]" % [id_copy],
            #~ 'views': [(tree_res, 'tree'), (form_res, 'form')],
            #~ 'context': {}
        #~ }
    
 
class hr_holidays(models.Model):
    _inherit='hr.holidays.status'
    
    @api.one
    def _ps_max_leaves(self):
        slip = self.env['hr.payslip'].browse(self._context.get('slip_id',None))
        if slip:
            holiday_ids = self.env['hr.holidays'].search([('holiday_status_id','=',self.id),('state','=','validate'),('employee_id','=',slip.employee_id.id),('date_from','>=',slip.date_from),('date_to','<=',slip.date_to)])
            self.ps_max_leaves = sum(holiday_ids.filtered(lambda h: h.type == 'add').mapped('number_of_days_temp'))
            self.ps_leaves_taken = sum(holiday_ids.filtered(lambda h: h.type == 'remove').mapped('number_of_days_temp'))
    ps_max_leaves = fields.Integer(string='Max Leaves',compute='_ps_max_leaves')
    ps_leaves_taken = fields.Integer(string='Max Leaves',compute='_ps_max_leaves')
      
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: