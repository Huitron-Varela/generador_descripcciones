# UML AI Studio · Gemini

Aplicación académica en Python para transformar requerimientos expresados en lenguaje formal o informal en diagramas UML mediante Gemini y PlantUML.

## Flujo UX

1. Selecciona **Casos de uso, Clases, Secuencia o Actividad**.
2. Elige **Lenguaje natural** o **Requerimientos formales**.
3. Describe el sistema.
4. Gemini normaliza e interpreta la entrada y devuelve una estructura JSON validada con Pydantic.
5. El usuario revisa requerimientos normalizados, elementos detectados, supuestos, alertas y confianza.
6. Python genera PlantUML y obtiene una vista SVG.
7. El usuario puede pedir un refinamiento a Gemini o exportar `.puml` y `.svg`.

## Requisitos

- Python 3.10 o superior.
- Conexión a Internet para Gemini y para el renderizado mediante el servidor público de PlantUML.
- API Key de Gemini.

La versión del framework visual está fijada en **Flet 0.86.0** para evitar incompatibilidades con APIs antiguas como `ft.border.all`.

## Instalación en Windows

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copia `.env.example` como `.env` y agrega tu clave:

```env
GEMINI_API_KEY=TU_CLAVE
GEMINI_MODEL=gemini-2.5-flash
```

Ejecuta:

```bash
flet run app.py
```

Para versión web:

```bash
flet run --web app.py
```

## Exportaciones

Los archivos generados se guardan en la carpeta `exports/` del proyecto. No se utiliza base de datos: el modelo actual se mantiene únicamente en memoria durante la sesión.

## Seguridad

No publiques el archivo `.env` ni la API Key. El `.gitignore` incluido excluye credenciales y exportaciones.

## Arquitectura

```text
Entrada del usuario
      ↓
UX en Flet
      ↓
Gemini API
      ↓
UMLAnalysis (Pydantic / JSON)
      ↓
Validación humana
      ↓
PlantUMLGenerator
      ↓
Código PlantUML
      ↓
SVG / exportación
```

## Nota de privacidad

La vista previa usa el servidor público de PlantUML. Para información confidencial se recomienda migrar el renderizado a una instalación local de PlantUML.

## Inicio rápido en Windows

También se incluyen dos accesos directos por lote:

- `INSTALAR.bat`: crea `.venv` e instala las versiones fijadas.
- `INICIAR.bat`: verifica Flet, Gemini y la API Key antes de abrir la aplicación.

Puedes ejecutar `python verificar_entorno.py` manualmente para diagnosticar instalaciones incompatibles.


## Compatibilidad Flet 0.86.0
Esta revisión elimina propiedades no soportadas por `Container`, incluyendo `min_height`. La vista previa utiliza `height=360`, compatible con la API actual.
