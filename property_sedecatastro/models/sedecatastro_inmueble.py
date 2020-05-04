# -*- coding: utf-8 -*-
#https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx?op=Consulta_DNPRC
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

import requests, xmltodict, json
from datetime import datetime
import pytz
import time

class SedecatastroInmueble(models.Model):
    _name = 'sedecatastro.inmueble'
    _description = 'Sedecatastro Inmueble'
    
    sedecatastro_provincia_id = fields.Many2one(
        comodel_name='sedecatastro.provincia',
        string='Sedecatastro Provincia'
    )
    sedecatastro_municipio_id = fields.Many2one(
        comodel_name='sedecatastro.municipio',
        string='Sedecatastro Municipio'
    )
    sedecatastro_via_id = fields.Many2one(
        comodel_name='sedecatastro.via',
        string='Sedecatastro Via'
    )
    sedecatastro_numero_id = fields.Many2one(
        comodel_name='sedecatastro.numero',
        string='Sedecatastro Numero'
    )
    referencia = fields.Char(
        string='Referencia',
        help='Referencia Catastral (Concatenacion de todos los datos de rc)'
    ) 
    idbi_cn = fields.Char(
        string='Idbi Cn',
        help='TIPO DE BIEN INMUEBLE'
    )
    rc_pc1 = fields.Char(
        string='Rc Pc1',
        help='POSICIONES 1-7 DE LA REFERENCIA CATASTRAL (RC) DEL INMUEBLE'
    )
    rc_pc2 = fields.Char(
        string='Rc Pc2',
        help='POSICIONES 8-14 DE LA RC DEL INMUEBLE'
    )
    rc_car = fields.Char(
        string='Rc Car',
        help='POSICIONES 15-19 DE LA RC (CARGO)'
    )
    rc_cc1 = fields.Char(
        string='Rc Cc1',
        help='PRIMER DIGITO DE CONTROL DE LA RC'
    )
    rc_cc2 = fields.Char(
        string='Rc Cc2',
        help='SEGUNDO DIGITO DE CONTROL DE LA RC'
    )
    ldt = fields.Char(
        string='LDT',
        help='DOMICILIO TRIBUTARIO NO ESTRUCTURADO (TEXTO)'
    )
    debi_luso = fields.Char(
        string='Debi Luso',
        help='Residencial'
    )
    debi_sfc = fields.Integer(
        string='Debi Sfc',
        help='SUPERFICIE'
    )
    debi_cpt = fields.Float(
        string='Debi Cpt',
        help='COEFICIENTE DE PARTICIPACION'
    )
    debi_ant = fields.Integer(
        string='Debi Ant',
        help='ANTIGUEDAD'
    )    
    full = fields.Boolean(
        string='Full'
    )
    date_last_check = fields.Date(
        string='Date Last Check'
    )                       
    
    @api.one    
    def action_get_info_sedecatastro(self):
        current_date = datetime.now()
        #return
        return_item = {
            'errors': False,
            'status_code': 200,
            'error': ''
        }
        #fields_to_create_reference
        fields_to_create_reference = ['rc_pc1', 'rc_pc2', 'rc_car', 'rc_cc1', 'rc_cc2']
        #request
        url = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC'
        data_obj = {
            'Provincia': self.sedecatastro_provincia_id.np, 
            'Municipio': self.sedecatastro_municipio_id.nm,
            'RC': str(self.referencia),
        }                 
        response = requests.post(url, data=data_obj)        
        if response.status_code==200:
            xmltodict_response = xmltodict.parse(response.text)
            inmuebles = json.loads(json.dumps(xmltodict_response))            
            if 'consulta_dnp' in inmuebles:
                if 'control' in inmuebles['consulta_dnp']:
                    if inmuebles['consulta_dnp']['control']['cudnp']=='1':
                        #inmueble y toda la info
                        if 'bico' in inmuebles['consulta_dnp']:
                            _logger.info('ok, es solo 1 inmueble con la info completa')
                            
                            if 'bi' in inmuebles['consulta_dnp']['bico']:
                                #ldt
                                self.ldt = str(inmuebles['consulta_dnp']['bico']['bi']['ldt'].encode('utf-8'))
                                #idbi
                                if 'idbi' in inmuebles['consulta_dnp']['bico']['bi']:
                                    self.idbi_cn = str(inmuebles['consulta_dnp']['bico']['bi']['idbi']['cn'])
                                    #rc
                                    if 'rc' in inmuebles['consulta_dnp']['bico']['bi']['idbi']:
                                        self.rc_pc1 = str(inmuebles['consulta_dnp']['bico']['bi']['idbi']['rc']['pc1'])
                                        self.rc_pc2 = str(inmuebles['consulta_dnp']['bico']['bi']['idbi']['rc']['pc2'])
                                        self.rc_car = str(inmuebles['consulta_dnp']['bico']['bi']['idbi']['rc']['car'])
                                        self.rc_cc1 = str(inmuebles['consulta_dnp']['bico']['bi']['idbi']['rc']['cc1'])
                                        self.rc_cc2 = str(inmuebles['consulta_dnp']['bico']['bi']['idbi']['rc']['cc2'])
                                #debi
                                if 'debi' in inmuebles['consulta_dnp']['bico']['bi']:
                                    #luso
                                    if 'luso' in inmuebles['consulta_dnp']['bico']['bi']['debi']:
                                        self.debi_luso = str(inmuebles['consulta_dnp']['bico']['bi']['debi']['luso'].encode('utf-8'))
                                    #sfc
                                    if 'sfc' in inmuebles['consulta_dnp']['bico']['bi']['debi']:
                                        self.debi_sfc = int(inmuebles['consulta_dnp']['bico']['bi']['debi']['sfc'])
                                    #cpt
                                    if 'cpt' in inmuebles['consulta_dnp']['bico']['bi']['debi']:
                                        self.debi_cpt = str(inmuebles['consulta_dnp']['bico']['bi']['debi']['cpt'].replace(',', '.'))
                                    #ant
                                    if 'ant' in inmuebles['consulta_dnp']['bico']['bi']['debi']:
                                        self.debi_ant = int(inmuebles['consulta_dnp']['bico']['bi']['debi']['ant'])                                
                                #lcons
                                if 'lcons' in inmuebles['consulta_dnp']['bico']:
                                    if 'cons' in inmuebles['consulta_dnp']['bico']['lcons']:
                                        #fix multi items
                                        if type(inmuebles['consulta_dnp']['bico']['lcons']['cons'])==dict:
                                            inmuebles['consulta_dnp']['bico']['lcons']['cons'] = [inmuebles['consulta_dnp']['bico']['lcons']['cons']]
                                        #for
                                        for cons_item in inmuebles['consulta_dnp']['bico']['lcons']['cons']:
                                            #cals
                                            sedecatastro_inmueble_construccion_vals = {
                                                'sedecatastro_inmueble_id': self.id,
                                                'lcd': str(cons_item['lcd'])
                                            }
                                            #dt
                                            if 'dt' in cons_item:
                                                if 'lourb' in cons_item['dt']:
                                                    if 'loint' in cons_item['dt']['lourb']:
                                                        #es
                                                        if 'es' in cons_item['dt']['lourb']['loint']:
                                                            sedecatastro_inmueble_construccion_vals['dt_lourb_loint_es'] = int(cons_item['dt']['lourb']['loint']['es'])
                                                        #pt
                                                        if 'pt' in cons_item['dt']['lourb']['loint']:
                                                            sedecatastro_inmueble_construccion_vals['dt_lourb_loint_pt'] = str(cons_item['dt']['lourb']['loint']['pt'])
                                                        #pu
                                                        if 'pu' in cons_item['dt']['lourb']['loint']:
                                                            sedecatastro_inmueble_construccion_vals['dt_lourb_loint_pu'] = str(cons_item['dt']['lourb']['loint']['pu'])
                                            #dfcons
                                            if 'dfcons' in cons_item:
                                                sedecatastro_inmueble_construccion_vals['dfcons_stl'] = int(cons_item['dfcons']['stl'])
                                            #create
                                            sedecatastro_inmueble_construccion_obj = self.env['sedecatastro.inmueble.construccion'].sudo().create(sedecatastro_inmueble_construccion_vals)                        
                        #finall_thins
                        self.full = True
                        self.date_last_check = current_date.strftime("%Y-%m-%d")                                            
        else:
            return {
                'errors': True,
                'status_code': response.status_code,
                'error': {                    
                    'url': url,
                    'data': data_obj,
                    'text': response.text
                }
            }            
        #return
        return return_item
                
    @api.model
    def cron_check_sedecatastro_inmuebles(self):
        _logger.info('cron_check_sedecatastro_inmuebles')                
        
        sedecatastro_numero_ids = self.env['sedecatastro.numero'].search([('full', '=', False)],limit=1000)
        if len(sedecatastro_numero_ids)>0:
            count = 0
            for sedecatastro_numero_id in sedecatastro_numero_ids:
                count += 1
                #action_get_numeros_sedecatastro
                return_item = sedecatastro_numero_id.action_get_inmuebles_sedecatastro()[0]
                if 'errors' in return_item:
                    if return_item['errors']==True:
                        _logger.info(return_item)
                        #fix
                        if return_item['status_code']!=403:
                            _logger.info(paramos)
                        else:
                            _logger.info('Raro que sea un 403 pero pasamos')
                #_logger.info(sedecatastro_numero_id.id)
                percent = (float(count)/float(len(sedecatastro_numero_ids)))*100
                percent = "{0:.2f}".format(percent)                    
                _logger.info(str(sedecatastro_numero_id.id)+' - '+str(percent)+'% ('+str(count)+'/'+str(len(sedecatastro_numero_ids))+')')                
                #update
                sedecatastro_numero_id.full = True
                #Sleep 1 second to prevent error
                time.sleep(1)
                
    @api.model
    def cron_check_sedecatastro_inmuebles_sin_datos(self):
        _logger.info('cron_check_sedecatastro_inmuebles_sin_datos')                
        
        sedecatastro_inmueble_ids = self.env['sedecatastro.inmueble'].search([('full', '=', False)],limit=1000)
        if len(sedecatastro_inmueble_ids)>0:
            count = 0
            for sedecatastro_inmueble_id in sedecatastro_inmueble_ids:
                count += 1
                #action_get_info_sedecatastro
                return_item = sedecatastro_inmueble_id.action_get_info_sedecatastro()[0]
                if 'errors' in return_item:
                    if return_item['errors']==True:
                        _logger.info(return_item)
                        #fix
                        if return_item['status_code']!=403:
                            _logger.info(paramos)
                        else:
                            _logger.info('Raro que sea un 403 pero pasamos')
                #_logger.info(sedecatastro_inmueble_id.id)
                percent = (float(count)/float(len(sedecatastro_inmueble_ids)))*100
                percent = "{0:.2f}".format(percent)                    
                _logger.info(str(sedecatastro_inmueble_id.id)+' - '+str(percent)+'% ('+str(count)+'/'+str(len(sedecatastro_inmueble_ids))+')')                
                #update
                sedecatastro_inmueble_id.full = True
                #Sleep 1 second to prevent error
                time.sleep(1)                