# SQL Database Testing Project

Proyecto de pruebas automatizadas para bases de datos MySQL usando pytest.

## Estructura del Proyecto

```
sql_testing_project/
├── config/
│   └── db_config.py          # Configuración de conexión a BD
├── data/
│   └── test_data.py          # Datos de prueba y generadores
├── database/
│   └── db_connector.py       # Conector MySQL con operaciones CRUD
├── tests/
│   ├── conftest.py           # Fixtures de pytest
│   ├── test_crud_operations.py    # Tests CRUD
│   ├── test_data_integrity.py     # Tests de integridad
│   └── test_performance.py        # Tests de rendimiento
├── reports/                  # Reportes HTML generados
├── .env                      # Variables de entorno (no commitear)
├── .env.example              # Plantilla de variables de entorno
├── pytest.ini                # Configuración de pytest
└── requirements.txt          # Dependencias del proyecto
```

## Requisitos Previos

- Python 3.10+
- MySQL Server 8.0+
- PyCharm IDE 

## Instalación

### 1. Clonar o Crear el Proyecto

```bash
# Crear directorio del proyecto
mkdir sql_testing_project
cd sql_testing_project
```

### 2. Crear Entorno Virtual en PyCharm

1. Abrir PyCharm
2. `File > Open` → seleccionar la carpeta del proyecto
3. `File > Settings > Project > Python Interpreter`
4. Click en el engranaje ⚙️ → `Add`
5. Seleccionar `Virtualenv Environment > New`
6. Click `OK`

### 3. Instalar Dependencias

En la terminal de PyCharm:

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos MySQL

Conectarse a MySQL y ejecutar:

```sql
-- Crear base de datos de prueba
CREATE DATABASE IF NOT EXISTS test_database;

-- Crear usuario de prueba (opcional)
CREATE USER IF NOT EXISTS 'test_user'@'localhost' IDENTIFIED BY 'test_password';
GRANT ALL PRIVILEGES ON test_database.* TO 'test_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar Variables de Entorno

Copiar `.env.example` a `.env` y editar:

```bash
cp .env.example .env
```

Editar `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_aqui
DB_NAME=test_database
```

## Configuración de PyCharm

### Configurar pytest como Test Runner

1. `File > Settings > Tools > Python Integrated Tools`
2. En "Default test runner" seleccionar `pytest`
3. Click `OK`

### Configurar Run Configuration

1. `Run > Edit Configurations`
2. Click `+` → `pytest`
3. Configurar:
   - **Name**: `All Tests`
   - **Target**: `Custom`
   - **Additional Arguments**: `-v --tb=short`
   - **Working directory**: `/ruta/al/proyecto`
4. Click `OK`

## Ejecución de Tests

### Desde Terminal

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con reporte HTML
pytest --html=reports/report.html --self-contained-html

# Ejecutar por marcadores
pytest -m crud          # Solo tests CRUD
pytest -m integrity     # Solo tests de integridad
pytest -m performance   # Solo tests de rendimiento
pytest -m smoke         # Tests rápidos de humo

# Ejecutar archivo específico
pytest tests/test_crud_operations.py

# Ejecutar test específico
pytest tests/test_crud_operations.py::TestCreateOperations::test_insert_single_user

# Ejecutar en paralelo
pytest -n auto
```

### Desde PyCharm

1. Click derecho en `tests/` → `Run 'pytest in tests'`
2. O usar el botón verde ▶️ junto a cada test
3. Ver resultados en la ventana "Run"

## Estructura de Tests

### Test CRUD (`test_crud_operations.py`)

| ID | Test | Descripción |
|---|------|-------------|
| TC-CR-001 | test_insert_single_user | Inserción simple de usuario |
| TC-CR-002 | test_insert_user_data_persisted | Verificar datos persistidos |
| TC-CR-003 | test_insert_single_product | Inserción de producto |
| TC-CR-004 | test_insert_many_users | Inserción masiva de usuarios |
| TC-RD-001 | test_select_all_users | SELECT sin condiciones |
| TC-UP-001 | test_update_single_field | UPDATE de un campo |
| TC-DL-001 | test_delete_single_record | DELETE de un registro |

### Test Integridad (`test_data_integrity.py`)

| ID | Test | Descripción |
|---|------|-------------|
| TC-INT-001 | test_users_table_exists | Verificar existencia de tabla |
| TC-CON-001 | test_unique_username_constraint | Constraint UNIQUE |
| TC-CON-005 | test_foreign_key_user_constraint | Constraint FOREIGN KEY |
| TC-DT-001 | test_decimal_precision_price | Precisión DECIMAL |
| TC-REF-001 | test_order_references_valid_user | Integridad referencial |

### Test Rendimiento (`test_performance.py`)

| ID | Test | Descripción |
|---|------|-------------|
| TC-PERF-001 | test_select_all_performance | Performance SELECT * |
| TC-PERF-006 | test_bulk_insert_100_records | Performance inserción masiva |
| TC-PERF-011 | test_mixed_operations | Operaciones mixtas CRUD |

## Uso del DatabaseConnector

```python
from database.db_connector import DatabaseConnector

# Usando context manager 
with DatabaseConnector() as db:
    # Insert
    user_id = db.insert('users', {'username': 'test', 'email': 'test@test.com'})
    
    # Select
    users = db.select('users', condition='is_active = %s', condition_params=(True,))
    
    # Update
    db.update('users', {'email': 'new@email.com'}, 'id = %s', (user_id,))
    
    # Delete
    db.delete('users', 'id = %s', (user_id,))
    
    # Custom query
    result = db.execute_query("SELECT COUNT(*) FROM users")
```

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

## Reportes

### Reporte HTML

```bash
pytest --html=reports/report.html --self-contained-html
```

### Reporte Allure

```bash
# Generar datos
pytest --alluredir=allure-results

# Ver reporte
allure serve allure-results
```

## Troubleshooting

### Error de Conexión

```
Error: Access denied for user 'root'@'localhost'
```
**Solución**: Verificar credenciales en `.env`

### Error de Codificación

```
Error: 'latin-1' codec can't encode character
```
**Solución**: Agregar `charset='utf8mb4'` en db_connector.py

### Tests Fallan en CI/CD

Asegurarse de que las variables de entorno están configuradas en el pipeline.

## Extensiones Sugeridas

1. **Agregar más tablas**: Extender el schema según necesidades
2. **Tests de transacciones**: Verificar rollback en errores
3. **Tests de concurrencia**: Usar threading para tests paralelos
4. **Fixtures parametrizadas**: Usar `@pytest.mark.parametrize`

## Licencia

MIT License
