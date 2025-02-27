from app import app, db, ACS, Ciudadano, VisitaDomiciliar
from datetime import datetime, timedelta
import random

def generar_fecha_aleatoria(start_date=None):
    if not start_date:
        start_date = datetime.now() - timedelta(days=90)  # Últimos 3 meses
    days_between = (datetime.now() - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

def generar_visitas():
    with app.app_context():
        # Obtener todos los ACS activos
        acs_list = ACS.query.filter_by(activo=True).all()
        
        if not acs_list:
            print("No hay ACS activos en el sistema.")
            return
        
        visitas_generadas = 0
        
        for acs in acs_list:
            print(f"\nGenerando visitas para ACS: {acs.nombre}")
            # Obtener ciudadanos en las microáreas del ACS
            microareas = acs.microareas.split(',')
            ciudadanos = Ciudadano.query.filter(Ciudadano.microarea.in_(microareas)).all()
            
            if not ciudadanos:
                print(f"No hay ciudadanos en las microáreas {microareas} del ACS {acs.nombre}")
                continue
            
            # Generar entre 5 y 10 visitas para cada ACS
            num_visitas = random.randint(5, 10)
            
            for _ in range(num_visitas):
                ciudadano = random.choice(ciudadanos)
                
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
                
                db.session.add(visita)
                visitas_generadas += 1
            
            print(f"Se generaron {num_visitas} visitas para el ACS {acs.nombre}")
        
        try:
            db.session.commit()
            print(f"\nTotal de visitas generadas: {visitas_generadas}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar las visitas: {str(e)}")

if __name__ == '__main__':
    generar_visitas() 