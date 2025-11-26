# SQL Database Testing Project

Proyecto de pruebas automatizadas para bases de datos MySQL usando pytest.

## Bases de Datos

Este proyecto incluye tests para dos bases de datos:

| Base de Datos | Descripción | Tests |
|---------------|-------------|-------|
| `test_database` | Base de datos de prueba con tablas users, products, orders | 65 tests |
| `sakila` | Base de datos de ejemplo de MySQL (tienda de DVD) | 91 tests |

**Total: 156 tests**

---

## Estructura del Proyecto

```
sql_testing_project/
├── config/
│   ├── __init__.py
│   └── db_config.py              # Configuración para test_database y sakila
├── data/
│   ├── __init__.py
│   ├── test_data.py              # Datos para test_database
│   └── sakila_test_data.py       # Datos para sakila
├── database/
│   ├── __init__.py
│   └── db_connector.py           # Conector MySQL
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Fixtures de pytest
│   ├── test_crud_operations.py   # Tests CRUD (test_database)
│   ├── test_data_integrity.py    # Tests integridad (test_database)
│   ├── test_performance.py       # Tests rendimiento (test_database)
│   ├── test_sakila_schema.py     # Tests schema (sakila)
│   ├── test_sakila_data.py       # Tests datos (sakila)
│   ├── test_sakila_queries.py    # Tests queries (sakila)
│   └── test_sakila_performance.py # Tests rendimiento (sakila)
├── reports/
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Requisitos Previos

- Python 3.10+
- MySQL Server 8.0+
- PyCharm IDE (recomendado)
- Base de datos Sakila instalada (con datos)

---

## Instalación

### 1. Clonar el Proyecto

```bash
git clone <repo-url>
cd sql_testing_project
```

### 2. Crear Entorno Virtual

PyCharm lo crea automáticamente al abrir el proyecto.

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos test_database

Conectar a MySQL y ejecutar:

```sql
CREATE DATABASE IF NOT EXISTS test_database;
```

### 5. Verificar Sakila

Sakila debe estar instalada con datos. Verificar:

```sql
USE sakila;
SELECT COUNT(*) FROM actor;  -- Debe mostrar 200
```

Si no está instalada o no tiene datos, descargar de: https://dev.mysql.com/doc/index-other.html

```bash
# Importar schema y datos
mysql -u root -p < sakila-schema.sql
mysql -u root -p < sakila-data.sql
```

### 6. Configurar Variables de Entorno

Editar `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=test_database
```

---

## Ejecución de Tests

### Todos los Tests

```bash
pytest
```

### Solo test_database

```bash
pytest tests/test_crud_operations.py tests/test_data_integrity.py tests/test_performance.py
```

### Solo Sakila

```bash
pytest -m sakila
```

### Por Categoría

```bash
pytest -m crud          # Operaciones CRUD
pytest -m integrity     # Integridad de datos
pytest -m performance   # Rendimiento
pytest -m schema        # Validación de schema
pytest -m data          # Validación de datos
pytest -m queries       # Validación de queries
```

### Con Reporte HTML

```bash
pytest --html=reports/report.html --self-contained-html
```

---

## Tests de test_database

### test_crud_operations.py (25 tests)

Valida operaciones CRUD básicas:

| Clase | Tests | Descripción |
|-------|-------|-------------|
| TestCreateOperations | 7 | INSERT simple, múltiple, duplicados |
| TestReadOperations | 8 | SELECT, filtros, ORDER BY, LIMIT, COUNT |
| TestUpdateOperations | 5 | UPDATE simple, múltiple, condicional |
| TestDeleteOperations | 5 | DELETE, CASCADE, TRUNCATE |

### test_data_integrity.py (26 tests)

Valida integridad y constraints:

| Clase | Tests | Descripción |
|-------|-------|-------------|
| TestSchemaIntegrity | 6 | Existencia de tablas y columnas |
| TestConstraints | 8 | UNIQUE, NOT NULL, FOREIGN KEY, ENUM |
| TestDataTypes | 5 | DECIMAL, INT, BOOLEAN, VARCHAR, TIMESTAMP |
| TestReferentialIntegrity | 4 | JOINs, CASCADE DELETE |
| TestDataConsistency | 3 | Defaults, timestamps automáticos |

### test_performance.py (14 tests)

Mide tiempos de ejecución:

| Clase | Tests | Descripción |
|-------|-------|-------------|
| TestQueryPerformance | 5 | SELECT, filtros, JOINs |
| TestBulkOperationPerformance | 4 | INSERT masivo, UPDATE, DELETE |
| TestStressTests | 3 | Operaciones repetidas, mixtas |
| TestConnectionPerformance | 2 | Conexión, context manager |

### test_database: Estructura

#### Tabla users

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INT | Primary key, auto increment |
| username | VARCHAR(50) | Único, no nulo |
| email | VARCHAR(100) | Único, no nulo |
| password_hash | VARCHAR(255) | No nulo |
| first_name | VARCHAR(50) | Nombre |
| last_name | VARCHAR(50) | Apellido |
| age | INT | Edad |
| is_active | BOOLEAN | Default TRUE |
| created_at | TIMESTAMP | Auto generado |
| updated_at | TIMESTAMP | Auto actualizado |

#### Tabla products

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INT | Primary key, auto increment |
| name | VARCHAR(100) | No nulo |
| description | TEXT | Descripción |
| price | DECIMAL(10,2) | No nulo |
| stock | INT | Default 0 |
| category | VARCHAR(50) | Categoría |
| is_available | BOOLEAN | Default TRUE |
| created_at | TIMESTAMP | Auto generado |

#### Tabla orders

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INT | Primary key, auto increment |
| user_id | INT | FK → users(id), CASCADE |
| product_id | INT | FK → products(id), CASCADE |
| quantity | INT | No nulo |
| total_price | DECIMAL(10,2) | No nulo |
| status | ENUM | pending, processing, shipped, delivered, cancelled |
| order_date | TIMESTAMP | Auto generado |

### Diagrama ER - test_database

```
users ──────< orders >────── products
  │              │
  │         [user_id]
  │         [product_id]
  │              │
  └──────────────┘
     CASCADE DELETE
