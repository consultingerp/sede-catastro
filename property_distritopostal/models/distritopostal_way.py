# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

import requests, xmltodict, json
from datetime import datetime
import pytz
import time
from bs4 import BeautifulSoup

class DistritopostalWay(models.Model):
    _name = 'distritopostal.way'
    _description = 'Distritopostal Way'
    
    distritopostal_municipality_id = fields.Many2one(
        comodel_name='distritopostal.municipality',
        string='Distritopostal Municipality Id'
    )
    distritopostal_postalcode_id = fields.Many2one(
        comodel_name='distritopostal.postalcode',
        string='Distritopostal Postalcode Id'
    )    
    name = fields.Char(
        string='Name'
    )
    
    @api.multi    
    def cron_check_ways_distritopostal(self, cr=None, uid=False, context=None):
        _logger.info('cron_check_ways_distritopostal')
        #postalcode
        distritopostal_postalcode_ids = self.env['distritopostal.postalcode'].search([('full', '=', False)], limit=1000)
        if len(distritopostal_postalcode_ids)>0:
            count = 0
            for distritopostal_postalcode_id in distritopostal_postalcode_ids:
                count += 1
                #action_get_ways
                distritopostal_postalcode_id.action_get_ways()[0]
                #_logger                
                percent = (float(count)/float(len(distritopostal_postalcode_ids)))*100
                percent = "{0:.2f}".format(percent)                    
                _logger.info(str(distritopostal_postalcode_id.url)+' - '+str(percent)+'% ('+str(count)+'/'+str(len(distritopostal_postalcode_ids))+')')
        #municipality
        distritopostal_municipality_ids = self.env['distritopostal.municipality'].search([('full', '=', False)], limit=1000)
        _logger.info(len(distritopostal_municipality_ids))
        if len(distritopostal_municipality_ids)>0:
            count = 0
            for distritopostal_municipality_id in distritopostal_municipality_ids:
                count += 1
                #action_get_ways                
                distritopostal_municipality_id.action_get_ways()[0]
                #_logger                
                percent = (float(count)/float(len(distritopostal_municipality_ids)))*100
                percent = "{0:.2f}".format(percent)                    
                _logger.info(str(distritopostal_municipality_id.url)+' - '+str(percent)+'% ('+str(count)+'/'+str(len(distritopostal_municipality_ids))+')')                                                                