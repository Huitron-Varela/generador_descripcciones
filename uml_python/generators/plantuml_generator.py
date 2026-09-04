from models.schemas import UMLAnalysis


def esc(text: str) -> str:
    return str(text).replace('"', "'").replace("\n", " ").strip()


class PlantUMLGenerator:
    @staticmethod
    def generate(data: UMLAnalysis) -> str:
        return {
            "use_case": PlantUMLGenerator.use_case,
            "class": PlantUMLGenerator.class_diagram,
            "sequence": PlantUMLGenerator.sequence,
            "activity": PlantUMLGenerator.activity,
        }[data.diagram_type](data)

    @staticmethod
    def _header(data: UMLAnalysis):
        return [
            "@startuml",
            "skinparam backgroundColor transparent",
            "skinparam shadowing false",
            "skinparam defaultFontName Arial",
            "skinparam defaultFontSize 14",
            "skinparam roundcorner 10",
            f'title {esc(data.system_name)}',
        ]

    @staticmethod
    def use_case(data: UMLAnalysis) -> str:
        lines = PlantUMLGenerator._header(data) + ["left to right direction", "skinparam packageStyle rectangle"]
        actors, cases = {}, {}
        for i, actor in enumerate(data.actors):
            actors[actor] = f"A{i}"
            lines.append(f'actor "{esc(actor)}" as A{i}')
        lines.append(f'rectangle "{esc(data.system_name)}" {{')
        for i, uc in enumerate(data.use_cases):
            cases[uc] = f"UC{i}"
            lines.append(f'  usecase "{esc(uc)}" as UC{i}')
        lines.append("}")
        for rel in data.relationships:
            if rel.source in actors and rel.target in cases:
                lines.append(f"{actors[rel.source]} --> {cases[rel.target]}")
            elif rel.target in actors and rel.source in cases:
                lines.append(f"{actors[rel.target]} --> {cases[rel.source]}")
        lines.append("@enduml")
        return "\n".join(lines)

    @staticmethod
    def class_diagram(data: UMLAnalysis) -> str:
        lines = PlantUMLGenerator._header(data) + ["skinparam classAttributeIconSize 0", "hide empty members"]
        known = set()
        for c in data.classes:
            alias = PlantUMLGenerator.alias(c.name)
            known.add(c.name)
            lines.append(f'class "{esc(c.name)}" as {alias} {{')
            for a in c.attributes:
                lines.append(f"  - {esc(a)}")
            for m in c.methods:
                lines.append(f"  + {esc(m)}")
            lines.append("}")
        symbols = {"association": "--", "aggregation": "o--", "composition": "*--", "inheritance": "--|>", "dependency": "..>"}
        for r in data.relationships:
            if r.source not in known or r.target not in known:
                continue
            s, t = PlantUMLGenerator.alias(r.source), PlantUMLGenerator.alias(r.target)
            sym = symbols.get(r.type.lower(), "--")
            ms = f' "{esc(r.multiplicity_source)}"' if r.multiplicity_source else ""
            mt = f' "{esc(r.multiplicity_target)}"' if r.multiplicity_target else ""
            label = f" : {esc(r.label)}" if r.label else ""
            lines.append(f"{s}{ms} {sym} {mt}{t}{label}")
        lines.append("@enduml")
        return "\n".join(lines)

    @staticmethod
    def sequence(data: UMLAnalysis) -> str:
        lines = PlantUMLGenerator._header(data) + ["autonumber"]
        participants = set(data.participants)
        for p in data.participants:
            lines.append(f'participant "{esc(p)}" as {PlantUMLGenerator.alias(p)}')
        for m in data.messages:
            if m.source not in participants:
                lines.append(f'participant "{esc(m.source)}" as {PlantUMLGenerator.alias(m.source)}')
                participants.add(m.source)
            if m.target not in participants:
                lines.append(f'participant "{esc(m.target)}" as {PlantUMLGenerator.alias(m.target)}')
                participants.add(m.target)
            arrow = "-->>" if m.response else "->>"
            lines.append(f"{PlantUMLGenerator.alias(m.source)} {arrow} {PlantUMLGenerator.alias(m.target)} : {esc(m.message)}")
        lines.append("@enduml")
        return "\n".join(lines)

    @staticmethod
    def activity(data: UMLAnalysis) -> str:
        lines = PlantUMLGenerator._header(data) + ["start"]
        for node in data.activities:
            if node.kind in ("start", "end"):
                continue
            if node.kind == "decision":
                yes = esc(node.yes_action or "Continuar")
                no = esc(node.no_action or "Revisar condición")
                lines += [f"if ({esc(node.text)}) then (Sí)", f":{yes};", "else (No)", f":{no};", "endif"]
            else:
                lines.append(f":{esc(node.text)};")
        lines += ["stop", "@enduml"]
        return "\n".join(lines)

    @staticmethod
    def alias(name: str) -> str:
        clean = "".join(ch for ch in str(name) if ch.isalnum())
        if clean and clean[0].isdigit():
            clean = "E" + clean
        return clean or "Elemento"
