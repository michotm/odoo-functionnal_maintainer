# -*- coding: utf-8 -*-
##############################################################################
#
#    Extraschool
#    Copyright (C) 2008-2014 
#    Jean-Michel Abé - Town of La Bruyère (<http://www.labruyere.be>)
#    Michael Michot - Imio (<http://www.imio.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields
from openerp.api import Environment
from datetime import date
import datetime
 
 
class instance(models.Model):
    _name = 'instance'
    _description = 'Instance'
    
    name = fields.Char('Name', required=True)
    template_id = fields.Many2one('instance.template', required=True) 
    connexion_ids = fields.One2many('instance.connexion.item','instance_id',string='Connexion')
    action_ids = fields.One2many('instance.action.item','instance_id',string='Actions')

    @api.multi
    def sync(self):
        action_to_add = []
        for action in self.template_id.action_ids:
            if len(self.action_ids.filtered(lambda r: r.action_template_id.id == action.id)) == 0:                   
                self.action_ids.create( {'name': action.name,
                                         'action_template_id': action.id,
                                         'instance_id': self.id,
                                         'connexion_id': self.connexion_ids.filtered(lambda r: r.action_type_id.id == action.type_id.id).connexion_id.id,
                                        })

class instance_connexion_item(models.Model):
    _name = "instance.connexion.item"
    _description = "Instance connexion item"

    connexion_id = fields.Many2one('connexion', required=True)
    instance_id = fields.Many2one('instance', required=True)
    action_type_id = fields.Many2one('instance.template.action.type', required=True)
    default = fields.Boolean("Default")
    
class instance_action_item(models.Model):
    _name = "instance.action.item"
    _description = "Instance action item"
    
    name= fields.Char('Name', required=True)
    instance_id = fields.Many2one('instance', required=True)
    action_template_id = fields.Many2one('instance.template.action', required=True, ondelete="cascade")
    connexion_id = fields.Many2one('connexion', required=True)
    ir_cron_id = fields.Many2one('ir.cron')    
    return_state = fields.Char('Return state')
    return_log = fields.Text('Return log')
    
    @api.multi
    def execute(self):
        return_dict = self.action_template_id.type_id.execute(self.action_template_id,self.connexion_id)
        print "*************************"
        if 'return_state' in return_dict:
            print "return_state in dict"
            return_map = self.action_template_id.return_map_ids.filtered(lambda r: r.state == str(return_dict['return_state']))
            print return_map
            if len(return_map):
                print "++++++++++++++++++"
                print return_map.color
                return_dict['return_state'] = return_map.color
                
        self.write({'return_state': return_dict['return_state'],
                    'return_log': return_dict['return_log'],})
    
    