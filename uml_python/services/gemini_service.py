import os
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv
from models.schemas import ProductDescription

load_dotenv()

DEFAULT_PROMPT = """Actúa como un Copywriter Senior especializado en e-commerce y analista de producto.
Tu objetivo es analizar meticulosamente la fotografía adjunta y deducir sus características, materiales, estilo y público objetivo basándote ÚNICAMENTE en la evidencia visual.

INSTRUCCIONES:
1. Análisis Visual: Identifica el tipo de producto, colores principales, texturas aparentes, forma, y posibles usos o contextos.
2. Redacción Persuasiva (HTML): Redacta un párrafo comercial y atractivo que transforme lo que ves en la imagen en beneficios claros para el comprador.
3. Especificaciones (Viñetas): Genera una lista de bullet points con las características técnicas que se puedan inferir de la imagen (ej. "Diseño ergonómico", "Acabado mate", "Corte ajustado").
4. SEO: Integra palabras clave de intención de compra relevantes para este tipo de producto.
5. Regla de Oro: No inventes datos absolutos que no se puedan ver (como medidas exactas, peso en gramos o certificaciones invisibles). Mantente fiel a lo que la imagen demuestra."""

DEFAULT_REQUEST = "Genera una ficha de producto atractiva y lista para publicar en una tienda online."


class GeminiProductService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Falta GEMINI_API_KEY.")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.client = genai.Client(api_key=api_key)

    def generate_description(
        self,
        image_path: str,
        prompt: str = DEFAULT_PROMPT,
        request: str = DEFAULT_REQUEST,
    ) -> ProductDescription:
        # Abrimos la imagen para enviarla al modelo
        image = Image.open(image_path)
        
        prompt = prompt.strip() or DEFAULT_PROMPT
        request = request.strip() or DEFAULT_REQUEST
        full_prompt = f"{prompt}\n\nSOLICITUD PARA ESTA IMAGEN:\n{request}"

        response = self.client.models.generate_content(
            model=self.model,
            # Enviamos la imagen y el texto (Multimodal)
            contents=[image, full_prompt], 
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ProductDescription,
                # Temperatura equilibrada para creatividad sin perder precisión
                temperature=0.5, 
            ),
        )
        
        if not response.text:
            raise RuntimeError("Gemini no devolvió contenido.")
            
        return ProductDescription.model_validate_json(response.text)