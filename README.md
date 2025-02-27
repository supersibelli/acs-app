# Sistema de Cadastro Individual

Este es un sistema de registro individual desarrollado con Flask para gestionar información de ciudadanos y sus datos de salud.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- En Windows:
```bash
venv\Scripts\activate
```
- En Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

1. Activar el entorno virtual (si no está activado)

2. Ejecutar la aplicación:
```bash
python app.py
```

3. Abrir el navegador y acceder a:
```
http://localhost:5000
```

## Características

- Registro completo de información personal
- Gestión de datos de salud
- Información sociodemográfica
- Registro de situación de calle
- Datos del profesional de salud

## Estructura del Proyecto

```
.
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias del proyecto
├── README.md          # Este archivo
└── templates/         # Plantillas HTML
    ├── base.html     # Plantilla base
    ├── index.html    # Página de inicio
    └── cadastro.html # Formulario de registro
```

## Contribución

1. Fork el proyecto
2. Cree una rama para su característica (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información. 