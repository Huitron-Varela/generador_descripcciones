# UML AI Studio Web

Sistema web para convertir requerimientos escritos en lenguaje natural en diagramas UML utilizando un LLM de OpenAI.

## Stack

- Frontend: HTML5 + CSS3 + JavaScript (Vanilla)
- Backend web: Node.js + Express (JavaScript, sin Python)
- LLM: OpenAI Responses API
- Modelo predeterminado: `gpt-5.6-terra`
- Structured Outputs: JSON Schema
- UML: PlantUML
- Render SVG: Kroki configurable
- Base de datos: ninguna

## Requisitos

- Node.js 20 o superior
- Una API Key de OpenAI con acceso al modelo configurado
- Conexión a Internet para la API del LLM y para el render SVG público

## Instalación

1. Copia `.env.example` como `.env`.
2. Coloca tu API Key:

```env
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-5.6-terra
OPENAI_REASONING_EFFORT=medium
PORT=3000
UML_RENDERER_URL=https://kroki.io/plantuml/svg
```

3. Instala dependencias:

```bash
npm install
```

4. Ejecuta:

```bash
npm start
```

5. Abre:

```text
http://localhost:3000
```

Para desarrollo:

```bash
npm run dev
```

## Flujo UX

1. Seleccionar diagrama: casos de uso, clases, secuencia o actividad.
2. Elegir redacción informal o formal.
3. Redactar requerimientos.
4. GPT analiza y devuelve un modelo estructurado con JSON Schema.
5. El usuario revisa requisitos normalizados, elementos UML, supuestos y ambigüedades.
6. JavaScript convierte el modelo estructurado a PlantUML.
7. El servidor solicita el SVG al renderizador UML.
8. El usuario puede refinar el modelo con una instrucción adicional y exportar `.puml` o `.svg`.

## Seguridad

La API Key **no se coloca en `public/js/app.js` ni en HTML**. Permanece en `.env` y las llamadas a OpenAI se realizan desde Node.js. Esto evita exponer la credencial a cualquier usuario que abra las herramientas de desarrollo del navegador.

## Privacidad del renderizado UML

La configuración predeterminada utiliza `https://kroki.io/plantuml/svg` para convertir PlantUML a SVG. Esto significa que el código PlantUML se envía a un servicio externo. Para información confidencial, cambia `UML_RENDERER_URL` por un renderizador Kroki/PlantUML alojado por tu organización.

## Persistencia

La V1 no utiliza base de datos. El estado vive en la sesión del navegador. Esto mantiene el proyecto centrado en integración LLM, validación estructurada y generación UML.
