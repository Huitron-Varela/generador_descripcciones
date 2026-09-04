import OpenAI from 'openai';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const model = process.env.OPENAI_MODEL || 'gpt-5.6-terra';
const reasoningEffort = process.env.OPENAI_REASONING_EFFORT || 'medium';

const schema = {
  type: 'object',
  additionalProperties: false,
  required: [
    'diagramType', 'systemName', 'summary', 'confidence', 'normalizedRequirements',
    'assumptions', 'ambiguities', 'actors', 'useCases', 'classes', 'relationships',
    'participants', 'messages', 'activities', 'activityEdges'
  ],
  properties: {
    diagramType: { type: 'string', enum: ['use_case', 'class', 'sequence', 'activity'] },
    systemName: { type: 'string' },
    summary: { type: 'string' },
    confidence: { type: 'integer', minimum: 0, maximum: 100 },
    normalizedRequirements: { type: 'array', items: { type: 'string' } },
    assumptions: { type: 'array', items: { type: 'string' } },
    ambiguities: { type: 'array', items: { type: 'string' } },
    actors: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'name', 'description'],
        properties: { id: { type: 'string' }, name: { type: 'string' }, description: { type: 'string' } }
      }
    },
    useCases: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'name', 'description', 'actorIds', 'includes', 'extends'],
        properties: {
          id: { type: 'string' }, name: { type: 'string' }, description: { type: 'string' },
          actorIds: { type: 'array', items: { type: 'string' } },
          includes: { type: 'array', items: { type: 'string' } },
          extends: { type: 'array', items: { type: 'string' } }
        }
      }
    },
    classes: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'name', 'attributes', 'methods'],
        properties: {
          id: { type: 'string' }, name: { type: 'string' },
          attributes: { type: 'array', items: { type: 'string' } },
          methods: { type: 'array', items: { type: 'string' } }
        }
      }
    },
    relationships: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['sourceId', 'targetId', 'type', 'label', 'sourceMultiplicity', 'targetMultiplicity'],
        properties: {
          sourceId: { type: 'string' }, targetId: { type: 'string' },
          type: { type: 'string', enum: ['association', 'aggregation', 'composition', 'inheritance', 'dependency'] },
          label: { type: 'string' }, sourceMultiplicity: { type: 'string' }, targetMultiplicity: { type: 'string' }
        }
      }
    },
    participants: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'name', 'kind'],
        properties: { id: { type: 'string' }, name: { type: 'string' }, kind: { type: 'string', enum: ['actor', 'participant', 'boundary', 'control', 'entity', 'database'] } }
      }
    },
    messages: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['fromId', 'toId', 'label', 'messageType', 'order'],
        properties: {
          fromId: { type: 'string' }, toId: { type: 'string' }, label: { type: 'string' },
          messageType: { type: 'string', enum: ['sync', 'async', 'return'] }, order: { type: 'integer', minimum: 1 }
        }
      }
    },
    activities: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'label', 'type'],
        properties: { id: { type: 'string' }, label: { type: 'string' }, type: { type: 'string', enum: ['start', 'action', 'decision', 'end'] } }
      }
    },
    activityEdges: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['sourceId', 'targetId', 'condition'],
        properties: { sourceId: { type: 'string' }, targetId: { type: 'string' }, condition: { type: 'string' } }
      }
    }
  }
};

const baseInstructions = `Eres un analista senior de ingeniería de software especializado en UML y especificación de requisitos.\n\nTu tarea es transformar requerimientos escritos por una persona en un modelo UML estructurado y conservador.\nReglas:\n- No inventes funcionalidades que no estén razonablemente soportadas por el texto.\n- Si necesitas asumir algo para cerrar el modelo, decláralo en assumptions.\n- Registra información incompleta o contradictoria en ambiguities.\n- normalizedRequirements debe reescribir los requerimientos de manera clara, verificable y profesional.\n- Los IDs deben ser cortos, únicos y estables dentro de la respuesta.\n- Completa especialmente las estructuras correspondientes al diagramType solicitado y deja vacías las estructuras no aplicables.\n- Para casos de uso, identifica actores, casos, asociaciones e include/extend solo cuando exista fundamento.\n- Para clases, prioriza conceptos del dominio, atributos, operaciones y multiplicidades justificables.\n- Para secuencia, representa un escenario principal coherente y ordena los mensajes.\n- Para actividad, crea un flujo completo con inicio y fin; usa decisiones solo cuando el requisito exprese alternativas o condiciones.\n- confidence mide la confianza de 0 a 100 sobre la fidelidad del modelo respecto al texto, no la calidad estética.`;

export async function analyzeRequirements({ diagramType, writingMode, requirements }) {
  const input = `TIPO DE DIAGRAMA: ${diagramType}\nTIPO DE REDACCIÓN: ${writingMode}\n\nREQUERIMIENTO:\n${requirements}\n\nAnaliza el requerimiento y devuelve exclusivamente la estructura solicitada.`;
  const response = await client.responses.create({
    model,
    reasoning: { effort: reasoningEffort },
    instructions: baseInstructions,
    input,
    text: {
      format: {
        type: 'json_schema',
        name: 'uml_analysis',
        strict: true,
        schema
      }
    }
  });
  return parseResponse(response);
}

export async function refineAnalysis({ analysis, instruction }) {
  const input = `MODELO UML ACTUAL:\n${JSON.stringify(analysis, null, 2)}\n\nCAMBIO SOLICITADO POR EL USUARIO:\n${instruction}\n\nActualiza el modelo manteniendo intactos los elementos no afectados. No cambies diagramType. Devuelve el modelo completo actualizado.`;
  const response = await client.responses.create({
    model,
    reasoning: { effort: reasoningEffort },
    instructions: baseInstructions,
    input,
    text: {
      format: {
        type: 'json_schema',
        name: 'uml_analysis_refined',
        strict: true,
        schema
      }
    }
  });
  return parseResponse(response);
}

function parseResponse(response) {
  const text = response.output_text;
  if (!text) throw new Error('El modelo no devolvió contenido estructurado.');
  try {
    return JSON.parse(text);
  } catch {
    throw new Error('La respuesta estructurada del modelo no pudo interpretarse.');
  }
}
