import os
import sys

print("UML AI Studio - Verificación de entorno")
print("Python:", sys.version.split()[0])

ok = True
try:
    import flet as ft
    print("Flet:", getattr(ft, "__version__", "versión no reportada"))
    for attr in ["Border", "FilledButton", "OutlinedButton", "SegmentedButton", "DropdownOption", "InteractiveViewer"]:
        if not hasattr(ft, attr):
            print(f"[ERROR] Flet no expone ft.{attr}")
            ok = False
except Exception as ex:
    print("[ERROR] No se pudo importar Flet:", ex)
    ok = False

try:
    from google import genai  # noqa: F401
    print("Google GenAI: OK")
except Exception as ex:
    print("[ERROR] No se pudo importar google-genai:", ex)
    ok = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY", "").strip()
    print("GEMINI_API_KEY:", "configurada" if key else "NO configurada")
    if not key:
        ok = False
except Exception as ex:
    print("[ERROR] No se pudo leer .env:", ex)
    ok = False

print("\nRESULTADO:", "ENTORNO LISTO" if ok else "REVISAR MENSAJES ANTERIORES")
sys.exit(0 if ok else 1)
