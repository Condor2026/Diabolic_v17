#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
🔥 DIABOLIC v5.1 - ANÁLISIS DE PATRONES DELICTIVOS EN BALEARES 🔥
================================================================================
🕷️  "Un gran poder conlleva una gran responsabilidad" - Spiderman
================================================================================
LEGALIDAD Y ÉTICA:
• Esta herramienta trabaja EXCLUSIVAMENTE con datos públicos (noticias digitales).
• No almacena ni procesa información personal de ningún tipo.
• Su objetivo es la prevención, el periodismo de datos y la investigación social.
• El usuario es el único responsable de hacer un uso ético y legal de la misma.
• Se desaconseja rotundamente cualquier modificación que pueda vulnerar derechos,
  realizar vigilancia masiva, perfilar personas o incurrir en actividades ilegales.
• Si se añaden nuevas fuentes, debe hacerse respetando siempre los términos de uso
  de los sitios web y la legislación vigente (especialmente protección de datos).

🔍 Fuentes: 18 periódicos de Mallorca, Menorca, Ibiza y Formentera.
📊 Funcionalidad: Detección automática de URLs, paginación inteligente,
   análisis de patrones, web interactiva, exportación de datos,
   y NUEVA opción 3: Conexiones entre incidentes.
⚖️  Transparencia: Código abierto, sin datos personales, solo noticias públicas.