```

---

## Tests de Sakila

### test_sakila_schema.py (35 tests)

Valida la estructura de la base de datos:

- Existencia de las 16 tablas
- Existencia de las 7 vistas
- Columnas de cada tabla
- Primary keys y foreign keys
- Constraints (ENUM, NOT NULL)

### test_sakila_data.py (22 tests)

Valida los datos existentes:

- Conteo de registros por tabla
- Valores válidos (categorías, ratings, idiomas)
- Integridad referencial
- Datos no nulos donde se requiere

### test_sakila_queries.py (21 tests)

Valida queries complejas:

- SELECTs básicos y filtrados
- JOINs de múltiples tablas
- Agregaciones (COUNT, SUM, AVG)
- Subqueries

### test_sakila_performance.py (13 tests)

Mide tiempos de ejecución:

- SELECT en tablas grandes
- JOINs complejos
- Agregaciones
- Vistas

### Sakila: Estructura

#### Tablas Principales

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| actor | 200 | Actores de películas |
| film | 1000 | Catálogo de películas |
| customer | 599 | Clientes de la tienda |
| rental | 16044 | Historial de alquileres |
| payment | 16049 | Pagos realizados |
| inventory | 4581 | Inventario por tienda |
| category | 16 | Categorías de películas |
| language | 6 | Idiomas disponibles |
| store | 2 | Tiendas |
| staff | 2 | Empleados |

#### Vistas

- `customer_list` - Lista de clientes con dirección
- `film_list` - Películas con categoría y actores
- `sales_by_film_category` - Ventas por categoría
- `sales_by_store` - Ventas por tienda
- `staff_list` - Lista de empleados
- `actor_info` - Actores con sus películas
- `nicer_but_slower_film_list` - Lista detallada de películas

### Diagrama ER - Sakila (Simplificado)

```
customer ──< rental >── inventory ──< film
    │           │                      │
    │           │                      ├──< film_actor >── actor
    │           │                      │
    │           │                      └──< film_category >── category
    │           │
    └───< payment
```

---

## Uso del DatabaseConnector

```python
from database.db_connector import DatabaseConnector

# Usando context manager (recomendado)
with DatabaseConnector() as db:
    # Insert
    user_id = db.insert('users', {'username': 'test', 'email': 'test@test.com', 'password_hash': 'hash'})
    
    # Select
    users = db.select('users', condition='is_active = %s', condition_params=(True,))
    
    # Update
    db.update('users', {'email': 'new@email.com'}, 'id = %s', (user_id,))
    
    # Delete
    db.delete('users', 'id = %s', (user_id,))
    
    # Custom query
    result = db.execute_query("SELECT COUNT(*) as count FROM users")
```

---

## Generación de Datos de Prueba

```python
from data.test_data import TestDataGenerator

# Generar un usuario aleatorio
user = TestDataGenerator.generate_user()

# Generar múltiples usuarios
users = TestDataGenerator.generate_users(10)

# Generar datos para insert_many
columns, data = TestDataGenerator.generate_bulk_users_tuple(100)
db.insert_many('users', columns, data)
```

---

## Troubleshooting

### Error: test_database not found

```sql
CREATE DATABASE test_database;
```

### Error: sakila database not found

```bash
# Descargar sakila
wget https://downloads.mysql.com/docs/sakila-db.zip
unzip sakila-db.zip
cd sakila-db

# Importar
mysql -u root -p < sakila-schema.sql
mysql -u root -p < sakila-data.sql
```

### Error: sakila tables empty (COUNT = 0)

Solo importaste el schema. Necesitas importar los datos:

```bash
mysql -u root -p sakila < sakila-data.sql
```

### Error: Access denied

Verificar credenciales en `.env`

### Error: COLUMN_NAME KeyError

Cambiar `column_name` por `COLUMN_NAME` en los tests de schema.

### Error en Mac: mysql command not found

Usar la ruta completa:

```bash
/usr/local/mysql/bin/mysql -u root -p
```

---

## Licencia

MIT License
