import asyncio
import flet as ft
from services.gemini_service import GeminiProductService

def main(page: ft.Page):
    page.title = "Generador de Descripciones E-commerce"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F4F7FB"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.Padding(24, 20, 24, 36)

    state = {
        "image_path": None,
        "json_input": '{\n  "producto": "Camisa Casual",\n  "color_base": "Azul marino",\n  "material": "100% Algodón"\n}'
    }

    status_text = ft.Text("Sube una imagen para empezar", color="#526173", size=14)
    
    json_field = ft.TextField(
        label="Datos del producto (JSON)",
        value=state["json_input"],
        multiline=True,
        min_lines=6,
        max_lines=8,
        border_color="#D7DFEA",
        focused_border_color="#1F7A8C",
        cursor_color="#1F7A8C",
        bgcolor="#FFFFFF",
        text_size=14,
        expand=True,
    )

    image_preview = ft.Image(src="", width=360, height=280, fit=ft.BoxFit.CONTAIN, visible=False)
    preview_area = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, size=52, color="#1F7A8C"),
                ft.Text("Tu producto empieza aquí", size=17, weight=ft.FontWeight.BOLD, color="#243447"),
                ft.Text("JPG, PNG o WEBP", size=13, color="#7A8797"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        height=300,
        border=ft.Border.all(2, "#B8D8DD"),
        border_radius=16,
        bgcolor="#F7FCFC",
        alignment=ft.Alignment(0, 0),
    )
    
    # Resultados
    res_title = ft.Text(weight=ft.FontWeight.BOLD, size=21, color="#243447")
    res_desc = ft.Text(color="#526173", size=14)
    res_bullets = ft.Column(spacing=6)
    res_tags = ft.Text(italic=True, color="#1F7A8C", size=13)
    res_alt = ft.Text(color="#7A8797", size=13)

    # --- Selector de Archivos ---
    async def pick_image(e):
        files = await file_picker.pick_files(allow_multiple=False)
        if files:
            selected_file = files[0]
            file_path = selected_file.path
            state["image_path"] = file_path
            image_preview.src = file_path
            image_preview.visible = True
            preview_area.content = image_preview
            status_text.value = f"Imagen cargada: {selected_file.name}"
            status_text.color = "#26734D"
            page.update()

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # --- Generación ---
    async def generate_content(e):
        if not state["image_path"]:
            status_text.value = "Selecciona una imagen antes de generar el contenido."
            status_text.color = "#B45309"
            page.update()
            return

        generate_btn.disabled = True
        status_text.value = "Generando descripción persuasiva con Gemini..."
        status_text.color = "#1F7A8C"
        page.update()

        try:
            service = GeminiProductService()
            # Ejecutamos en un hilo para no bloquear la UI de Flet
            result = await asyncio.to_thread(
                service.generate_description, 
                state["image_path"], 
                json_field.value
            )
            
            # Mostramos resultados
            res_title.value = result.seo_title
            res_desc.value = result.descripcion_html
            res_bullets.controls = [
                ft.Row(
                    [ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#26734D", size=18), ft.Text(b, color="#526173", expand=True)],
                    spacing=8,
                )
                for b in result.bullet_points
            ]
            res_tags.value = f"Tags: {', '.join(result.tags_busqueda)}"
            res_alt.value = f"Alt Text: {result.ui_metadata.alt_text}"
            
            status_text.value = "Descripción generada correctamente."
            status_text.color = "#26734D"
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = "#B42318"
        finally:
            generate_btn.disabled = False
            page.update()

    generate_btn = ft.FilledButton(
        "Generar descripción",
        icon=ft.Icons.AUTO_AWESOME,
        on_click=generate_content,
        style=ft.ButtonStyle(
            bgcolor="#D97742",
            color="#FFFFFF",
            padding=ft.Padding(20, 14, 20, 14),
        ),
    )
    upload_btn = ft.OutlinedButton(
        "Elegir imagen",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=pick_image,
        style=ft.ButtonStyle(color="#1F7A8C", side=ft.BorderSide(1, "#1F7A8C")),
    )

    # --- Composición ---
    results_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [ft.Icon(ft.Icons.AUTO_AWESOME, color="#D97742", size=22),
                     ft.Text("Resultados generados", size=18, weight=ft.FontWeight.BOLD, color="#243447")],
                    spacing=10,
                ),
                ft.Divider(color="#E4EAF1", height=1),
                res_title, res_desc, res_bullets, res_tags, res_alt,
            ],
            spacing=12,
        ),
        padding=24,
        border_radius=16,
        bgcolor="#FFFFFF",
        border=ft.Border.all(1, "#E1E8F0"),
    )

    page.add(
        ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("ESTUDIO DE PRODUCTO", size=12, color="#D97742", weight=ft.FontWeight.BOLD),
                            ft.Text("Generador de contenido", size=30, weight=ft.FontWeight.BOLD, color="#243447"),
                            ft.Text("Convierte una fotografía en una ficha de producto lista para vender.", size=15, color="#526173"),
                        ],
                        spacing=7,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=42, color="#D97742"),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(4, 0, 4, 20),
        ),
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.IMAGE_OUTLINED, color="#1F7A8C", size=23),
                                    ft.Text("1. Sube la fotografía", size=18, weight=ft.FontWeight.BOLD, color="#243447")], spacing=10),
                            preview_area,
                            ft.Row([upload_btn], alignment=ft.MainAxisAlignment.CENTER),
                            status_text,
                        ],
                        spacing=14,
                    ),
                    padding=24, border_radius=16, bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#E1E8F0"), col={"sm": 12, "md": 6},
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.DATA_OBJECT, color="#1F7A8C", size=23),
                                    ft.Text("2. Describe el producto", size=18, weight=ft.FontWeight.BOLD, color="#243447")], spacing=10),
                            json_field,
                            ft.Row([generate_btn], alignment=ft.MainAxisAlignment.END),
                        ],
                        spacing=16,
                    ),
                    padding=24, border_radius=16, bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#E1E8F0"), col={"sm": 12, "md": 6},
                ),
            ],
            spacing=18,
        ),
        ft.Container(content=results_panel, padding=ft.Padding(0, 18, 0, 0)),
    )

if __name__ == "__main__":
    ft.run(main)