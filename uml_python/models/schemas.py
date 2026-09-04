from typing import List
from pydantic import BaseModel, Field

class UIMetadata(BaseModel):
    alt_text: str = Field(description="Texto alternativo descriptivo de la imagen para accesibilidad.")

class ProductDescription(BaseModel):
    seo_title: str = Field(description="Título SEO atractivo y descriptivo.")
    descripcion_html: str = Field(description="Párrafo persuasivo en formato HTML (<p>, <strong>, etc.) que transforme características en beneficios.")
    bullet_points: List[str] = Field(description="Lista de viñetas resumiendo las especificaciones más importantes.")
    tags_busqueda: List[str] = Field(description="Etiquetas clave para posicionamiento SEO.")
    ui_metadata: UIMetadata