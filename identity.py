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

class identity(models.Model):
    _name = 'identity'
    _description = 'Identity'

    name = fields.Char('Name', required=True)    
    user = fields.Char('User', required=True)    
    password = fields.Char('Password', required=True)    

class connexion(models.Model):
    _name = 'connexion'
    _description = 'Connexion'

    name = fields.Char('Name', required=True)    
    identity_id = fields.Many2one('identity', required=True)
    host = fields.Char('Host', required=True)    
    port = fields.Integer('Port')   
    db = fields.Char('DataBase')    

    
    