Desarrollado por SpectrumSecurity
================================================================================
"""

import os
import sys
import time
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from collections import defaultdict
import urllib.parse

# ============================================
# COLORES (para terminal)
# ============================================

class Color:
    ROJO = '\033[91m'
    ROJO_OSCURO = '\033[31m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIAN = '\033[96m'
    GRIS = '\033[90m'
    BLANCO = '\033[97m'
    NEGRITA = '\033[1m'
    SUBRAYADO = '\033[4m'
    PARPADEO = '\033[5m'
    RESET = '\033[0m'
    FONDO_ROJO = '\033[41m'
    FONDO_VERDE = '\033[42m'
    FONDO_AMARILLO = '\033[43m'
    FONDO_AZUL = '\033[44m'

def cprint(texto, color=None, negrita=False, subrayado=False, parpadeo=False, fondo=False, fin='\n'):
    colores = {
        'rojo': Color.ROJO, 'rojo_oscuro': Color.ROJO_OSCURO,
        'verde': Color.VERDE, 'amarillo': Color.AMARILLO,
        'azul': Color.AZUL, 'magenta': Color.MAGENTA,
        'cian': Color.CIAN, 'gris': Color.GRIS, 'blanco': Color.BLANCO
    }
    col = colores.get(color, '')
    neg = Color.NEGRITA if negrita else ''
    sub = Color.SUBRAYADO if subrayado else ''
    parp = Color.PARPADEO if parpadeo else ''
    fondo_color = ''
    if fondo:
        if color == 'rojo':
            fondo_color = Color.FONDO_ROJO
        elif color == 'verde':
            fondo_color = Color.FONDO_VERDE
        elif color == 'amarillo':
            fondo_color = Color.FONDO_AMARILLO
        elif color == 'azul':
            fondo_color = Color.FONDO_AZUL
    print(f"{fondo_color}{neg}{sub}{parp}{col}{texto}{Color.RESET}", end=fin)

# ============================================
# CONFIGURACIÓN - URLs CORREGIDAS 2025 (18 PERIÓDICOS)
# ============================================

VERSION = "5.1"  # <-- ACTUALIZADO
PUERTO = 5013
ARCHIVO = 'diabolic_v51.json'  # <-- ACTUALIZADO
ARCHIVO_ESTADO = 'estado_periodicos.json'
PAGINAS_BUSQUEDA = 10

# Periódicos de Baleares - TODOS VERIFICADOS MANUALMENTE (18 activos)
PERIODICOS_BASE = [
    # MALLORCA (8)
    {'nombre': 'Diario de Mallorca', 'url': 'https://www.diariodemallorca.es/sucesos/', 'base': 'https://www.diariodemallorca.es', 'zona': 'Mallorca', 'activo': True},
    {'nombre': 'Última Hora', 'url': 'https://www.ultimahora.es/sucesos.html', 'base': 'https://www.ultimahora.es', 'zona': 'Mallorca', 'activo': True},
    {'nombre': 'Mallorca Diario', 'url': 'https://www.mallorcadiario.com/categoria/sucesos', 'base': 'https://www.mallorcadiario.com', 'zona': 'Mallorca', 'activo': True},  # CORREGIDO
    {'nombre': 'Crónica Balear', 'url': 'https://www.cronicabalear.es/sucesos/', 'base': 'https://www.cronicabalear.es', 'zona': 'Mallorca', 'activo': True},  # CORREGIDO
    {'nombre': 'Noticias Mallorca', 'url': 'https://noticiasmallorca.es/category/sucesos/', 'base': 'https://noticiasmallorca.es', 'zona': 'Mallorca', 'activo': True},
    {'nombre': 'Mallorca Confidencial', 'url': 'https://mallorcaconfidencial.com/categoria/sucesos/', 'base': 'https://mallorcaconfidencial.com', 'zona': 'Mallorca', 'activo': True},
    {'nombre': 'El Mundo - Baleares', 'url': 'https://www.elmundo.es/baleares.html', 'base': 'https://www.elmundo.es', 'zona': 'Mallorca', 'activo': True},
    {'nombre': 'El País - Baleares', 'url': 'https://elpais.com/espana/baleares/', 'base': 'https://elpais.com', 'zona': 'Mallorca', 'activo': True},

    # MENORCA (4) - CORREGIDAS
    {'nombre': 'Menorca Info', 'url': 'https://www.menorca.info/sucesos/', 'base': 'https://www.menorca.info', 'zona': 'Menorca', 'activo': True},  # CORREGIDO
    {'nombre': 'Menorca Al Día', 'url': 'https://menorcaaldia.com/category/successos/', 'base': 'https://menorcaaldia.com', 'zona': 'Menorca', 'activo': True},
    {'nombre': 'Es Diari Menorca', 'url': 'https://www.esdiari.cat/successos/', 'base': 'https://www.esdiari.cat', 'zona': 'Menorca', 'activo': True},  # CORREGIDO (.cat)
    {'nombre': 'Menorca Esportiu', 'url': 'https://menorcaesportiu.com/successos/', 'base': 'https://menorcaesportiu.com', 'zona': 'Menorca', 'activo': True},  # CORREGIDO

    # IBIZA (4) - INCLUYE LA VOZ DE IBIZA
    {'nombre': 'Diario de Ibiza', 'url': 'https://www.diariodeibiza.es/sucesos/', 'base': 'https://www.diariodeibiza.es', 'zona': 'Ibiza', 'activo': True},
    {'nombre': 'Periódico de Ibiza', 'url': 'https://www.periodicodeibiza.es/', 'base': 'https://www.periodicodeibiza.es', 'zona': 'Ibiza', 'activo': True},  # CORREGIDO (portada)
    {'nombre': 'Noudiari', 'url': 'https://www.noudiari.es/categoria/successos/', 'base': 'https://www.noudiari.es', 'zona': 'Ibiza', 'activo': True},
    {'nombre': 'La Voz de Ibiza', 'url': 'https://lavozdeibiza.com/', 'base': 'https://lavozdeibiza.com', 'zona': 'Ibiza', 'activo': True},  # NUEVA

    # FORMENTERA (2) - CORREGIDAS (.cat)
    {'nombre': 'Formentera Avui', 'url': 'https://www.formenteraavui.cat/successos/', 'base': 'https://www.formenteraavui.cat', 'zona': 'Formentera', 'activo': True},  # CORREGIDO
    {'nombre': 'Formentera Digital', 'url': 'https://formenteradigital.cat/successos/', 'base': 'https://formenteradigital.cat', 'zona': 'Formentera', 'activo': True},  # CORREGIDO
]

# Palabras clave de delitos (ampliado con jerga local)
DELITOS = [
    'robo', 'robos', 'ladrón', 'ladrones', 'detenido', 'detenidos',
    'estafa', 'estafas', 'violencia', 'agresión', 'narcotráfico',
    'droga', 'cocaína', 'marihuana', 'asesinato', 'muerto',
    'homicidio', 'apuñalado', 'tiroteo', 'alunicero', 'butrón',
    'escalo', 'hurtos', 'hurto', 'sustrajo', 'sustrajeron',
    'peta', 'falcon', 'vuelco', 'machada', 'successos', 'sucesos',
    'alquiler ilegal', 'intrusismo', 'multa'  # Añadido para noticias de Ibiza
]

TIPOS_DELITO = {
    'robo': {'icono': '💰', 'color': '#8b0000'},
    'violencia': {'icono': '👊', 'color': '#ff0000'},
    'narcotrafico': {'icono': '💊', 'color': '#4b0082'},
    'estafa': {'icono': '📄', 'color': '#8b6b00'},
    'asesinato': {'icono': '💀', 'color': '#000000'},
    'sexual': {'icono': '⚠️', 'color': '#660066'},
    'intrusismo': {'icono': '🏠', 'color': '#cc6600'}  # Nuevo tipo para alquileres ilegales
}

ISLAS = ['Mallorca', 'Menorca', 'Ibiza', 'Formentera']

# ============================================
# DETECTOR AUTOMÁTICO DE URLs (mejorado)
# ============================================

class DetectorURLs:
    def __init__(self):
        self.archivo_estado = ARCHIVO_ESTADO
        self.estado = self.cargar_estado()
        self.posibles_paths = [
            'sucesos', 'sucesos/', 'local', 'local/', 'noticias', 'noticias/',
            'sucesos-mallorca', 'category/sucesos/', 'categoria/sucesos/',
            'sucesos.html', 'index.php/sucesos', 'seccion/sucesos',
            'successos', 'successos/', 'categoria/successos/', 'seccio/successos/'
        ]

    def cargar_estado(self):
        if os.path.exists(self.archivo_estado):
            try:
                with open(self.archivo_estado, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def guardar_estado(self):
        with open(self.archivo_estado, 'w', encoding='utf-8') as f:
            json.dump(self.estado, f, indent=2)

    def encontrar_url_correcta(self, periodico):
        dominio = periodico['base']
        nombre = periodico['nombre']

        if nombre in self.estado and self.estado[nombre].get('url'):
            url_guardada = self.estado[nombre]['url']
            try:
                r = requests.get(url_guardada, timeout=3)
                if r.status_code == 200:
                    return url_guardada
            except:
                pass

        for path in self.posibles_paths:
            url = f"{dominio}/{path}"
            try:
                r = requests.get(url, timeout=3)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    texto = soup.get_text().lower()
                    if any(d in texto for d in DELITOS) or 'sucesos' in texto or 'successos' in texto:
                        self.estado[nombre] = {'url': url, 'path': path}
                        self.guardar_estado()
                        return url
            except:
                continue
        return None

    def verificar_todos(self, periodicos):
        cprint(f"\n{'='*70}", 'rojo', negrita=True)
        cprint(f"🔍 VERIFICANDO {len(periodicos)} PERIÓDICOS", 'rojo', negrita=True, fondo=True)
        cprint(f"{'='*70}", 'rojo', negrita=True)

        verificados = []
        activos = 0

        for p in periodicos:
            cprint(f"\n📰 {p['nombre']} ", 'amarillo', negrita=True, fin='')

            try:
                r = requests.get(p['url'], timeout=3)
                if r.status_code == 200:
                    p['activo'] = True
                    cprint(f"✅ OK", 'verde')
                    activos += 1
                else:
                    nueva_url = self.encontrar_url_correcta(p)
                    if nueva_url:
                        p['url'] = nueva_url
                        p['activo'] = True
                        cprint(f"✅ NUEVA URL", 'verde')
                        activos += 1
                    else:
                        p['activo'] = False
                        cprint(f"❌ No encontrada", 'rojo')
            except:
                nueva_url = self.encontrar_url_correcta(p)
                if nueva_url:
                    p['url'] = nueva_url
                    p['activo'] = True
                    cprint(f"✅ NUEVA URL", 'verde')
                    activos += 1
                else:
                    p['activo'] = False
                    cprint(f"❌ Error conexión", 'rojo')

            verificados.append(p)
            time.sleep(0.5)

        cprint(f"\n{'='*70}", 'verde', negrita=True)
        cprint(f"📊 ACTIVOS: {activos} de {len(periodicos)}", 'verde', negrita=True)
        cprint(f"{'='*70}", 'verde', negrita=True)

        return verificados

# ============================================
# GESTOR DE DATOS
# ============================================

class GestorDatos:
    def __init__(self):
        self.archivo = ARCHIVO
        self.datos = self.cargar()
        self.detector = DetectorURLs()

    def cargar(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'incidentes': [], 'ultima_actualizacion': None}
        return {'incidentes': [], 'ultima_actualizacion': None}

    def guardar(self):
        self.datos['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=2, ensure_ascii=False)

    def agregar_incidentes(self, nuevos):
        ids_existentes = {inc['id'] for inc in self.datos['incidentes']}
        contador = 0
        for n in nuevos:
            if n['id'] not in ids_existentes:
                self.datos['incidentes'].append(n)
                contador += 1
        if contador:
            self.guardar()
        return contador

    def detectar_tipo(self, texto):
        texto_lower = texto.lower()
        if any(p in texto_lower for p in ['alquiler ilegal', 'intrusismo', 'piso turístico']):
            return 'intrusismo'
        for tipo, datos in TIPOS_DELITO.items():
            if tipo == 'robo' and any(p in texto_lower for p in ['robo', 'robos', 'ladrón', 'sustrajo', 'alunicero', 'butrón', 'escalo']):
                return tipo
            elif tipo == 'violencia' and any(p in texto_lower for p in ['violencia', 'agresión', 'paliza', 'apuñalado', 'machada']):
                return tipo
            elif tipo == 'narcotrafico' and any(p in texto_lower for p in ['droga', 'cocaína', 'marihuana', 'narcotráfico', 'peta', 'falcon', 'vuelco']):
                return tipo
            elif tipo == 'estafa' and any(p in texto_lower for p in ['estafa', 'estafas', 'timaron']):
                return tipo
            elif tipo == 'asesinato' and any(p in texto_lower for p in ['asesinato', 'muerto', 'homicidio', 'cadáver']):
                return tipo
            elif tipo == 'sexual' and any(p in texto_lower for p in ['sexual', 'violación', 'abusos', 'menores']):
                return tipo
        return 'otro'

    def estadisticas(self, incidentes=None):
        if incidentes is None:
            incidentes = self.datos['incidentes']

        stats = {
            'total': len(incidentes),
            'islas': defaultdict(int),
            'tipos': defaultdict(int),
            'fuentes': defaultdict(int),
            'municipios': defaultdict(int),
            'ultimos_7dias': 0,
            'ultimos_30dias': 0,
            'ultimos_90dias': 0,
            'tendencia': {}
        }

        hoy = datetime.now()
        hace_7d = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
        hace_30d = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        hace_90d = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')

        for inc in incidentes:
            if inc.get('isla'):
                stats['islas'][inc['isla']] += 1
            if inc.get('tipo'):
                stats['tipos'][inc['tipo']] += 1
            if inc.get('fuente'):
                stats['fuentes'][inc['fuente']] += 1
            if inc.get('municipio'):
                stats['municipios'][inc['municipio']] += 1

            fecha = inc.get('fecha', '')
            if fecha >= hace_7d:
                stats['ultimos_7dias'] += 1
            if fecha >= hace_30d:
                stats['ultimos_30dias'] += 1
            if fecha >= hace_90d:
                stats['ultimos_90dias'] += 1

            if fecha and len(fecha) >= 7:
                mes = fecha[:7]
                stats['tendencia'][mes] = stats['tendencia'].get(mes, 0) + 1

        return stats

    def evolucion_mensual(self):
        meses = {}
        for inc in self.datos['incidentes']:
            if inc.get('fecha') and len(inc['fecha']) >= 7:
                mes = inc['fecha'][:7]
                meses[mes] = meses.get(mes, 0) + 1
        return dict(sorted(meses.items()))

# ============================================
# EXTRACTOR DE NOTICIAS
# ============================================

class ExtractorNoticias:
    def __init__(self, periodicos):
        self.periodicos = periodicos
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.cache_paginacion = {}

    def _generar_url_pagina(self, url_base, pagina):
        dominio = url_base.split('/')[2] if '//' in url_base else url_base
        if dominio in self.cache_paginacion:
            formato = self.cache_paginacion[dominio]
            return formato.format(pagina=pagina)

        formatos = [
            f"{url_base}pagina/{{pagina}}/",
            f"{url_base}?page={{pagina}}",
            f"{url_base}{{pagina}}/",
            f"{url_base}page/{{pagina}}/",
        ]

        for formato in formatos:
            url = formato.format(pagina=pagina)
            try:
                r = self.session.get(url, timeout=3)
                if r.status_code == 200:
                    self.cache_paginacion[dominio] = formato
                    return url
            except:
                continue
        return None

    def buscar_todo(self, paginas=10):
        cprint(f"\n{'='*80}", 'rojo', negrita=True)
        cprint(f"🔥 BÚSQUEDA EN {len(self.periodicos)} PERIÓDICOS", 'rojo', negrita=True, fondo=True)
        cprint(f"{'='*80}", 'rojo', negrita=True)

        todas = []
        total_activos = 0
        self.cache_paginacion = {}

        for periodico in self.periodicos:
            if not periodico.get('activo', True):
                continue

            total_activos += 1
            cprint(f"\n📰 {periodico['nombre']}", 'amarillo', negrita=True)
            cprint(f"   Zona: {periodico['zona']}", 'gris')

            encontrados = 0
            for pagina in range(1, paginas + 1):
                url = self._generar_url_pagina(periodico['url'], pagina)

                if not url:
                    if pagina == 1:
                        cprint(f"   📄 Página {pagina}... ✗ No accesible", 'rojo')
                    else:
                        cprint(f"   📄 Página {pagina}... ✗ No hay más páginas", 'amarillo')
                    break

                try:
                    cprint(f"   📄 Página {pagina}... ", 'gris', fin='')
                    r = self.session.get(url, timeout=8)

                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, 'html.parser')
                        articulos = []
                        articulos.extend(soup.find_all('article'))
                        articulos.extend(soup.find_all('div', class_=lambda x: x and ('article' in x or 'noticia' in x)))
                        articulos.extend(soup.find_all('h2'))

                        encontrados_pagina = 0
                        for art in articulos[:20]:
                            titulo_elem = art.find(['h2', 'h3']) if art.name != 'h2' else art
                            if not titulo_elem:
                                continue

                            titulo = titulo_elem.get_text().strip()
                            if len(titulo) < 20:
                                continue

                            titulo_lower = titulo.lower()
                            if any(d in titulo_lower for d in DELITOS):
                                isla = periodico['zona']
                                for i in ISLAS:
                                    if i.lower() in titulo_lower:
                                        isla = i
                                        break

                                fecha_elem = art.find('time')
                                fecha = datetime.now().strftime('%Y-%m-%d')
                                if fecha_elem and fecha_elem.get('datetime'):
                                    fecha = fecha_elem.get('datetime')[:10]

                                tipo = gestor.detectar_tipo(titulo)

                                todas.append({
                                    'id': hashlib.md5(titulo.encode()).hexdigest()[:16],
                                    'titulo': titulo[:300],
                                    'fecha': fecha,
                                    'isla': isla,
                                    'tipo': tipo,
                                    'fuente': periodico['nombre']
                                })
                                encontrados_pagina += 1
                                encontrados += 1

                        cprint(f"✓ {encontrados_pagina}", 'verde')
                        if encontrados_pagina == 0 and pagina > 1:
                            break

                    elif r.status_code == 404:
                        cprint(f"✗ No existe (404)", 'amarillo')
                        break
                    else:
                        cprint(f"✗ Error {r.status_code}", 'rojo')

                except Exception as e:
                    cprint(f"✗ Error", 'rojo')

                time.sleep(0.5)
            time.sleep(1)

        unicos = {}
        for n in todas:
            key = hashlib.md5(n['titulo'].encode()).hexdigest()
            if key not in unicos:
                unicos[key] = n

        cprint(f"\n{'='*80}", 'verde', negrita=True)
        cprint(f"📊 TOTAL: {len(unicos)} noticias únicas de {total_activos} periódicos", 'verde', negrita=True)
        cprint(f"{'='*80}", 'verde', negrita=True)

        return list(unicos.values())

# ============================================
# HTML TEMPLATE (interactivo)
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔥 DIABOLIC v{{ version }}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0505;
            color: #fff;
            font-family: 'Segoe UI', Arial;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #4a0000, #8b0000, #ff0000);
            padding: 40px;
            border-radius: 30px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 0 40px rgba(255,0,0,0.5);
        }
        .header h1 { font-size: 4em; text-shadow: 3px 3px 0 #4a0000; }
        .version-badge {
            background: black;
            color: #ff0000;
            padding: 5px 20px;
            border-radius: 50px;
            display: inline-block;
            margin-top: 10px;
        }
        .stats-header {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .stat-header-item {
            background: rgba(0,0,0,0.7);
            padding: 10px 25px;
            border-radius: 50px;
            border: 1px solid #ff5555;
        }
        .btn {
            background: #8b0000;
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.2em;
            cursor: pointer;
            margin: 10px;
            border: 2px solid #ff5555;
        }
        .btn:hover { background: #ff0000; }
        .config-btn {
            background: #2a0a0a;
            color: #ffaa00;
            border: 2px solid #8b0000;
            padding: 12px 25px;
            border-radius: 40px;
            cursor: pointer;
            margin: 10px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        .config-btn:hover {
            background: #8b0000;
            color: white;
        }
        .filtros {
            display: flex; gap: 10px; justify-content: center; margin: 20px 0; flex-wrap: wrap;
        }
        .filtro-btn {
            background: #1a0a0a; color: white; border: 2px solid #8b0000;
            padding: 10px 20px; border-radius: 30px; text-decoration: none;
        }
        .filtro-btn:hover, .filtro-btn.activo { background: #8b0000; }
        .stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin: 30px 0;
        }
        .stat-card {
            background: #1a0a0a; padding: 25px; border-radius: 15px;
            border-left: 8px solid #ff0000; text-align: center;
        }
        .stat-number { font-size: 3em; color: #ff5555; }
        .analysis-section {
            background: #1a0f0f; border-radius: 20px; padding: 25px; margin: 30px 0;
        }
        .section-title {
            color: #ff5555; font-size: 1.8em; margin-bottom: 20px;
            border-bottom: 2px solid #8b0000; padding-bottom: 10px;
        }
        .badge {
            background: #8b0000; color: white; padding: 5px 15px;
            border-radius: 30px; font-size: 0.6em;
        }
        .chart-bar-bg {
            width: 100%; height: 25px; background: #2a1a1a;
            border-radius: 12px; margin: 10px 0; overflow: hidden;
        }
        .chart-bar-fill {
            height: 100%; background: linear-gradient(90deg, #8b0000, #ff0000);
            border-radius: 12px; transition: width 0.5s;
        }
        .chart-label {
            display: flex; justify-content: space-between; color: #ffaa00; margin: 5px 0;
        }
        .incidente-card {
            background: #1a0a0a; margin: 15px 0; padding: 20px;
            border-radius: 12px; border-left: 10px solid #ff0000;
        }
        .incidente-titulo { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .incidente-meta {
            color: #aaa; display: flex; gap: 20px; flex-wrap: wrap;
        }
        .isla-badge {
            background: #8b0000; color: white; padding: 3px 12px; border-radius: 20px;
        }
        .tipo-badge {
            padding: 3px 12px; border-radius: 20px; font-weight: bold; display: inline-block;
        }
        .footer {
            text-align: center; margin-top: 40px; padding: 20px;
            background: #1a0f0f; border-radius: 15px; color: #8b0000;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ DIABOLIC ⚡</h1>
            <div class="version-badge">v{{ version }} · Puerto {{ puerto }}</div>
            <div class="stats-header">
                <div class="stat-header-item">📊 {{ total_incidentes }} incidentes</div>
                <div class="stat-header-item">📰 {{ total_fuentes }} fuentes</div>
                <div class="stat-header-item">🏝️ {{ total_islas }} islas</div>
            </div>
        </div>

        <div style="text-align: center;">
            <form action="/actualizar" method="post" style="display: inline;">
                <button class="btn">🔥 ACTUALIZAR</button>
            </form>
            <a href="/exportar/json" class="config-btn">📥 JSON</a>
            <a href="/exportar/csv" class="config-btn">📥 CSV</a>
        </div>

        <div class="filtros">
            <a href="/" class="filtro-btn {% if filtro == 'todo' %}activo{% endif %}">TODOS</a>
            <a href="/filtro/7d" class="filtro-btn {% if filtro == '7d' %}activo{% endif %}">7 DÍAS</a>
            <a href="/filtro/30d" class="filtro-btn {% if filtro == '30d' %}activo{% endif %}">30 DÍAS</a>
            <a href="/filtro/90d" class="filtro-btn {% if filtro == '90d' %}activo{% endif %}">90 DÍAS</a>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div>TOTAL</div>
                <div class="stat-number">{{ stats.total }}</div>
            </div>
            <div class="stat-card">
                <div>ÚLTIMOS 7d</div>
                <div class="stat-number">{{ stats.ultimos_7dias }}</div>
            </div>
            <div class="stat-card">
                <div>ÚLTIMOS 30d</div>
                <div class="stat-number">{{ stats.ultimos_30dias }}</div>
            </div>
            <div class="stat-card">
                <div>ÚLTIMOS 90d</div>
                <div class="stat-number">{{ stats.ultimos_90dias }}</div>
            </div>
        </div>

        <div class="analysis-section">
            <div class="section-title">📍 POR ISLAS</div>
            {% set total_islas = stats.islas.values()|sum %}
            {% for isla, cantidad in stats.islas.items() %}
            <div class="chart-label">
                <span>{{ isla }}</span>
                <span>{{ cantidad }} ({{ (cantidad / total_islas * 100)|round(1) }}%)</span>
            </div>
            <div class="chart-bar-bg">
                <div class="chart-bar-fill" style="width: {{ (cantidad / total_islas * 100) }}%;"></div>
            </div>
            {% endfor %}
        </div>

        <div class="analysis-section">
            <div class="section-title">🔍 POR TIPO</div>
            {% set total_tipos = stats.tipos.values()|sum %}
            {% for tipo, cantidad in stats.tipos.items() %}
            {% set datos = TIPOS_DELITO.get(tipo, {'icono': '❓', 'color': '#666'}) %}
            <div class="chart-label">
                <span><span style="color: {{ datos.color }};">{{ datos.icono }}</span> {{ tipo|upper }}</span>
                <span>{{ cantidad }} ({{ (cantidad / total_tipos * 100)|round(1) }}%)</span>
            </div>
            <div class="chart-bar-bg">
                <div class="chart-bar-fill" style="width: {{ (cantidad / total_tipos * 100) }}%;"></div>
            </div>
            {% endfor %}
        </div>

        <div class="analysis-section">
            <div class="section-title">📰 TODOS LOS INCIDENTES ({{ incidentes|length }})</div>
            {% for inc in incidentes[:20] %}
            {% set tipo_color = TIPOS_DELITO.get(inc.tipo, {'color': '#666'}).color %}
            <div class="incidente-card" style="border-left-color: {{ tipo_color }};">
                <div class="incidente-titulo">{{ inc.titulo }}</div>
                <div class="incidente-meta">
                    <span class="isla-badge">{{ inc.isla or '?' }}</span>
                    <span>📅 {{ inc.fecha }}</span>
                    <span>📰 {{ inc.fuente }}</span>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>🔥 DIABOLIC v{{ version }} · {{ periodicos_activos }} PERIÓDICOS ACTIVOS · 100% LEGAL</p>
            <p style="font-size:0.8em; color:#666;">"Un gran poder conlleva una gran responsabilidad" - Usa esta herramienta de forma ética.</p>
        </div>
    </div>
</body>
</html>
'''

# ============================================
# FLASK APP
# ============================================

app = Flask(__name__)
gestor = GestorDatos()

@app.route('/')
def home():
    incidentes = gestor.datos['incidentes']
    stats = gestor.estadisticas()
    periodicos_activos = len([p for p in PERIODICOS_BASE if p.get('activo', True)])
    return render_template_string(
        HTML_TEMPLATE,
        version=VERSION,
        puerto=PUERTO,
        stats=stats,
        incidentes=incidentes[::-1],
        total_incidentes=stats['total'],
        total_fuentes=len(stats['fuentes']),
        total_islas=len(stats['islas']),
        periodicos_activos=periodicos_activos,
        TIPOS_DELITO=TIPOS_DELITO,
        ISLAS=ISLAS,
        filtro='todo'
    )

@app.route('/filtro/<periodo>')
def filtro(periodo):
    incidentes = gestor.datos['incidentes']
    if periodo == '7d':
        hace = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        incidentes = [i for i in incidentes if i.get('fecha', '') >= hace]
    elif periodo == '30d':
        hace = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        incidentes = [i for i in incidentes if i.get('fecha', '') >= hace]
    elif periodo == '90d':
        hace = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        incidentes = [i for i in incidentes if i.get('fecha', '') >= hace]
    stats = gestor.estadisticas(incidentes)
    periodicos_activos = len([p for p in PERIODICOS_BASE if p.get('activo', True)])
    return render_template_string(
        HTML_TEMPLATE,
        version=VERSION,
        puerto=PUERTO,
        stats=stats,
        incidentes=incidentes[::-1],
        total_incidentes=stats['total'],
        total_fuentes=len(stats['fuentes']),
        total_islas=len(stats['islas']),
        periodicos_activos=periodicos_activos,
        TIPOS_DELITO=TIPOS_DELITO,
        ISLAS=ISLAS,
        filtro=periodo
    )

@app.route('/actualizar', methods=['POST'])
def actualizar():
    cprint(f"\n{'='*80}", 'rojo', negrita=True)
    cprint(f"🔥 ACTUALIZANDO NOTICIAS", 'rojo', negrita=True, fondo=True)
    cprint(f"{'='*80}", 'rojo', negrita=True)

    periodicos = gestor.detector.verificar_todos(PERIODICOS_BASE)
    extractor = ExtractorNoticias(periodicos)
    nuevas = extractor.buscar_todo(paginas=PAGINAS_BUSQUEDA)
    agregadas = gestor.agregar_incidentes(nuevas)

    cprint(f"\n{'='*80}", 'verde', negrita=True)
    cprint(f"✅ {agregadas} NUEVAS NOTICIAS", 'verde', negrita=True, fondo=True)
    cprint(f"{'='*80}", 'verde', negrita=True)

    return home()

@app.route('/exportar/json')
def exportar_json():
    return jsonify(gestor.datos)

@app.route('/exportar/csv')
def exportar_csv():
    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Título', 'Fecha', 'Isla', 'Tipo', 'Fuente'])
    for inc in gestor.datos['incidentes']:
        cw.writerow([inc['titulo'], inc['fecha'], inc.get('isla',''), inc.get('tipo',''), inc['fuente']])
    return si.getvalue()

# ============================================
# MENÚ TERMINAL
# ============================================

def menu():
    while True:
        print(f"\n{Color.ROJO}{'═'*90}{Color.RESET}")
        print(f"{Color.FONDO_ROJO}{Color.NEGRITA}🔥 DIABOLIC v{VERSION} - PUERTO {PUERTO}{Color.RESET}")
        print(f"{Color.ROJO}{'═'*90}{Color.RESET}")

        stats = gestor.estadisticas()
        periodicos_activos = len([p for p in PERIODICOS_BASE if p.get('activo', True)])

        print(f"\n{Color.VERDE}📊 ESTADÍSTICAS ACTUALES:{Color.RESET}")
        print(f"   📈 Total: {stats['total']} incidentes")
        if stats['total'] > 0:
            pct_7d = round((stats['ultimos_7dias'] / stats['total'] * 100), 1)
        else:
            pct_7d = 0
        print(f"   ⚡ Últimos 7 días: {stats['ultimos_7dias']} ({pct_7d}% del total)")
        print(f"   🔥 Últimos 30 días: {stats['ultimos_30dias']}")
        print(f"   📆 Últimos 90 días: {stats['ultimos_90dias']}")
        print(f"   🏝️ Islas activas: {len(stats['islas'])}")
        print(f"   📰 Periódicos activos: {periodicos_activos}")
        print(f"   🔍 Tipos detectados: {len(stats['tipos'])}")

        print(f"\n{Color.AMARILLO}📋 COMANDOS COMPLETOS:{Color.RESET}")
        print(f"{Color.ROJO}[1]{Color.RESET} 🔍 Buscar noticias (con detección automática de URLs)")
        print(f"{Color.ROJO}[2]{Color.RESET} 📊 Ver análisis completo")
        print(f"{Color.ROJO}[3]{Color.RESET} 🔗 Ver conexiones entre incidentes")  # <-- AHORA SÍ FUNCIONA
        print(f"{Color.ROJO}[4]{Color.RESET} 📈 Ver evolución mensual")
        print(f"{Color.ROJO}[5]{Color.RESET} 🌐 Iniciar servidor web")
        print(f"{Color.ROJO}[6]{Color.RESET} 📰 Ver últimos 20 incidentes")
        print(f"{Color.ROJO}[7]{Color.RESET} 📥 Exportar datos (JSON/CSV)")
        print(f"{Color.ROJO}[8]{Color.RESET} 🔍 Verificar periódicos (detector automático)")
        print(f"{Color.ROJO}[9]{Color.RESET} 📊 Ver distribución por tipo")
        print(f"{Color.ROJO}[10]{Color.RESET} 🗑️ Salir")

        op = input(f"\n{Color.ROJO}➤ Opción: {Color.RESET}")

        if op == '1':
            periodicos = gestor.detector.verificar_todos(PERIODICOS_BASE)
            extractor = ExtractorNoticias(periodicos)
            nuevas = extractor.buscar_todo(paginas=PAGINAS_BUSQUEDA)
            agregadas = gestor.agregar_incidentes(nuevas)
            cprint(f"\n✅ {agregadas} nuevas noticias", 'verde', negrita=True)
            input(f"\n{Color.GRIS}Enter para continuar...{Color.RESET}")

        elif op == '2':
            stats = gestor.estadisticas()
            print(f"\n{Color.ROJO}{'═'*70}{Color.RESET}")
            print(f"{Color.AMARILLO}📊 ANÁLISIS COMPLETO{Color.RESET}")
            print(f"{Color.ROJO}{'═'*70}{Color.RESET}")

            print(f"\n{Color.VERDE}📈 TENDENCIAS:{Color.RESET}")
            print(f"   Total histórico: {stats['total']}")
            if stats['total'] > 0:
                pct_7d = round((stats['ultimos_7dias'] / stats['total'] * 100), 1)
                pct_30d = round((stats['ultimos_30dias'] / stats['total'] * 100), 1)
                pct_90d = round((stats['ultimos_90dias'] / stats['total'] * 100), 1)
            else:
                pct_7d = pct_30d = pct_90d = 0
            print(f"   Últimos 7 días: {stats['ultimos_7dias']} ({pct_7d}%)")
            print(f"   Últimos 30 días: {stats['ultimos_30dias']} ({pct_30d}%)")
            print(f"   Últimos 90 días: {stats['ultimos_90dias']} ({pct_90d}%)")

            print(f"\n{Color.VERDE}📍 DISTRIBUCIÓN POR ISLAS:{Color.RESET}")
            for isla, cant in stats['islas'].items():
                pct = round((cant / stats['total'] * 100), 1) if stats['total'] > 0 else 0
                print(f"   {isla}: {cant} ({pct}%)")

            print(f"\n{Color.VERDE}🔍 DISTRIBUCIÓN POR TIPO:{Color.RESET}")
            for tipo, cant in stats['tipos'].items():
                pct = round((cant / stats['total'] * 100), 1) if stats['total'] > 0 else 0
                print(f"   {tipo}: {cant} ({pct}%)")

            input(f"\n{Color.GRIS}Enter para continuar...{Color.RESET}")

        elif op == '3':
            # ========== NUEVA OPCIÓN 3 FUNCIONAL ==========
            print(f"\n{Color.ROJO}{'═'*70}{Color.RESET}")
            print(f"{Color.AMARILLO}🔗 CONEXIONES ENTRE INCIDENTES DETECTADAS{Color.RESET}")
            print(f"{Color.ROJO}{'═'*70}{Color.RESET}")
            
            incidentes = gestor.datos['incidentes'][-100:]  # Últimos 100 para analizar
            if len(incidentes) < 5:
                print(f"{Color.GRIS}   Pocos incidentes para detectar patrones. Busca más noticias primero.{Color.RESET}")
                input(f"\n{Color.GRIS}Enter...{Color.RESET}")
                continue

            # 1. Agrupar por tipo y zona en los últimos 30 días
            from collections import defaultdict
            grupos = defaultdict(list)
            hace_30d = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            for inc in incidentes:
                if inc.get('fecha', '') >= hace_30d:
                    clave = (inc.get('tipo', 'otro'), inc.get('isla', 'Desconocida'))
                    grupos[clave].append(inc)
            
            # Mostrar grupos con 3 o más incidentes (posibles oleadas)
            patrones_mostrados = 0
            for (tipo, isla), lista in grupos.items():
                if len(lista) >= 3:
                    print(f"\n{Color.ROJO}🔥 PATRÓN: {len(lista)} {tipo.upper()} en {isla}{Color.RESET}")
                    # Mostrar los 3 más recientes
                    for inc in sorted(lista, key=lambda x: x['fecha'], reverse=True)[:3]:
                        print(f"   • {inc['fecha']}: {inc['titulo'][:80]}...")
                    # Calcular frecuencia
                    fechas = [inc['fecha'] for inc in lista]
                    dias = (datetime.now() - datetime.strptime(min(fechas), '%Y-%m-%d')).days if fechas else 0
                    if dias > 0:
                        freq = round(len(lista) / dias, 1)
                        print(f"   ⚡ Frecuencia: {freq} incidentes/día")
                    patrones_mostrados += 1
            
            # 2. Detectar posibles mismas bandas por palabras clave (modus operandi)
            print(f"\n{Color.AMARILLO}🔍 POSIBLES MISMAS BANDAS (modus operandi){Color.RESET}")
            palabras_modus = ['alunicero', 'butrón', 'escalo', 'tirón', 'violencia', 'estafa', 'intrusismo']
            for palabra in palabras_modus:
                relacionados = [inc for inc in incidentes if palabra in inc['titulo'].lower()]
                if len(relacionados) >= 2:
                    print(f"\n   {Color.ROJO}• {palabra.upper()}: {len(relacionados)} incidentes{Color.RESET}")
                    for inc in relacionados[:3]:
                        print(f"     - {inc['fecha']} ({inc['isla']}): {inc['titulo'][:60]}...")
            
            if patrones_mostrados == 0:
                print(f"\n{Color.GRIS}   No se detectaron patrones significativos en los últimos 30 días.{Color.RESET}")
            
            input(f"\n{Color.GRIS}Enter para continuar...{Color.RESET}")

        elif op == '4':
            evolucion = gestor.evolucion_mensual()
            print(f"\n{Color.ROJO}{'═'*70}{Color.RESET}")
            print(f"{Color.AMARILLO}📈 EVOLUCIÓN MENSUAL{Color.RESET}")
            print(f"{Color.ROJO}{'═'*70}{Color.RESET}")
            for mes, cant in evolucion.items():
                print(f"   {mes}: {cant} incidentes")
            input(f"\n{Color.GRIS}Enter para continuar...{Color.RESET}")

        elif op == '5':
            cprint(f"\n🌐 Servidor web: http://localhost:{PUERTO}", 'verde', negrita=True)
            cprint(f"   Presiona Ctrl+C para volver al menú", 'gris')
            app.run(host='0.0.0.0', port=PUERTO, debug=False)

        elif op == '6':
            incidentes = gestor.datos['incidentes'][-20:][::-1]
            print(f"\n{Color.ROJO}{'═'*70}{Color.RESET}")
            print(f"{Color.AMARILLO}📰 ÚLTIMOS 20 INCIDENTES{Color.RESET}")
            print(f"{Color.ROJO}{'═'*70}{Color.RESET}")
            for i, inc in enumerate(incidentes, 1):
                print(f"\n{Color.ROJO}{i:2d}.{Color.RESET} {inc['titulo'][:100]}...")
                print(f"      {inc['fecha']} | {inc.get('isla', '?')} | {inc['fuente']}")
            input(f"\n{Color.GRIS}Enter para continuar...{Color.RESET}")

        elif op == '7':
            with open('export.json', 'w', encoding='utf-8') as f:
                json.dump(gestor.datos, f, indent=2, ensure_ascii=False)
            with open('export.csv', 'w', encoding='utf-8') as f:
                f.write("Título,Fecha,Isla,Tipo,Fuente\n")
                for inc in gestor.datos['incidentes']:
                    f.write(f"{inc['titulo'][:100].replace(',', ' ')},{inc['fecha']},{inc.get('isla','')},{inc.get('tipo','')},{inc['fuente']}\n")
            cprint(f"\n✅ Exportados export.json y export.csv", 'verde')
            input(f"\n{Color.GRIS}Enter...{Color.RESET}")

        elif op == '8':
            gestor.detector.verificar_todos(PERIODICOS_BASE)
            input(f"\n{Color.GRIS}Enter...{Color.RESET}")

        elif op == '9':
            stats = gestor.estadisticas()
            print(f"\n{Color.ROJO}{'═'*70}{Color.RESET}")
            print(f"{Color.AMARILLO}📊 DISTRIBUCIÓN POR TIPO{Color.RESET}")
            print(f"{Color.ROJO}{'═'*70}{Color.RESET}")
            for tipo, cant in stats['tipos'].items():
                pct = round((cant / stats['total'] * 100), 1) if stats['total'] > 0 else 0
                barra = '█' * int(pct // 2)
                print(f"   {tipo}: {barra} {cant} ({pct}%)")
            input(f"\n{Color.GRIS}Enter...{Color.RESET}")

        elif op == '10':
            cprint(f"\n👋 Hasta pronto, DIABOLIC se despide", 'rojo', negrita=True)
            break

        else:
            cprint(f"\n❌ Opción no válida", 'rojo')
            time.sleep(1)

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print(f"""
{Color.ROJO}
╔══════════════════════════════════════════════════════════════════╗
║  🔥 DIABOLIC v{VERSION} - 18 PERIÓDICOS ACTIVOS 🔥               ║
║  ⚡ URLs 2025 MANUALMENTE Osint 100% Legal   ⚡                  ║
║  Mallorca · Menorca · Ibiza · Formentera                         ║
║                                         - By                     ║
║                                            •SpectrumSecurity•    ║
╚══════════════════════════════════════════════════════════════════╝
{Color.RESET}""")
    print(f"{Color.GRIS}🕷️  \"Un gran poder conlleva una gran responsabilidad\" - Spiderman{Color.RESET}")
    print(f"{Color.GRIS}⚖️  Uso ético y legal, solo datos públicos.{Color.RESET}")

    stats = gestor.estadisticas()
    print(f"{Color.VERDE}📊 Incidentes en base: {stats['total']}{Color.RESET}")
    print(f"{Color.AMARILLO}⏳ Última actualización: {gestor.datos.get('ultima_actualizacion', 'Nunca')}{Color.RESET}")

    print(f"\n{Color.CIAN}¿Cómo quieres ejecutar?{Color.RESET}")
    print(f"{Color.ROJO}1.{Color.RESET} Modo terminal (10 comandos)")
    print(f"{Color.ROJO}2.{Color.RESET} Modo web directo")

    modo = input(f"\n{Color.ROJO}➤ Elige: {Color.RESET}")

    if modo == '2':
        cprint(f"\n🌐 Servidor web: http://localhost:{PUERTO}", 'verde', negrita=True)
        cprint(f"   Presiona Ctrl+C para detener", 'gris')
        app.run(host='0.0.0.0', port=PUERTO, debug=True)
    else:
        menu()