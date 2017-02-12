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
import odoorpc
import re
import json

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

class instance_template_action_type(models.Model):
    _name = 'instance.template.action.type'
    _description = 'Instance template action type'

    name = fields.Char('Name', required=True)
    script = fields.Text('Script')
    test_connexion = fields.Many2one('connexion')
    test_script = fields.Text('Test Script')
    return_state = fields.Boolean('Return state')
    return_log = fields.Text('Return Log')
    
    def dict_to_python(self,dict):
        
        res = ""
        for elem in dict:
            res += "%s = %s\n" % (elem, dict[elem])
        return res
    
    @api.multi
    def test(self):
        print "---------------------------"
        print "----------TEST-------------"
        print "---------------------------"
        
        param = {
            '_host':self.test_connexion.host,
            '_port': self.test_connexion.port,
            '_db':self.test_connexion.db,
            '_user': self.test_connexion.identity_id.user,
            '_password': self.test_connexion.identity_id.password,    
            '_ssl':  self.test_connexion.ssl,    
        }
        
        json_param = json.dumps(param)
        
        #pattern = re.compile(r'\b(' + '|'.join(d.keys()) + r')\b')
#        exec(pattern.sub(lambda x: d[x.group()], "%s%s" % (self.script,self.test_script)), locals())
        script = "param=%s\n%s%s" % (json_loads_byteified(json_param), self.script,self.test_script)
        print script
        exec(script, locals())

    @api.multi
    def execute(self,action,connexion):
        param = {
            '_host': connexion.host,
            '_port': connexion.port,
            '_db': connexion.db,
            '_user': connexion.identity_id.user,
            '_password': connexion.identity_id.password,        
            '_ssl':  self.test_connexion.ssl,    
        }
        
        return_dict = {}
        
        exec("%s%s" % (self.script,action.script))
        print"-----------------"
        print "%s%s" % (self.script,action.script)
        print return_dict
        print"-----------------"
        return return_dict
    
class instance_template_action(models.Model):
    _name = 'instance.template.action'
    _description = 'Instance template action'

    name = fields.Char('Name', required=True)
    type_id = fields.Many2one('instance.template.action.type')    
    script = fields.Text('Script')
    return_state = fields.Boolean('Return state')
    return_map_ids = fields.One2many('instance.template.action.return.map','template_action_id',string='Return map')
    
    @api.multi
    def execute(self,action,connexion):
        return self.type_id.execute(self,connexion)

class instance_template_action_return_map(models.Model):
    _name = 'instance.template.action.return.map'
    _description = 'Instance template action return map'

    state = fields.Char('Return Value', required=True)    
    color = fields.Char('Color', required=True)    
    template_action_id = fields.Many2one('instance.template.action')    

        
class instance_template(models.Model):
    _name = 'instance.template'
    _description = 'Instance template'

    name = fields.Char('Name', required=True)
    action_ids = fields.Many2many('instance.template.action','instance_template_action_rel','template_id','action_id', string='Actions')
    
    @api.multi
    def write(self, vals):
        if "action_ids" in vals:
            if len(vals["action_ids"]):
                deleted_actions_ids = list(set(self.action_ids.ids) - set(vals["action_ids"][0][2]))
                added_actions_ids = list(set(vals["action_ids"][0][2]) - set(self.action_ids.ids))
                self.env['instance'].sync_all(self.id, deleted_actions_ids, added_actions_ids)
        
        return super(instance_template,self).write(vals)
        


    
    