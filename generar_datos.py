from app import app, db, Ciudadano, CadastroDomiciliar, VisitaDomiciliar, ActividadColectiva, ACS
from datetime import datetime, timedelta
import random
from faker import Faker
import string

fake = Faker(['pt_BR'])

def generar_cns():
    return ''.join(random.choices(string.digits, k=15))

def generar_cpf():
    return ''.join(random.choices(string.digits, k=11))

def generar_fecha_aleatoria(start_year=2023):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generar_ciudadanos(cantidad=50):
    ciudadanos = []
    for _ in range(cantidad):
        sexo = random.choice(['M', 'F'])
        fecha_nacimiento = fake.date_of_birth(minimum_age=0, maximum_age=90)
        
        ciudadano = Ciudadano(
            cns_cpf=generar_cns() if random.random() > 0.5 else generar_cpf(),
            nombre_completo=fake.name(),
            nombre_social=fake.name() if random.random() > 0.8 else None,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            raza_color=random.choice(['Branca', 'Preta', 'Parda', 'Amarela', 'Indígena']),
            etnia=fake.word() if random.random() > 0.9 else None,
            nis_pis_pasep=generar_cns() if random.random() > 0.7 else None,
            nombre_madre=fake.name_female(),
            nombre_padre=fake.name_male() if random.random() > 0.3 else None,
            nacionalidad=random.choice(['Brasileira', 'Naturalizado', 'Estrangeiro']),
            telefono=fake.phone_number(),
            email=fake.email() if random.random() > 0.5 else None,
            microarea=str(random.randint(1, 10)),
            es_responsable_familiar=random.random() > 0.7,
            escolaridad=random.choice(['Creche', 'Pré-escola', 'Fundamental 1ª a 4ª séries', 'Fundamental 5ª a 8ª séries', 'Ensino Médio Completo', 'Superior']),
            situacion_trabajo=random.choice(['Empregador', 'Assalariado com carteira', 'Autônomo com previdência', 'Desempregado']),
            gestante=(sexo == 'F' and random.random() > 0.8),
            hipertension=random.random() > 0.8,
            diabetes=random.random() > 0.9,
            cancer=random.random() > 0.95,
            fumante=random.random() > 0.8,
            alcohol=random.random() > 0.8,
            otras_drogas=random.random() > 0.9,
            situacion_calle=random.random() > 0.95,
            cns_profesional=generar_cns(),
            cbo='123456',
            cnes='654321',
            ine='789012',
            fecha_registro=generar_fecha_aleatoria()
        )
        ciudadanos.append(ciudadano)
    
    return ciudadanos

def generar_cadastros_domiciliares(cantidad=30):
    barrios = ['Centro', 'Jardim América', 'Vila Nova', 'Bela Vista', 'São José', 
               'Santa Rosa', 'Jardim das Flores', 'Vila Verde', 'Parque São João', 'Nova Esperança']
    
    cadastros = []
    for _ in range(cantidad):
        cadastro = CadastroDomiciliar(
            cnes='654321',
            ine='789012',
            microarea=str(random.randint(1, 10)),
            fecha_registro=generar_fecha_aleatoria(),
            prontuario_familiar=str(random.randint(1000, 9999)),
            tipo_logradouro=random.choice(['Rua', 'Avenida', 'Travessa', 'Praça', 'Alameda']),
            nombre_logradouro=fake.street_name(),
            numero=str(random.randint(1, 999)),
            complemento=fake.street_suffix() if random.random() > 0.7 else None,
            barrio=random.choice(barrios),
            municipio=fake.city(),
            uf=random.choice(['SP', 'RJ', 'MG', 'BA', 'RS']),
            cep=fake.postcode(),
            telefono_residencial=fake.phone_number(),
            telefono_referencia=fake.phone_number() if random.random() > 0.7 else None,
            tiene_animales=random.random() > 0.5,
            cantidad_animales=random.randint(1, 5),
            tipo_animal_gato=random.random() > 0.5,
            tipo_animal_perro=random.random() > 0.5,
            tipo_animal_pajaro=random.random() > 0.5,
            tipo_animal_otro=random.random() > 0.8,
            otro_animal_especificar=fake.word() if random.random() > 0.8 else None,
            tipo_domicilio=random.choice(['Casa', 'Apartamento', 'Cômodo']),
            numero_moradores=random.randint(1, 8),
            numero_comodos=random.randint(3, 10),
            energia_electrica=random.random() > 0.1,
            cartao_sus_profesional=generar_cns()
        )
        cadastros.append(cadastro)
    
    return cadastros

