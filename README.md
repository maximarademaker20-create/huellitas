# Huellitas — Sistema de gestión de pacientes veterinarios

Proyecto integrador · Maxima Rademaker
ISET N° 25 "Beppo Levi"

Aplicación web para la gestión de pacientes de una clínica veterinaria: registro de
dueños y mascotas, historial clínico, control de vacunas, agenda de turnos y envío de
recordatorios e informes por WhatsApp.

## Tecnologías

| Herramienta | Uso |
|---|---|
| Python 3 | Lenguaje de programación |
| Django 5.2 | Framework web (modelos, vistas, formularios, autenticación) |
| MySQL 8.0 | Base de datos relacional |
| PyMySQL | Conector entre Django y MySQL |
| HTML y CSS | Interfaz de usuario (plantillas de Django) |

## Puesta en marcha

### 1. Crear la base de datos y el usuario

En MySQL Workbench o en la consola de MySQL:

```sql
create database if not exists huellitas character set utf8mb4;

create user 'huellitas'@'localhost' identified by 'huellitas123';
grant all privileges on huellitas.* to 'huellitas'@'localhost';
flush privileges;
```

Si se quieren usar otras credenciales, hay que modificarlas en `huellitas/settings.py`,
en la sección `DATABASES`.

### 2. Crear el entorno virtual e instalar las dependencias

Desde la carpeta que contiene a `huellitas`:

```
python -m venv venv
venv\Scripts\activate
python -m pip install -r huellitas\requirements.txt
```

En Linux o macOS, la activación es `source venv/bin/activate`.

### 3. Crear las tablas

Desde la carpeta que contiene `manage.py`:

```
python manage.py migrate
```

### 4. Cargar datos de prueba (opcional)

```
python manage.py datos_prueba
```

Carga especies, razas, vacunas, dueños, mascotas, consultas y turnos de ejemplo.

### 5. Crear la primera cuenta y levantar el servidor

```
python manage.py runserver
```

Abrir http://127.0.0.1:8000 e ingresar a "Registrate" para crear la primera cuenta
del personal, eligiendo el rol (Recepción o Veterinario/a).

## Estructura del proyecto

```
huellitas/
├── manage.py
├── requirements.txt
├── huellitas/              Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── __init__.py         Activa el conector PyMySQL
├── usuarios/               Acceso al sistema y gestión del personal
│   ├── models.py           Modelo Perfil (rol y teléfono)
│   ├── views.py            Registro, listado y edición del personal
│   └── templates/usuarios/
├── veterinaria/            Aplicación principal
│   ├── models.py           9 modelos del sistema
│   ├── views.py            Lógica de todas las pantallas
│   ├── forms.py            Formularios y validaciones
│   ├── whatsapp.py         Armado de los mensajes de WhatsApp
│   ├── migrations/
│   └── templates/veterinaria/
└── static/                 Hoja de estilos e imágenes
```

## Funcionalidades

- **Dueños**: alta, edición y búsqueda por nombre, apellido o DNI. Control de DNI duplicado.
- **Mascotas**: ficha del paciente con especie, raza, sexo, fecha de nacimiento y dueño.
  Búsqueda combinada con filtros por especie y estado. Baja lógica con motivo y reactivación.
- **Historial clínico**: consultas y vacunas aplicadas en una línea de tiempo única.
- **Turnos**: calendario mensual, control de superposición de horarios y cambio de estado.
- **Recordatorios por WhatsApp**: aviso de turno al dueño y aviso de vacuna próxima.
- **Informe de la agenda diaria**: genera el listado de turnos del día y lo envía al
  veterinario por WhatsApp.
- **Personal**: alta de cuentas con rol y teléfono.
- **Seguridad**: acceso restringido con inicio de sesión, contraseñas cifradas con
  PBKDF2-SHA256, protección CSRF en todos los formularios.

## Base de datos

Las tablas se llaman igual que en el diseño original (`especie`, `raza`, `dueno`,
`mascota`, `consulta`, `vacuna`, `vacuna_aplicada`, `turno`, `recordatorio`, `perfil`)
y sus claves primarias siguen el formato `id_<tabla>`.

## Repositorio

https://github.com/maximarademaker20-create/huellitas
