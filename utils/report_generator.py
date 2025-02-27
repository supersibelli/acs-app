from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import xlsxwriter
from datetime import datetime
from sqlalchemy import func

class ReportGenerator:
    @staticmethod
    def generate_visit_pdf(visit_id, output_path, db_models):
        """Genera un PDF detallado de una visita domiciliar específica"""
        VisitaDomiciliar = db_models['VisitaDomiciliar']
        Ciudadano = db_models['Ciudadano']
        ACS = db_models['ACS']

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Obtener datos de la visita
        visit = VisitaDomiciliar.query.get(visit_id)
        citizen = Ciudadano.query.filter_by(cns_cpf=visit.cns_ciudadano).first()
        acs = ACS.query.filter_by(cns=visit.cns_profesional).first()

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Ficha de Visita Domiciliar - {visit.fecha_registro.strftime('%d/%m/%Y')}", title_style))

        # Datos básicos
        data = [
            ["Datos Básicos", ""],
            ["Fecha", visit.fecha_registro.strftime("%d/%m/%Y")],
            ["Turno", visit.turno],
            ["Microárea", visit.microarea],
            ["Tipo de Inmueble", visit.tipo_inmueble],
            ["\nDatos del Ciudadano", ""],
            ["CNS", citizen.cns_cpf],
            ["Nombre", citizen.nombre_completo],
            ["Fecha de Nacimiento", citizen.fecha_nacimiento.strftime("%d/%m/%Y")],
            ["\nMotivos de la Visita", ""],
            ["Cadastramento/Actualización", "Sí" if visit.cadastramento_atualizacao else "No"],
            ["Visita Periódica", "Sí" if visit.visita_periodica else "No"],
            ["Busca Activa", "Sí" if visit.busca_ativa else "No"],
            ["\nResultado", visit.resultado_visita]
        ]

        # Crear tabla
        table = Table(data, colWidths=[4*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))

        elements.append(table)
        doc.build(elements)

    @staticmethod
    def generate_visits_excel(start_date, end_date, output_path, db_models):
        """Genera un informe Excel de todas las visitas en un rango de fechas"""
        VisitaDomiciliar = db_models['VisitaDomiciliar']
        Ciudadano = db_models['Ciudadano']
        ACS = db_models['ACS']

        visits = VisitaDomiciliar.query.filter(
            VisitaDomiciliar.fecha_registro.between(start_date, end_date)
        ).all()

        # Crear workbook
        workbook = xlsxwriter.Workbook(output_path)
        worksheet = workbook.add_worksheet('Visitas')

        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0d6efd',
            'font_color': 'white',
            'border': 1
        })

        cell_format = workbook.add_format({
            'border': 1
        })

        # Encabezados
        headers = ['Fecha', 'Turno', 'Microárea', 'CNS Ciudadano', 'Nombre Ciudadano', 'ACS', 'Tipo Inmueble', 'Resultado']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Datos
        for row, visit in enumerate(visits, start=1):
            citizen = Ciudadano.query.filter_by(cns_cpf=visit.cns_ciudadano).first()
            acs = ACS.query.filter_by(cns=visit.cns_profesional).first()
            
            worksheet.write(row, 0, visit.fecha_registro.strftime("%d/%m/%Y"), cell_format)
            worksheet.write(row, 1, visit.turno, cell_format)
            worksheet.write(row, 2, visit.microarea, cell_format)
            worksheet.write(row, 3, visit.cns_ciudadano, cell_format)
            worksheet.write(row, 4, citizen.nombre_completo if citizen else '', cell_format)
            worksheet.write(row, 5, f"{acs.nombre}" if acs else '', cell_format)
            worksheet.write(row, 6, visit.tipo_inmueble, cell_format)
            worksheet.write(row, 7, visit.resultado_visita, cell_format)

        # Ajustar ancho de columnas
        for i, header in enumerate(headers):
            worksheet.set_column(i, i, len(header) + 5)

        workbook.close()

    @staticmethod
    def generate_statistics_report(start_date, end_date, output_path, db_models):
        """Genera un informe estadístico en PDF con gráficos"""
        VisitaDomiciliar = db_models['VisitaDomiciliar']
        db = db_models['db']

        doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        elements = []

        # Título
        title = Paragraph(
            f"Informe Estadístico de Visitas ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})",
            styles['Heading1']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Estadísticas generales
        total_visits = VisitaDomiciliar.query.filter(
            VisitaDomiciliar.fecha_registro.between(start_date, end_date)
        ).count()

        visits_by_type = db.session.query(
            VisitaDomiciliar.tipo_inmueble,
            func.count(VisitaDomiciliar.id)
        ).filter(
            VisitaDomiciliar.fecha_registro.between(start_date, end_date)
        ).group_by(VisitaDomiciliar.tipo_inmueble).all()

        # Crear tabla de estadísticas
        stats_data = [
            ['Estadísticas Generales', ''],
            ['Total de Visitas', str(total_visits)],
            ['\nVisitas por Tipo de Inmueble', '']
        ]
        
        for tipo, count in visits_by_type:
            stats_data.append([tipo, str(count)])

        table = Table(stats_data, colWidths=[5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))

        elements.append(table)
        doc.build(elements) 