def generar_visitas_domiciliares(cantidad=100):
    visitas = []
    ciudadanos = Ciudadano.query.all()
    acs_list = ACS.query.filter_by(activo=True).all()
    
    for _ in range(cantidad):
        ciudadano = random.choice(ciudadanos)
        acs = random.choice(acs_list)
        
        visita = VisitaDomiciliar(
            fecha_registro=generar_fecha_aleatoria(),
            turno=random.choice(['M', 'T', 'N']),
            microarea=ciudadano.microarea,
            tipo_inmueble='01',  # Domicilio
            cns_ciudadano=ciudadano.cns_cpf,
            fecha_nacimiento=ciudadano.fecha_nacimiento,
            sexo=ciudadano.sexo,
            
            # Motivos de la visita (aleatorios)
            cadastramento_atualizacao=random.choice([True, False]),
            visita_periodica=random.choice([True, False]),
            busca_ativa=random.choice([True, False]),
            convite_atividades=random.choice([True, False]),
            orientacao_prevencao=random.choice([True, False]),
            
            # Acompañamiento (basado en las condiciones del ciudadano)
            gestante=ciudadano.gestante,
            pessoa_hipertensao=ciudadano.hipertension,
            pessoa_diabetes=ciudadano.diabetes,
            pessoa_cancer=ciudadano.cancer,
            
            # Control ambiental/vectorial (aleatorio)
            vulnerabilidade_social=random.choice([True, False]),
            tabagista=ciudadano.fumante,
            usuario_alcool=ciudadano.alcohol,
            usuario_drogas=ciudadano.otras_drogas,
            
            # Datos antropométricos
            peso=round(random.uniform(45.0, 95.0), 1) if random.random() > 0.3 else None,
            altura=random.randint(150, 190) if random.random() > 0.3 else None,
            
            # Resultado de la visita
            resultado_visita=random.choices(
                ['01', '02', '03'],  # Realizada, Recusada, Ausente
                weights=[0.8, 0.1, 0.1]  # 80% realizadas, 10% recusadas, 10% ausentes
            )[0],
            visita_compartida=random.random() > 0.8,  # 20% de probabilidad de ser compartida
            
            # Datos del profesional
            cns_profesional=acs.cns,
            cbo=acs.cbo,
            cnes=acs.cnes,
            ine=acs.ine
        )
        visitas.append(visita)
    
    return visitas

def generar_actividades_colectivas(cantidad=20):
    actividades = []
    for _ in range(cantidad):
        actividad = ActividadColectiva(
            cnes='654321',
            ine='789012',
            fecha_actividad=generar_fecha_aleatoria(),
            turno=random.choice(['M', 'T', 'N']),
            numero_hoja=str(random.randint(1, 999)),
            tipo_actividad=random.choice(['01', '02', '03', '04', '05', '06']),
            otro_tipo_actividad=fake.word() if random.random() > 0.8 else None,
            publico_comunidad=random.random() > 0.5,
            publico_gestantes=random.random() > 0.7,
            publico_mujeres=random.random() > 0.6,
            tema_alimentacion=random.random() > 0.6,
            tema_autocuidado=random.random() > 0.7,
            practica_antropometria=random.random() > 0.8,
            practica_corporal=random.random() > 0.7,
            cns_profesional=generar_cns(),
            cbo='123456',
            cnes_profesional='654321',
            ine_profesional='789012',
            cantidad_participantes=random.randint(5, 50),
            evaluaciones_alteradas=random.randint(0, 5)
        )
        actividades.append(actividad)
    
    return actividades

def generar_acs(cantidad=20):
    unidades_saude = [
        'UBS Centro',
        'UBS Vila Nova',
        'UBS Jardim América',
        'UBS Santa Rosa',
        'UBS São José'
    ]
    
    acs_list = []
    for _ in range(cantidad):
        # Generar entre 1 y 3 microáreas aleatorias para cada ACS
        num_microareas = random.randint(1, 3)
        microareas = sorted(random.sample(range(1, 11), num_microareas))
        
        acs = ACS(
            nombre=fake.name(),
            cns=generar_cns(),
            cbo='515105',  # CBO específico para ACS
            cnes=str(random.randint(1000000, 9999999)),
            ine=str(random.randint(1000, 9999)),
            unidade_saude=random.choice(unidades_saude),
            microareas=','.join(map(str, microareas)),
            activo=random.random() > 0.1,  # 90% de probabilidad de estar activo
            fecha_registro=generar_fecha_aleatoria()
        )
        acs_list.append(acs)
    
    return acs_list

def main():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Limpiar tablas existentes
        db.session.query(VisitaDomiciliar).delete()
        db.session.query(Ciudadano).delete()
        db.session.query(CadastroDomiciliar).delete()
        db.session.query(ActividadColectiva).delete()
        db.session.query(ACS).delete()
        db.session.commit()

        # Generar datos en orden
        print("Generando ACS...")
        acs_list = generar_acs(20)
        db.session.add_all(acs_list)
        db.session.commit()
        
        print("Generando ciudadanos...")
        ciudadanos = generar_ciudadanos(50)
        db.session.add_all(ciudadanos)
        db.session.commit()
        
        print("Generando cadastros domiciliares...")
        cadastros = generar_cadastros_domiciliares(30)
        db.session.add_all(cadastros)
        db.session.commit()
        
        print("Generando visitas domiciliares...")
        visitas = generar_visitas_domiciliares(100)
        db.session.add_all(visitas)
        db.session.commit()
        
        print("Generando actividades colectivas...")
        actividades = generar_actividades_colectivas(20)
        db.session.add_all(actividades)
        db.session.commit()

        print("Dados de teste gerados com sucesso!")
        print(f"Foram gerados:")
        print(f"- {len(acs_list)} agentes comunitários de saúde")
        print(f"- {len(ciudadanos)} cadastros individuais")
        print(f"- {len(cadastros)} cadastros domiciliares")
        print(f"- {len(visitas)} visitas domiciliares")
        print(f"- {len(actividades)} atividades coletivas")

if __name__ == '__main__':
    main() 