from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime
from sqlalchemy import or_
from utils.report_generator import ReportGenerator
import os
import json

app = Flask(__name__)

# Configuración de la base de datos
if os.environ.get('RENDER'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/cadastro.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cadastro.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

# Configuración de la sesión
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db = SQLAlchemy(app)

# Crear directorio para informes si no existe
if not os.path.exists('static/reports'):
    os.makedirs('static/reports')

class ACS(db.Model):
    __tablename__ = 'acs'  # Definir explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cns = db.Column(db.String(20), unique=True, nullable=False)
    cbo = db.Column(db.String(20), nullable=False)
    cnes = db.Column(db.String(20), nullable=False)
    ine = db.Column(db.String(20), nullable=False)
    unidade_saude = db.Column(db.String(100), nullable=False)
    microareas = db.Column(db.String(100), nullable=False)  # Lista de microáreas separadas por coma
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class Ciudadano(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cns_cpf = db.Column(db.String(20), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    nombre_social = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.DateTime, nullable=False)
    sexo = db.Column(db.String(1), nullable=False)
    raza_color = db.Column(db.String(20), nullable=False)
    etnia = db.Column(db.String(50))
    nis_pis_pasep = db.Column(db.String(20))
    nombre_madre = db.Column(db.String(100), nullable=False)
    nombre_padre = db.Column(db.String(100))
    nacionalidad = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    microarea = db.Column(db.String(10), nullable=False)
    es_responsable_familiar = db.Column(db.Boolean, default=False)
    escolaridad = db.Column(db.String(50))
    situacion_trabajo = db.Column(db.String(50))
    gestante = db.Column(db.Boolean, default=False)
    hipertension = db.Column(db.Boolean, default=False)
    diabetes = db.Column(db.Boolean, default=False)
    cancer = db.Column(db.Boolean, default=False)
    fumante = db.Column(db.Boolean, default=False)
    alcohol = db.Column(db.Boolean, default=False)
    otras_drogas = db.Column(db.Boolean, default=False)
    situacion_calle = db.Column(db.Boolean, default=False)
    cns_profesional = db.Column(db.String(20), nullable=False)
    cbo = db.Column(db.String(20), nullable=False)
    cnes = db.Column(db.String(20), nullable=False)
    ine = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class CadastroDomiciliar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cnes = db.Column(db.String(20), nullable=False)
    ine = db.Column(db.String(20), nullable=False)
    microarea = db.Column(db.String(10), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    prontuario_familiar = db.Column(db.String(20), nullable=False)
    tipo_logradouro = db.Column(db.String(20))
    nombre_logradouro = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    complemento = db.Column(db.String(50))
    barrio = db.Column(db.String(50), nullable=False)
    municipio = db.Column(db.String(50), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    telefono_residencial = db.Column(db.String(20))
    telefono_referencia = db.Column(db.String(20))
    tiene_animales = db.Column(db.Boolean, default=False)
    cantidad_animales = db.Column(db.Integer)
    tipo_animal_gato = db.Column(db.Boolean, default=False)
    tipo_animal_perro = db.Column(db.Boolean, default=False)
    tipo_animal_pajaro = db.Column(db.Boolean, default=False)
    tipo_animal_otro = db.Column(db.Boolean, default=False)
    otro_animal_especificar = db.Column(db.String(50))
    tipo_domicilio = db.Column(db.String(20), nullable=False)
    numero_moradores = db.Column(db.Integer, nullable=False)
    numero_comodos = db.Column(db.Integer)
    energia_electrica = db.Column(db.Boolean, default=True)
    cartao_sus_profesional = db.Column(db.String(20), nullable=False)

class VisitaDomiciliar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    turno = db.Column(db.String(1), nullable=False)  # M, T, N
    microarea = db.Column(db.String(10), nullable=False)
    tipo_inmueble = db.Column(db.String(2), nullable=False)
    tipo_inmueble_otro = db.Column(db.String(100))
    
    # Datos del ciudadano
    cns_ciudadano = db.Column(db.String(20), db.ForeignKey('ciudadano.cns_cpf'), nullable=False)
    ciudadano = db.relationship('Ciudadano', backref=db.backref('visitas', lazy=True))
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(1))
    
    # Motivos de la visita
    cadastramento_atualizacao = db.Column(db.Boolean, default=False)
    visita_periodica = db.Column(db.Boolean, default=False)
    busca_ativa = db.Column(db.Boolean, default=False)
    convite_atividades = db.Column(db.Boolean, default=False)
    orientacao_prevencao = db.Column(db.Boolean, default=False)
    
    # Acompañamiento
    gestante = db.Column(db.Boolean, default=False)
    puerpera = db.Column(db.Boolean, default=False)
    recem_nascido = db.Column(db.Boolean, default=False)
    crianca = db.Column(db.Boolean, default=False)
    pessoa_desnutricao = db.Column(db.Boolean, default=False)
    pessoa_reabilitacao = db.Column(db.Boolean, default=False)
    pessoa_hipertensao = db.Column(db.Boolean, default=False)
    pessoa_diabetes = db.Column(db.Boolean, default=False)
    pessoa_asma = db.Column(db.Boolean, default=False)
    pessoa_dpoc = db.Column(db.Boolean, default=False)
    pessoa_cancer = db.Column(db.Boolean, default=False)
    pessoa_outras = db.Column(db.Boolean, default=False)
    
    # Control ambiental/vectorial
    egresso_internacao = db.Column(db.Boolean, default=False)
    convivente_hanseniase = db.Column(db.Boolean, default=False)
    convivente_tuberculose = db.Column(db.Boolean, default=False)
    sintomatico_respiratorio = db.Column(db.Boolean, default=False)
    tabagista = db.Column(db.Boolean, default=False)
    domiciliados_acamados = db.Column(db.Boolean, default=False)
    vulnerabilidade_social = db.Column(db.Boolean, default=False)
    condicionalidades_bolsa_familia = db.Column(db.Boolean, default=False)
    saude_mental = db.Column(db.Boolean, default=False)
    usuario_alcool = db.Column(db.Boolean, default=False)
    usuario_drogas = db.Column(db.Boolean, default=False)
    
    # Datos antropométricos
    peso = db.Column(db.Float)
    altura = db.Column(db.Integer)
    
    # Resultado de la visita
    resultado_visita = db.Column(db.String(2), nullable=False)  # 01=Realizada, 02=Recusada, 03=Ausente
    visita_compartida = db.Column(db.Boolean, default=False)
    
    # Datos del profesional
    cns_profesional = db.Column(db.String(20), db.ForeignKey('acs.cns'), nullable=False)
    acs = db.relationship('ACS', backref=db.backref('visitas', lazy=True))
    cbo = db.Column(db.String(20), nullable=False)
    cnes = db.Column(db.String(20), nullable=False)
    ine = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<VisitaDomiciliar {self.id}>'

class ActividadColectiva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cnes = db.Column(db.String(20), nullable=False)
    ine = db.Column(db.String(20), nullable=False)
    fecha_actividad = db.Column(db.DateTime, nullable=False)
    turno = db.Column(db.String(1), nullable=False)
    numero_hoja = db.Column(db.String(10))
    tipo_actividad = db.Column(db.String(2), nullable=False)
    otro_tipo_actividad = db.Column(db.String(50))
    publico_comunidad = db.Column(db.Boolean, default=False)
    publico_gestantes = db.Column(db.Boolean, default=False)
    publico_mujeres = db.Column(db.Boolean, default=False)
    tema_alimentacion = db.Column(db.Boolean, default=False)
    tema_autocuidado = db.Column(db.Boolean, default=False)
    practica_antropometria = db.Column(db.Boolean, default=False)
    practica_corporal = db.Column(db.Boolean, default=False)
    cns_profesional = db.Column(db.String(20), nullable=False)
    cbo = db.Column(db.String(20), nullable=False)
    cnes_profesional = db.Column(db.String(20), nullable=False)
    ine_profesional = db.Column(db.String(20), nullable=False)
    cantidad_participantes = db.Column(db.Integer, nullable=False)
    evaluaciones_alteradas = db.Column(db.Integer, default=0)

def get_acs_actual():
    acs_id = session.get('acs_id')
    if acs_id:
        return ACS.query.get(acs_id)
    return None

@app.route('/')
def index():
    # Obtener todos los ACS activos
    acs_list = ACS.query.filter_by(activo=True).order_by(ACS.nombre).all()
    
    # Si solo hay un ACS, seleccionarlo automáticamente
    if len(acs_list) == 1 and not session.get('acs_id'):
        session['acs_id'] = acs_list[0].id
        flash(f'ACS {acs_list[0].nombre} selecionado automaticamente!', 'success')
    
    # Obtener el ACS actual de la sesión
    acs_actual_id = session.get('acs_id')
    acs_actual = ACS.query.get(acs_actual_id) if acs_actual_id else None
    
    return render_template('index.html', 
                         acs_list=acs_list,
                         acs_actual=acs_actual,
                         acs_actual_id=acs_actual_id)

@app.route('/seleccionar_acs', methods=['POST'])
def seleccionar_acs():
    acs_id = request.form.get('acs_id')
    if acs_id:
        session['acs_id'] = int(acs_id)
        acs = ACS.query.get(acs_id)
        if acs:
            flash(f'ACS {acs.nombre} selecionado com sucesso!', 'success')
        else:
            flash('ACS não encontrado.', 'error')
    else:
        session.pop('acs_id', None)
        flash('Nenhum ACS selecionado.', 'warning')
    
    return redirect(url_for('index'))

@app.route('/acs')
def listar_acs():
    acs_list = ACS.query.order_by(ACS.nombre).all()
    return render_template('listar_acs.html', acs_list=acs_list)

@app.route('/acs/registrar', methods=['GET', 'POST'])
def registrar_acs():
    if request.method == 'POST':
        nuevo_acs = ACS(
            nombre=request.form['nombre'],
            cns=request.form['cns'],
            cbo=request.form['cbo'],
            cnes=request.form['cnes'],
            ine=request.form['ine'],
            unidade_saude=request.form['unidade_saude'],
            microareas=request.form['microareas'],
            activo=True
        )
        
        try:
            db.session.add(nuevo_acs)
            db.session.commit()
            flash('ACS registrado com sucesso!', 'success')
            return redirect(url_for('listar_acs'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar ACS. Verifique se o CNS já está cadastrado.', 'error')
            return render_template('registrar_acs.html')
            
    return render_template('registrar_acs.html')

@app.route('/acs/editar/<int:id>', methods=['GET', 'POST'])
def editar_acs(id):
    acs = ACS.query.get_or_404(id)
    
    if request.method == 'POST':
        acs.nombre = request.form['nombre']
        acs.cns = request.form['cns']
        acs.cbo = request.form['cbo']
        acs.cnes = request.form['cnes']
        acs.ine = request.form['ine']
        acs.unidade_saude = request.form['unidade_saude']
        acs.microareas = request.form['microareas']
        acs.activo = 'activo' in request.form
        
        try:
            db.session.commit()
            flash('ACS atualizado com sucesso!', 'success')
            return redirect(url_for('listar_acs'))
        except:
            db.session.rollback()
            flash('Erro ao atualizar ACS.', 'error')
            
    return render_template('editar_acs.html', acs=acs)

@app.route('/acs/eliminar/<int:id>', methods=['POST'])
def eliminar_acs(id):
    acs = ACS.query.get_or_404(id)
    try:
        db.session.delete(acs)
        db.session.commit()
        flash('ACS eliminado com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao eliminar ACS.', 'error')
    return redirect(url_for('listar_acs'))

@app.route('/cadastro', methods=['GET', 'POST'])
@app.route('/cadastro/<int:id>', methods=['GET', 'POST'])
def cadastro(id=None):
    acs_actual = get_acs_actual()
    if not acs_actual:
        flash('Por favor, seleccione um ACS primeiro.', 'warning')
        return redirect(url_for('index'))

    # Si hay un ID, estamos editando
    if id:
        cadastro = Ciudadano.query.get_or_404(id)
    else:
        cadastro = None

    if request.method == 'POST':
        try:
            # Si estamos editando, usamos el objeto existente
            if id:
                cadastro = Ciudadano.query.get_or_404(id)
            else:
                cadastro = Ciudadano()

            # Actualizar los campos del cadastro
            cadastro.cns_cpf = request.form['cns_cpf']
            cadastro.nombre_completo = request.form['nombre_completo']
            cadastro.nombre_social = request.form.get('nombre_social')
            cadastro.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d')
            cadastro.sexo = request.form['sexo']
            cadastro.raza_color = request.form['raza_color']
            cadastro.etnia = request.form.get('etnia')
            cadastro.nis_pis_pasep = request.form.get('nis_pis_pasep')
            cadastro.nombre_madre = request.form['nombre_madre']
            cadastro.nombre_padre = request.form.get('nombre_padre')
            cadastro.nacionalidad = request.form.get('nacionalidad')
            cadastro.telefono = request.form.get('telefono')
            cadastro.email = request.form.get('email')
            cadastro.microarea = request.form.get('microarea')
            cadastro.es_responsable_familiar = 'es_responsable_familiar' in request.form
            cadastro.escolaridad = request.form.get('escolaridad')
            cadastro.situacion_trabajo = request.form.get('situacion_trabajo')
            cadastro.gestante = 'gestante' in request.form
            cadastro.hipertension = 'hipertension' in request.form
            cadastro.diabetes = 'diabetes' in request.form
            cadastro.cancer = 'cancer' in request.form
            cadastro.fumante = 'fumante' in request.form
            cadastro.alcohol = 'alcohol' in request.form
            cadastro.otras_drogas = 'otras_drogas' in request.form
            cadastro.situacion_calle = 'situacion_calle' in request.form
            cadastro.cns_profesional = acs_actual.cns
            cadastro.cbo = acs_actual.cbo
            cadastro.cnes = acs_actual.cnes
            cadastro.ine = acs_actual.ine
            cadastro.fecha_registro = datetime.strptime(request.form['fecha_registro'], '%Y-%m-%d')

            if not id:  # Solo si es un nuevo registro
                db.session.add(cadastro)
            
            db.session.commit()
            flash('Cadastro {} com sucesso!'.format('atualizado' if id else 'realizado'), 'success')
            return redirect(url_for('listar_cadastros'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao {} o cadastro: {}'.format('atualizar' if id else 'realizar', str(e)), 'danger')

    return render_template('cadastro.html', cadastro=cadastro, acs=acs_actual, now=datetime.now())

@app.route('/listar_cadastros')
def listar_cadastros():
    acs_actual = get_acs_actual()
    if not acs_actual:
        flash('Por favor, selecione um ACS primeiro.', 'warning')
        return redirect(url_for('index'))
    
    page = request.args.get('pagina', 1, type=int)
    per_page = 10
    microareas = acs_actual.microareas.split(',')
    
    cadastros = Ciudadano.query.filter(Ciudadano.microarea.in_(microareas))\
        .order_by(Ciudadano.nombre_completo)\
        .paginate(page=page, per_page=per_page)
    
    return render_template('listar_cadastros.html', 
                         acs=acs_actual,
                         cadastros=cadastros,
                         microareas=microareas)

@app.route('/cadastro_domiciliar', methods=['GET', 'POST'])
@app.route('/cadastro_domiciliar/<int:id>', methods=['GET', 'POST'])
def cadastro_domiciliar(id=None):
    acs_actual = get_acs_actual()
    if not acs_actual:
        flash('Por favor, seleccione um ACS primeiro.', 'warning')
        return redirect(url_for('index'))

    # Si hay un ID, estamos editando
    if id:
        cadastro = CadastroDomiciliar.query.get_or_404(id)
    else:
        cadastro = None

    if request.method == 'POST':
        try:
            # Si estamos editando, usamos el objeto existente
            if id:
                cadastro = CadastroDomiciliar.query.get_or_404(id)
            else:
                cadastro = CadastroDomiciliar()
            
            # Datos de identificación
            cadastro.cnes = request.form['cnes']
            cadastro.ine = request.form['ine']
            cadastro.microarea = request.form['microarea']
            cadastro.fecha_registro = datetime.strptime(request.form['fecha_registro'], '%Y-%m-%d')
            cadastro.prontuario_familiar = request.form['prontuario_familiar']
            
            # Dirección
            cadastro.tipo_logradouro = request.form['tipo_logradouro']
            cadastro.nombre_logradouro = request.form['nombre_logradouro']
            cadastro.numero = request.form['numero']
            cadastro.complemento = request.form.get('complemento')
            cadastro.barrio = request.form['barrio']
            cadastro.municipio = request.form['municipio']
            cadastro.uf = request.form['uf']
            cadastro.cep = request.form['cep']
            
            # Contacto
            cadastro.telefono_residencial = request.form.get('telefono_residencial')
            cadastro.telefono_referencia = request.form.get('telefono_referencia')
            
            # Animales
            cadastro.tiene_animales = 'tiene_animales' in request.form
            cadastro.cantidad_animales = int(request.form['cantidad_animales']) if request.form.get('cantidad_animales') else None
            cadastro.tipo_animal_gato = 'tipo_animal_gato' in request.form
            cadastro.tipo_animal_perro = 'tipo_animal_perro' in request.form
            cadastro.tipo_animal_pajaro = 'tipo_animal_pajaro' in request.form
            cadastro.tipo_animal_otro = 'tipo_animal_otro' in request.form
            cadastro.otro_animal_especificar = request.form.get('otro_animal_especificar')
            
            # Características del domicilio
            cadastro.tipo_domicilio = request.form['tipo_domicilio']
            cadastro.numero_moradores = int(request.form['numero_moradores'])
            cadastro.numero_comodos = int(request.form['numero_comodos']) if request.form.get('numero_comodos') else None
            cadastro.energia_electrica = 'energia_electrica' in request.form
            
            # Datos del profesional
            cadastro.cartao_sus_profesional = acs_actual.cns
            
            if not id:  # Solo si es un nuevo registro
                db.session.add(cadastro)
            
            db.session.commit()
            flash('Cadastro domiciliar {} com sucesso!'.format('atualizado' if id else 'registrado'), 'success')
            return redirect(url_for('listar_cadastros_domiciliares'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao {} o cadastro domiciliar: {}'.format('atualizar' if id else 'registrar', str(e)), 'danger')
    
    return render_template('cadastro_domiciliar.html', cadastro=cadastro, acs=acs_actual, now=datetime.now())

@app.route('/listar_cadastros_domiciliares')
def listar_cadastros_domiciliares():
    acs_actual = get_acs_actual()
    if not acs_actual:
        flash('Por favor, selecione um ACS primeiro.', 'warning')
        return redirect(url_for('index'))
    
    page = request.args.get('pagina', 1, type=int)
    per_page = 10
    microareas = acs_actual.microareas.split(',')
    
    cadastros = CadastroDomiciliar.query.filter(CadastroDomiciliar.microarea.in_(microareas))\
        .order_by(CadastroDomiciliar.prontuario_familiar)\
        .paginate(page=page, per_page=per_page)
    
    return render_template('listar_cadastros_domiciliares.html', 
                         acs=acs_actual,
                         cadastros=cadastros,
                         microareas=microareas)

@app.route('/visita_domiciliar', methods=['GET', 'POST'])
@app.route('/visita_domiciliar/<int:id>', methods=['GET', 'POST'])
def visita_domiciliar(id=None):
    acs = get_acs_actual()
    if not acs:
        flash('Por favor, seleccione un ACS primero', 'warning')
        return redirect(url_for('index'))
    
    visita = None
    if id:
        visita = VisitaDomiciliar.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            if not visita:
                visita = VisitaDomiciliar()
            
            # Datos básicos
            visita.fecha_registro = datetime.strptime(request.form['fecha_registro'], '%Y-%m-%d')
            visita.turno = request.form['turno']
            visita.microarea = request.form['microarea']
            visita.tipo_inmueble = request.form['tipo_inmueble']
            if visita.tipo_inmueble == '99':
                visita.tipo_inmueble_otro = request.form.get('tipo_inmueble_otro')
            
            # Datos del ciudadano
            visita.cns_ciudadano = request.form['cns_ciudadano']
            visita.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d')
            visita.sexo = request.form['sexo']
            
            # Motivos de la visita
            visita.cadastramento_atualizacao = 'cadastramento_atualizacao' in request.form
            visita.visita_periodica = 'visita_periodica' in request.form
            visita.busca_ativa = 'busca_ativa' in request.form
            visita.convite_atividades = 'convite_atividades' in request.form
            visita.orientacao_prevencao = 'orientacao_prevencao' in request.form
            
            # Acompañamiento
            visita.gestante = 'gestante' in request.form
            visita.puerpera = 'puerpera' in request.form
            visita.recem_nascido = 'recem_nascido' in request.form
            visita.crianca = 'crianca' in request.form
            visita.pessoa_desnutricao = 'pessoa_desnutricao' in request.form
            visita.pessoa_reabilitacao = 'pessoa_reabilitacao' in request.form
            visita.pessoa_hipertensao = 'pessoa_hipertensao' in request.form
            visita.pessoa_diabetes = 'pessoa_diabetes' in request.form
            visita.pessoa_asma = 'pessoa_asma' in request.form
            visita.pessoa_dpoc = 'pessoa_dpoc' in request.form
            visita.pessoa_cancer = 'pessoa_cancer' in request.form
            visita.pessoa_outras = 'pessoa_outras' in request.form
            
            # Control ambiental/vectorial
            visita.egresso_internacao = 'egresso_internacao' in request.form
            visita.convivente_hanseniase = 'convivente_hanseniase' in request.form
            visita.convivente_tuberculose = 'convivente_tuberculose' in request.form
            visita.sintomatico_respiratorio = 'sintomatico_respiratorio' in request.form
            visita.tabagista = 'tabagista' in request.form
            visita.domiciliados_acamados = 'domiciliados_acamados' in request.form
            visita.vulnerabilidade_social = 'vulnerabilidade_social' in request.form
            visita.condicionalidades_bolsa_familia = 'condicionalidades_bolsa_familia' in request.form
            visita.saude_mental = 'saude_mental' in request.form
            visita.usuario_alcool = 'usuario_alcool' in request.form
            visita.usuario_drogas = 'usuario_drogas' in request.form
            
            # Datos antropométricos
            if request.form.get('peso'):
                visita.peso = float(request.form['peso'])
            if request.form.get('altura'):
                visita.altura = int(request.form['altura'])
            
            # Resultado de la visita
            visita.resultado_visita = request.form['resultado_visita']
            visita.visita_compartida = 'visita_compartida' in request.form
            
            # Datos del profesional
            visita.cns_profesional = acs.cns
            visita.cbo = acs.cbo
            visita.cnes = acs.cnes
            visita.ine = acs.ine
            
            if not id:
                db.session.add(visita)
            
            db.session.commit()
            flash('Visita guardada con éxito', 'success')
            return redirect(url_for('listar_visitas_domiciliares'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la visita: {str(e)}', 'danger')
    
    return render_template('visita_domiciliar.html', visita=visita, acs=acs, now=datetime.now())

@app.route('/ver_visita_domiciliar/<int:id>')
def ver_visita_domiciliar(id):
    visita = VisitaDomiciliar.query.get_or_404(id)
    return render_template('ver_visita_domiciliar.html', visita=visita)

@app.route('/editar_visita_domiciliar/<int:id>', methods=['GET', 'POST'])
def editar_visita_domiciliar(id):
    acs = get_acs_actual()
    if not acs:
        flash('Por favor, seleccione un ACS primero', 'warning')
        return redirect(url_for('index'))
    
    visita = VisitaDomiciliar.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Datos básicos
            visita.fecha_registro = datetime.strptime(request.form['fecha_registro'], '%Y-%m-%d')
            visita.turno = request.form['turno']
            visita.microarea = request.form['microarea']
            visita.tipo_inmueble = request.form['tipo_inmueble']
            if visita.tipo_inmueble == '99':
                visita.tipo_inmueble_otro = request.form.get('tipo_inmueble_otro')
            
            # Datos del ciudadano
            visita.cns_ciudadano = request.form['cns_ciudadano']
            visita.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d')
            visita.sexo = request.form['sexo']
            
            # Motivos de la visita
            visita.cadastramento_atualizacao = 'cadastramento_atualizacao' in request.form
            visita.visita_periodica = 'visita_periodica' in request.form
            visita.busca_ativa = 'busca_ativa' in request.form
            visita.convite_atividades = 'convite_atividades' in request.form
            visita.orientacao_prevencao = 'orientacao_prevencao' in request.form
            
            # Acompañamiento
            visita.gestante = 'gestante' in request.form
            visita.puerpera = 'puerpera' in request.form
            visita.recem_nascido = 'recem_nascido' in request.form
            visita.crianca = 'crianca' in request.form
            visita.pessoa_desnutricao = 'pessoa_desnutricao' in request.form
            visita.pessoa_reabilitacao = 'pessoa_reabilitacao' in request.form
            visita.pessoa_hipertensao = 'pessoa_hipertensao' in request.form
            visita.pessoa_diabetes = 'pessoa_diabetes' in request.form
            visita.pessoa_asma = 'pessoa_asma' in request.form
            visita.pessoa_dpoc = 'pessoa_dpoc' in request.form
            visita.pessoa_cancer = 'pessoa_cancer' in request.form
            visita.pessoa_outras = 'pessoa_outras' in request.form
            
            # Control ambiental/vectorial
            visita.egresso_internacao = 'egresso_internacao' in request.form
            visita.convivente_hanseniase = 'convivente_hanseniase' in request.form
            visita.convivente_tuberculose = 'convivente_tuberculose' in request.form
            visita.sintomatico_respiratorio = 'sintomatico_respiratorio' in request.form
            visita.tabagista = 'tabagista' in request.form
            visita.domiciliados_acamados = 'domiciliados_acamados' in request.form
            visita.vulnerabilidade_social = 'vulnerabilidade_social' in request.form
            visita.condicionalidades_bolsa_familia = 'condicionalidades_bolsa_familia' in request.form
            visita.saude_mental = 'saude_mental' in request.form
            visita.usuario_alcool = 'usuario_alcool' in request.form
            visita.usuario_drogas = 'usuario_drogas' in request.form
            
            # Datos antropométricos
            if request.form.get('peso'):
                visita.peso = float(request.form['peso'])
            if request.form.get('altura'):
                visita.altura = int(request.form['altura'])
            
            # Resultado de la visita
            visita.resultado_visita = request.form['resultado_visita']
            visita.visita_compartida = 'visita_compartida' in request.form
            
            db.session.commit()
            flash('Visita actualizada con éxito', 'success')
            return redirect(url_for('ver_visita_domiciliar', id=visita.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la visita: {str(e)}', 'danger')
    
    return render_template('visita_domiciliar.html', visita=visita, acs=acs, now=datetime.now(), editar=True)

@app.route('/eliminar_visita_domiciliar/<int:id>', methods=['POST'])
def eliminar_visita_domiciliar(id):
    visita = VisitaDomiciliar.query.get_or_404(id)
    try:
        db.session.delete(visita)
        db.session.commit()
        flash('Visita eliminada con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la visita: {str(e)}', 'danger')
    return redirect(url_for('listar_visitas_domiciliares'))

@app.route('/listar_visitas_domiciliares')
def listar_visitas_domiciliares():
    acs = get_acs_actual()
    if not acs:
        flash('Por favor, seleccione un ACS primero', 'warning')
        return redirect(url_for('index'))
    
    page = request.args.get('pagina', 1, type=int)
    per_page = 10
    
    # Filtros
    buscar = request.args.get('buscar', '')
    microarea = request.args.get('microarea', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    
    query = VisitaDomiciliar.query.filter_by(cns_profesional=acs.cns)
    
    if buscar:
        query = query.join(Ciudadano).filter(
            or_(
                Ciudadano.nombre_completo.ilike(f'%{buscar}%'),
                Ciudadano.cns_cpf.ilike(f'%{buscar}%')
            )
        )
    
    if microarea:
        query = query.filter(VisitaDomiciliar.microarea == microarea)
    
    if fecha_inicio:
        query = query.filter(VisitaDomiciliar.fecha_registro >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    
    if fecha_fin:
        query = query.filter(VisitaDomiciliar.fecha_registro <= datetime.strptime(fecha_fin, '%Y-%m-%d'))
    
    # Ordenamiento
    ordenar = request.args.get('ordenar', 'fecha_registro')
    direccion = request.args.get('direccion', 'desc')
    
    if ordenar == 'fecha_registro':
        if direccion == 'asc':
            query = query.order_by(VisitaDomiciliar.fecha_registro.asc())
        else:
            query = query.order_by(VisitaDomiciliar.fecha_registro.desc())
    
    visitas = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Obtener las microáreas del ACS actual
    microareas = acs.microareas.split(',')
    
    return render_template('listar_visitas_domiciliares.html', 
                         visitas=visitas,
                         microareas=microareas,
                         buscar=buscar,
                         microarea_seleccionada=microarea,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin)

@app.route('/actividad_colectiva', methods=['GET', 'POST'])
@app.route('/actividad_colectiva/<int:id>', methods=['GET', 'POST'])
def actividad_colectiva(id=None):
    acs_actual = get_acs_actual()
    if not acs_actual:
        flash('Por favor, seleccione um ACS primeiro.', 'warning')
        return redirect(url_for('index'))

    # Si hay un ID, estamos editando
    if id:
        actividad = ActividadColectiva.query.get_or_404(id)
    else:
        actividad = None

    if request.method == 'POST':
        try:
            # Si estamos editando, usamos el objeto existente
            if id:
                actividad = ActividadColectiva.query.get_or_404(id)
            else:
                actividad = ActividadColectiva()
            
            # Datos básicos
            actividad.cnes = request.form['cnes']
            actividad.ine = request.form['ine']
            actividad.fecha_actividad = datetime.strptime(request.form['fecha_actividad'], '%Y-%m-%d')
            actividad.turno = request.form['turno']
            actividad.numero_hoja = request.form['numero_hoja']
            actividad.tipo_actividad = request.form['tipo_actividad']
            actividad.otro_tipo_actividad = request.form.get('otro_tipo_actividad')
            
            # Público objetivo
            actividad.publico_comunidad = 'publico_comunidad' in request.form
            actividad.publico_gestantes = 'publico_gestantes' in request.form
            actividad.publico_mujeres = 'publico_mujeres' in request.form
            
            # Temas y prácticas
            actividad.tema_alimentacion = 'tema_alimentacion' in request.form
            actividad.tema_autocuidado = 'tema_autocuidado' in request.form
            actividad.practica_antropometria = 'practica_antropometria' in request.form
            actividad.practica_corporal = 'practica_corporal' in request.form
            
            # Datos del profesional
            actividad.cns_profesional = acs_actual.cns
            actividad.cbo = acs_actual.cbo
            actividad.cnes_profesional = acs_actual.cnes
            actividad.ine_profesional = acs_actual.ine
            
            # Resultados
            actividad.cantidad_participantes = int(request.form['cantidad_participantes'])
            actividad.evaluaciones_alteradas = int(request.form.get('evaluaciones_alteradas', 0))
            
            if not id:  # Solo si es un nuevo registro
                db.session.add(actividad)
            
            db.session.commit()
            flash('Atividade coletiva {} com sucesso!'.format('atualizada' if id else 'registrada'), 'success')
            return redirect(url_for('listar_actividades_colectivas'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao {} a atividade coletiva: {}'.format('atualizar' if id else 'registrar', str(e)), 'danger')
    
    return render_template('actividad_colectiva.html', actividad=actividad, acs=acs_actual, now=datetime.now())

@app.route('/listar_actividades_colectivas')
def listar_actividades_colectivas():
    acs_actual = get_acs_actual()
    if not acs_actual:
        flash('Por favor, selecione um ACS primeiro.', 'warning')
        return redirect(url_for('index'))
    
    actividades = ActividadColectiva.query.order_by(ActividadColectiva.fecha_actividad.desc()).all()
    
    return render_template('listar_actividades_colectivas.html', 
                         acs=acs_actual,
                         actividades=actividades)

@app.route('/ver_cadastro/<int:id>')
def ver_cadastro(id):
    cadastro = Ciudadano.query.get_or_404(id)
    return render_template('ver_cadastro.html', cadastro=cadastro)

@app.route('/editar_cadastro/<int:id>', methods=['GET', 'POST'])
def editar_cadastro(id):
    cadastro = Ciudadano.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Datos personales
            cadastro.cns_cpf = request.form['cns_cpf']
            cadastro.nombre_completo = request.form['nombre_completo']
            cadastro.nombre_social = request.form['nombre_social']
            cadastro.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d')
            cadastro.sexo = request.form['sexo']
            cadastro.raza_color = request.form['raza_color']
            cadastro.etnia = request.form['etnia']
            cadastro.nis_pis_pasep = request.form['nis_pis_pasep']
            cadastro.nombre_madre = request.form['nombre_madre']
            cadastro.nombre_padre = request.form['nombre_padre']
            cadastro.nacionalidad = request.form['nacionalidad']
            cadastro.telefono = request.form['telefono']
            cadastro.email = request.form['email']
            cadastro.microarea = request.form['microarea']
            
            # Datos socioeconómicos
            cadastro.es_responsable_familiar = 'es_responsable_familiar' in request.form
            cadastro.escolaridad = request.form['escolaridad']
            cadastro.situacion_trabajo = request.form['situacion_trabajo']
            
            # Condiciones de salud
            cadastro.gestante = 'gestante' in request.form
            cadastro.hipertension = 'hipertension' in request.form
            cadastro.diabetes = 'diabetes' in request.form
            cadastro.cancer = 'cancer' in request.form
            cadastro.fumante = 'fumante' in request.form
            cadastro.alcohol = 'alcohol' in request.form
            cadastro.otras_drogas = 'otras_drogas' in request.form
            cadastro.situacion_calle = 'situacion_calle' in request.form
            
            # Datos del profesional
            cadastro.cns_profesional = request.form['cns_profesional']
            cadastro.cbo = request.form['cbo']
            cadastro.cnes = request.form['cnes']
            cadastro.ine = request.form['ine']
            
            db.session.commit()
            flash('Cadastro atualizado com sucesso!', 'success')
            return redirect(url_for('listar_cadastros'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cadastro: {str(e)}', 'error')
    return render_template('editar_cadastro.html', cadastro=cadastro)

@app.route('/eliminar_cadastro/<int:id>', methods=['POST'])
def eliminar_cadastro(id):
    cadastro = Ciudadano.query.get_or_404(id)
    try:
        db.session.delete(cadastro)
        db.session.commit()
        flash('Cadastro eliminado com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao eliminar cadastro.', 'error')
    return redirect(url_for('listar_cadastros'))

@app.route('/ver_cadastro_domiciliar/<int:id>')
def ver_cadastro_domiciliar(id):
    cadastro = CadastroDomiciliar.query.get_or_404(id)
    return render_template('ver_cadastro_domiciliar.html', cadastro=cadastro)

@app.route('/editar_cadastro_domiciliar/<int:id>', methods=['GET', 'POST'])
def editar_cadastro_domiciliar(id):
    cadastro = CadastroDomiciliar.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Datos de identificación
            cadastro.cnes = request.form['cnes']
            cadastro.ine = request.form['ine']
            cadastro.microarea = request.form['microarea']
            cadastro.fecha_registro = datetime.strptime(request.form['fecha_registro'], '%Y-%m-%d')
            cadastro.prontuario_familiar = request.form['prontuario_familiar']
            
            # Dirección
            cadastro.tipo_logradouro = request.form['tipo_logradouro']
            cadastro.nombre_logradouro = request.form['nombre_logradouro']
            cadastro.numero = request.form['numero']
            cadastro.complemento = request.form['complemento']
            cadastro.barrio = request.form['barrio']
            cadastro.municipio = request.form['municipio']
            cadastro.uf = request.form['uf']
            cadastro.cep = request.form['cep']
            
            # Contacto
            cadastro.telefono_residencial = request.form['telefono_residencial']
            cadastro.telefono_referencia = request.form['telefono_referencia']
            
            # Animales
            cadastro.tiene_animales = 'tiene_animales' in request.form
            cadastro.cantidad_animales = int(request.form['cantidad_animales']) if request.form.get('cantidad_animales') else None
            cadastro.tipo_animal_gato = 'tipo_animal_gato' in request.form
            cadastro.tipo_animal_perro = 'tipo_animal_perro' in request.form
            cadastro.tipo_animal_pajaro = 'tipo_animal_pajaro' in request.form
            cadastro.tipo_animal_otro = 'tipo_animal_otro' in request.form
            cadastro.otro_animal_especificar = request.form.get('otro_animal_especificar')
            
            # Características del domicilio
            cadastro.tipo_domicilio = request.form['tipo_domicilio']
            cadastro.numero_moradores = int(request.form['numero_moradores'])
            cadastro.numero_comodos = int(request.form['numero_comodos']) if request.form.get('numero_comodos') else None
            cadastro.energia_electrica = 'energia_electrica' in request.form
            
            # Datos del profesional
            cadastro.cartao_sus_profesional = request.form['cartao_sus_profesional']
            
            db.session.commit()
            flash('Cadastro domiciliar atualizado com sucesso!', 'success')
            return redirect(url_for('listar_cadastros_domiciliares'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cadastro domiciliar: {str(e)}', 'error')
    return render_template('editar_cadastro_domiciliar.html', cadastro=cadastro)

@app.route('/eliminar_cadastro_domiciliar/<int:id>', methods=['POST'])
def eliminar_cadastro_domiciliar(id):
    cadastro = CadastroDomiciliar.query.get_or_404(id)
    try:
        db.session.delete(cadastro)
        db.session.commit()
        flash('Cadastro domiciliar eliminado com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao eliminar cadastro domiciliar.', 'error')
    return redirect(url_for('listar_cadastros_domiciliares'))

@app.route('/eliminar_actividad_colectiva/<int:id>', methods=['POST'])
def eliminar_actividad_colectiva(id):
    actividad = ActividadColectiva.query.get_or_404(id)
    try:
        db.session.delete(actividad)
        db.session.commit()
        flash('Atividade coletiva eliminada com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao eliminar atividade coletiva.', 'error')
    return redirect(url_for('listar_actividades_colectivas'))

@app.route('/editar_actividad_colectiva/<int:id>', methods=['GET', 'POST'])
def editar_actividad_colectiva(id):
    actividad = ActividadColectiva.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Datos básicos
            actividad.cnes = request.form['cnes']
            actividad.ine = request.form['ine']
            actividad.fecha_actividad = datetime.strptime(request.form['fecha_actividad'], '%Y-%m-%d')
            actividad.turno = request.form['turno']
            actividad.numero_hoja = request.form['numero_hoja']
            actividad.tipo_actividad = request.form['tipo_actividad']
            actividad.otro_tipo_actividad = request.form.get('otro_tipo_actividad')
            
            # Público objetivo
            actividad.publico_comunidad = 'publico_comunidad' in request.form
            actividad.publico_gestantes = 'publico_gestantes' in request.form
            actividad.publico_mujeres = 'publico_mujeres' in request.form
            
            # Temas y prácticas
            actividad.tema_alimentacion = 'tema_alimentacion' in request.form
            actividad.tema_autocuidado = 'tema_autocuidado' in request.form
            actividad.practica_antropometria = 'practica_antropometria' in request.form
            actividad.practica_corporal = 'practica_corporal' in request.form
            
            # Datos del profesional
            actividad.cns_profesional = request.form['cns_profesional']
            actividad.cbo = request.form['cbo']
            actividad.cnes_profesional = request.form['cnes_profesional']
            actividad.ine_profesional = request.form['ine_profesional']
            
            # Resultados
            actividad.cantidad_participantes = int(request.form['cantidad_participantes'])
            actividad.evaluaciones_alteradas = int(request.form.get('evaluaciones_alteradas', 0))
            
            db.session.commit()
            flash('Atividade coletiva atualizada com sucesso!', 'success')
            return redirect(url_for('listar_actividades_colectivas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar atividade coletiva: {str(e)}', 'error')
    return render_template('editar_actividad_colectiva.html', actividad=actividad)

@app.route('/ver_actividad_colectiva/<int:id>')
def ver_actividad_colectiva(id):
    actividad = ActividadColectiva.query.get_or_404(id)
    return render_template('ver_actividad_colectiva.html', actividad=actividad)

@app.route('/api/ciudadano/buscar', methods=['GET'])
def buscar_ciudadano():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'success': False, 'message': 'Ingrese al menos 2 caracteres'})
    
    # Buscar por CNS/CPF o nombre
    ciudadanos = Ciudadano.query.filter(
        or_(
            Ciudadano.cns_cpf.ilike(f'%{query}%'),
            Ciudadano.nombre_completo.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    resultados = []
    for ciudadano in ciudadanos:
        # Buscar el domicilio del ciudadano
        cadastro = CadastroDomiciliar.query.filter_by(microarea=ciudadano.microarea).first()
        domicilio = f"{cadastro.tipo_logradouro} {cadastro.nombre_logradouro}, {cadastro.numero}" if cadastro else "No especificado"
        
        resultados.append({
            'id': ciudadano.id,
            'cns_cpf': ciudadano.cns_cpf,
            'nombre_completo': ciudadano.nombre_completo,
            'fecha_nacimiento': ciudadano.fecha_nacimiento.strftime('%Y-%m-%d'),
            'sexo': ciudadano.sexo,
            'microarea': ciudadano.microarea,
            'domicilio': domicilio
        })
    
    return jsonify({
        'success': True,
        'resultados': resultados
    })

@app.route('/generar_pdf_visita/<int:visit_id>')
def generar_pdf_visita(visit_id):
    output_path = os.path.join('static', 'reports', f'visita_{visit_id}.pdf')
    db_models = {
        'VisitaDomiciliar': VisitaDomiciliar,
        'Ciudadano': Ciudadano,
        'ACS': ACS
    }
    ReportGenerator.generate_visit_pdf(visit_id, output_path, db_models)
    return send_file(output_path, as_attachment=True)

@app.route('/generar_excel_visitas', methods=['GET', 'POST'])
def generar_excel_visitas():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        output_path = os.path.join('static', 'reports', 'visitas.xlsx')
        db_models = {
            'VisitaDomiciliar': VisitaDomiciliar,
            'Ciudadano': Ciudadano,
            'ACS': ACS
        }
        ReportGenerator.generate_visits_excel(start_date, end_date, output_path, db_models)
        return send_file(output_path, as_attachment=True)
    return render_template('generar_informe.html')

@app.route('/generar_estadisticas', methods=['GET', 'POST'])
def generar_estadisticas():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        output_path = os.path.join('static', 'reports', 'estadisticas.pdf')
        db_models = {
            'VisitaDomiciliar': VisitaDomiciliar,
            'db': db
        }
        ReportGenerator.generate_statistics_report(start_date, end_date, output_path, db_models)
        return send_file(output_path, as_attachment=True)
    return render_template('generar_informe.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 