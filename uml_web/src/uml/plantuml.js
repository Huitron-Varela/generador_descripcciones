const safe = (value = '') => String(value).replace(/[\r\n]+/g, ' ').replace(/"/g, "'").trim();
const alias = (id = '') => String(id).replace(/[^a-zA-Z0-9_]/g, '_') || 'item';

export function toPlantUml(model) {
  const builders = {
    use_case: useCaseDiagram,
    class: classDiagram,
    sequence: sequenceDiagram,
    activity: activityDiagram
  };
  const builder = builders[model.diagramType];
  if (!builder) throw new Error('Tipo UML no compatible.');
  return builder(model);
}

function header(model) {
  return [
    '@startuml',
    'skinparam backgroundColor transparent',
    'skinparam shadowing false',
    'skinparam roundcorner 12',
    'skinparam defaultFontName Arial',
    'skinparam defaultFontSize 14',
    'skinparam ArrowColor #52606D',
    'skinparam BorderColor #CBD5E1',
    'skinparam FontColor #172033',
    'skinparam packageStyle rectangle',
    `title ${safe(model.systemName || 'Modelo UML')}`
  ];
}

function useCaseDiagram(m) {
  const out = header(m);
  out.push('left to right direction', 'skinparam actorStyle awesome');
  for (const actor of m.actors) out.push(`actor "${safe(actor.name)}" as ${alias(actor.id)}`);
  out.push(`rectangle "${safe(m.systemName || 'Sistema')}" {`);
  for (const uc of m.useCases) out.push(`  usecase "${safe(uc.name)}" as ${alias(uc.id)}`);
  out.push('}');
  const actors = new Set(m.actors.map(a => a.id));
  const cases = new Set(m.useCases.map(u => u.id));
  for (const uc of m.useCases) {
    for (const actorId of uc.actorIds) if (actors.has(actorId)) out.push(`${alias(actorId)} --> ${alias(uc.id)}`);
    for (const target of uc.includes) if (cases.has(target)) out.push(`${alias(uc.id)} ..> ${alias(target)} : <<include>>`);
    for (const target of uc.extends) if (cases.has(target)) out.push(`${alias(uc.id)} ..> ${alias(target)} : <<extend>>`);
  }
  out.push('@enduml');
  return out.join('\n');
}

function classDiagram(m) {
  const out = header(m);
  for (const c of m.classes) {
    out.push(`class "${safe(c.name)}" as ${alias(c.id)} {`);
    for (const a of c.attributes) out.push(`  ${safe(a)}`);
    if (c.attributes.length && c.methods.length) out.push('  --');
    for (const method of c.methods) out.push(`  ${safe(method)}`);
    out.push('}');
  }
  const ids = new Set(m.classes.map(c => c.id));
  const arrows = { association: '--', aggregation: 'o--', composition: '*--', inheritance: '<|--', dependency: '..>' };
  for (const r of m.relationships) {
    if (!ids.has(r.sourceId) || !ids.has(r.targetId)) continue;
    const arrow = arrows[r.type] || '--';
    const left = r.sourceMultiplicity ? ` "${safe(r.sourceMultiplicity)}"` : '';
    const right = r.targetMultiplicity ? `"${safe(r.targetMultiplicity)}" ` : '';
    const label = r.label ? ` : ${safe(r.label)}` : '';
    if (r.type === 'inheritance') out.push(`${alias(r.targetId)} <|-- ${alias(r.sourceId)}${label}`);
    else out.push(`${alias(r.sourceId)}${left} ${arrow} ${right}${alias(r.targetId)}${label}`);
  }
  out.push('@enduml');
  return out.join('\n');
}

function sequenceDiagram(m) {
  const out = header(m);
  const syntax = { actor: 'actor', participant: 'participant', boundary: 'boundary', control: 'control', entity: 'entity', database: 'database' };
  for (const p of m.participants) out.push(`${syntax[p.kind] || 'participant'} "${safe(p.name)}" as ${alias(p.id)}`);
  const ids = new Set(m.participants.map(p => p.id));
  const sorted = [...m.messages].sort((a, b) => a.order - b.order);
  const arrows = { sync: '->', async: '->>', return: '-->' };
  for (const msg of sorted) if (ids.has(msg.fromId) && ids.has(msg.toId)) out.push(`${alias(msg.fromId)} ${arrows[msg.messageType] || '->'} ${alias(msg.toId)} : ${safe(msg.label)}`);
  out.push('@enduml');
  return out.join('\n');
}

function activityDiagram(m) {
  const out = header(m);
  const activities = new Map(m.activities.map(a => [a.id, a]));
  const outgoing = new Map();
  for (const e of m.activityEdges) {
    if (!outgoing.has(e.sourceId)) outgoing.set(e.sourceId, []);
    outgoing.get(e.sourceId).push(e);
  }
  const start = m.activities.find(a => a.type === 'start') || m.activities[0];
  if (!start) return [...out, 'start', ':Sin actividades identificadas;', 'stop', '@enduml'].join('\n');

  out.push('start');
  const visited = new Set();
  let current = start;
  let guard = 0;
  while (current && guard++ < 100) {
    if (visited.has(current.id)) break;
    visited.add(current.id);
    if (current.type === 'action') out.push(`:${safe(current.label)};`);
    const edges = outgoing.get(current.id) || [];
    if (current.type === 'decision' && edges.length >= 2) {
      out.push(`if (${safe(current.label)}) then (${safe(edges[0].condition || 'Sí')})`);
      const a = activities.get(edges[0].targetId);
      if (a?.type === 'action') out.push(`  :${safe(a.label)};`);
      out.push(`else (${safe(edges[1].condition || 'No')})`);
      const b = activities.get(edges[1].targetId);
      if (b?.type === 'action') out.push(`  :${safe(b.label)};`);
      out.push('endif');
      const nextEdgesA = a ? outgoing.get(a.id) || [] : [];
      const nextEdgesB = b ? outgoing.get(b.id) || [] : [];
      const common = nextEdgesA.map(e => e.targetId).find(id => nextEdgesB.some(e => e.targetId === id));
      current = common ? activities.get(common) : undefined;
      continue;
    }
    if (current.type === 'end') break;
    current = edges[0] ? activities.get(edges[0].targetId) : undefined;
  }
  out.push('stop', '@enduml');
  return out.join('\n');
}
