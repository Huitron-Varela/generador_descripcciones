import 'dotenv/config';
import express from 'express';
import helmet from 'helmet';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { analyzeRequirements, refineAnalysis } from './src/services/openai.service.js';
import { toPlantUml } from './src/uml/plantuml.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = Number(process.env.PORT || 3000);

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'blob:'],
      connectSrc: ["'self'"]
    }
  }
}));
app.use(express.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname, 'public')));

function validateInput(body = {}) {
  const diagramType = String(body.diagramType || '').trim();
  const writingMode = String(body.writingMode || '').trim();
  const requirements = String(body.requirements || '').trim();
  const allowed = ['use_case', 'class', 'sequence', 'activity'];
  if (!allowed.includes(diagramType)) return 'Tipo de diagrama no válido.';
  if (!['formal', 'informal'].includes(writingMode)) return 'Tipo de redacción no válido.';
  if (requirements.length < 20) return 'Describe el requerimiento con al menos 20 caracteres.';
  if (requirements.length > 30000) return 'El requerimiento es demasiado extenso para esta versión.';
  return null;
}

app.get('/api/health', (_req, res) => {
  res.json({
    ok: true,
    model: process.env.OPENAI_MODEL || 'gpt-5.6-terra',
    apiKeyConfigured: Boolean(process.env.OPENAI_API_KEY)
  });
});

app.post('/api/analyze', async (req, res) => {
  try {
    const error = validateInput(req.body);
    if (error) return res.status(400).json({ error });
    if (!process.env.OPENAI_API_KEY) {
      return res.status(503).json({ error: 'OPENAI_API_KEY no está configurada en el servidor.' });
    }
    const analysis = await analyzeRequirements(req.body);
    const plantuml = toPlantUml(analysis);
    res.json({ analysis, plantuml });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: normalizeError(error) });
  }
});

app.post('/api/refine', async (req, res) => {
  try {
    const instruction = String(req.body?.instruction || '').trim();
    const analysis = req.body?.analysis;
    if (!analysis || typeof analysis !== 'object') return res.status(400).json({ error: 'Falta el análisis UML actual.' });
    if (instruction.length < 5) return res.status(400).json({ error: 'Describe el cambio que deseas realizar.' });
    if (instruction.length > 5000) return res.status(400).json({ error: 'La instrucción de refinamiento es demasiado extensa.' });
    const refined = await refineAnalysis({ analysis, instruction });
    const plantuml = toPlantUml(refined);
    res.json({ analysis: refined, plantuml });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: normalizeError(error) });
  }
});

app.post('/api/render', async (req, res) => {
  try {
    const plantuml = String(req.body?.plantuml || '').trim();
    if (!plantuml.startsWith('@startuml')) return res.status(400).json({ error: 'Código PlantUML no válido.' });
    if (plantuml.length > 100000) return res.status(400).json({ error: 'El diagrama excede el tamaño permitido.' });

    const renderer = process.env.UML_RENDERER_URL || 'https://kroki.io/plantuml/svg';
    const response = await fetch(renderer, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Accept': 'image/svg+xml' },
      body: plantuml,
      signal: AbortSignal.timeout(20000)
    });
    if (!response.ok) throw new Error(`El renderizador UML respondió ${response.status}.`);
    const svg = await response.text();
    res.type('image/svg+xml').send(svg);
  } catch (error) {
    console.error(error);
    res.status(502).json({ error: `No fue posible renderizar el UML: ${error.message}` });
  }
});

app.get('/{*splat}', (_req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

function normalizeError(error) {
  const status = error?.status || error?.response?.status;
  if (status === 401) return 'La API Key de OpenAI no es válida o no tiene acceso.';
  if (status === 429) return 'Se alcanzó el límite de uso de la API. Revisa cuota o facturación.';
  if (status === 404) return 'El modelo configurado no está disponible para esta cuenta.';
  return error?.message || 'Ocurrió un error inesperado al comunicarse con el LLM.';
}

app.listen(PORT, () => {
  console.log(`\nUML AI Studio Web disponible en http://localhost:${PORT}`);
  console.log(`Modelo: ${process.env.OPENAI_MODEL || 'gpt-5.6-terra'}`);
  console.log(`API Key: ${process.env.OPENAI_API_KEY ? 'configurada' : 'NO configurada'}\n`);
});
