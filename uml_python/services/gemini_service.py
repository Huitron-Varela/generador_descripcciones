import os
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv
from models.schemas import ProductDescription

load_dotenv()

class GeminiProductService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Falta GEMINI_API_KEY.")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.client = genai.Client(api_key=api_key)

    def generate_description(self, image_path: str, json_data: str) -> ProductDescription:
        # Abrimos la imagen para enviarla al modelo
        image = Image.open(image_path)
        
        prompt = f"""
        Actúa como el motor central de redacción publicitaria (copywriter) para un e-commerce.
        Analiza la fotografía adjunta del producto y el siguiente bloque de datos JSON con las especificaciones técnicas:
        
        DATOS DEL PRODUCTO:
        {json_data}
        
        INSTRUCCIONES:
        1. Redacta un párrafo persuasivo en HTML que transforme características técnicas en beneficios claros.
        2. Genera listas de viñetas (bullet points) que resuman las especificaciones más importantes.
        3. Integra palabras clave relevantes para optimizar el SEO.
        4. No inventes características que no se vean en la imagen o no estén en el JSON (evita alucinaciones).
        """

        response = self.client.models.generate_content(
            model=self.model,
            # Enviamos la imagen y el texto (Multimodal)
            contents=[image, prompt], 
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