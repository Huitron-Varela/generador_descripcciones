import asyncio
import flet as ft
from services.gemini_service import DEFAULT_REQUEST, GeminiProductService


def main(page: ft.Page):
    page.title = "Generador de Descripciones E-commerce"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F4F7FB"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.Padding(12, 10, 12, 18)

    # Eliminamos json_input del estado
    state = {
        "image_path": None,
        "result_text": "",
    }

    status_text = ft.Text("Sube una imagen para empezar", color="#526173", size=14)

    image_preview = ft.Image(src="", width=360, height=220, fit=ft.BoxFit.CONTAIN, visible=False)
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
        height=238,
        border=ft.Border.all(2, "#B8D8DD"),
        border_radius=16,
        bgcolor="#F7FCFC",
        alignment=ft.Alignment(0, 0),
    )

    # Resultados
    res_title = ft.Text(weight=ft.FontWeight.BOLD, size=21, color="#243447", selectable=True)
    res_desc = ft.Text(color="#526173", size=14, selectable=True)
    res_bullets = ft.Column(spacing=4)
    res_tags = ft.Text(italic=True, color="#1F7A8C", size=13, selectable=True)
    res_alt = ft.Text(color="#7A8797", size=13, selectable=True)
    copy_status = ft.Text(size=12, color="#26734D", visible=False)
    request_field = ft.TextField(
        value=DEFAULT_REQUEST,
        label="Solicitud para esta descripción",
        hint_text="¿Qué quieres que prepare la IA para esta imagen?",
        multiline=True,
        min_lines=2,
        max_lines=4,
        width=float("inf"),
        text_size=13,
        border_color="#B8D8DD",
        focused_border_color="#1F7A8C",
    )

    async def copy_result(e):
        if not state["result_text"]:
            copy_status.value = "Genera un resultado primero."
            copy_status.color = "#B45309"
        else:
            await page.clipboard.set(state["result_text"])
            copy_status.value = "Resultado copiado al portapapeles."
            copy_status.color = "#26734D"
        copy_status.visible = True
        page.update()

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
        status_text.value = "Analizando imagen y generando descripción..."
        status_text.color = "#1F7A8C"
        page.update()

        try:
            service = GeminiProductService()
            # Ya no enviamos el json_field.value
            result = await asyncio.to_thread(
                service.generate_description,
                state["image_path"],
                request_field.value,
            )

            # Mostramos resultados
            res_title.value = result.seo_title
            res_desc.value = result.descripcion_html
            res_bullets.controls = [
                ft.Row(
                    [ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#26734D", size=18),
                     ft.Text(b, color="#526173", expand=True)],
                    spacing=8,
                )
                for b in result.bullet_points
            ]
            res_tags.value = f"Tags: {', '.join(result.tags_busqueda)}"
            res_alt.value = f"Alt Text: {result.ui_metadata.alt_text}"
            state["result_text"] = "\n\n".join([
                result.seo_title,
                result.descripcion_html,
                "\n".join(f"- {bullet}" for bullet in result.bullet_points),
                res_tags.value,
                res_alt.value,
            ])

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
    copy_btn = ft.OutlinedButton(
        "Copiar resultado",
        icon=ft.Icons.CONTENT_COPY,
        on_click=copy_result,
        style=ft.ButtonStyle(color="#1F7A8C", side=ft.BorderSide(1, "#1F7A8C")),
    )

    def restore_default_request(e):
        request_field.value = DEFAULT_REQUEST
        page.update()

    restore_request_btn = ft.TextButton(
        "Restaurar solicitud",
        icon=ft.Icons.RESTORE,
        on_click=restore_default_request,
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
                ft.Row([copy_btn, copy_status], spacing=10),
            ],
            spacing=8,
        ),
        padding=14,
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
                            ft.Text("Convierte una fotografía en una ficha de producto lista para vender.", size=15,
                                    color="#526173"),
                        ],
                        spacing=7,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=42, color="#D97742"),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(4, 0, 4, 8),
        ),
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.IMAGE_OUTLINED, color="#1F7A8C", size=23),
                                    ft.Text("1. Sube la fotografía", size=18, weight=ft.FontWeight.BOLD,
                                            color="#243447")], spacing=10),
                            preview_area,
                            ft.Row([upload_btn], alignment=ft.MainAxisAlignment.CENTER),
                            status_text,
                        ],
                        spacing=8,
                    ),
                    padding=14, border_radius=12, bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#E1E8F0"), col={"sm": 12, "md": 6},
                ),
                # Reestructuramos esta columna para quitar el JSON
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME_MOTION, color="#1F7A8C", size=23),
                                    ft.Text("2. Genera el contenido", size=18, weight=ft.FontWeight.BOLD,
                                            color="#243447")], spacing=10),
                            ft.Text(
                                "Escribe qué necesitas para esta imagen y la IA generará el contenido.",
                                color="#526173", size=14),
                            request_field,
                            ft.Row([restore_request_btn], alignment=ft.MainAxisAlignment.END),
                            ft.Row([generate_btn], alignment=ft.MainAxisAlignment.START),
                        ],
                        spacing=10,
                    ),
                    padding=14, border_radius=12, bgcolor="#FFFFFF",
                    border=ft.Border.all(1, "#E1E8F0"), col={"sm": 12, "md": 6},
                ),
            ],
            spacing=10,
        ),
        ft.Container(content=results_panel, padding=ft.Padding(0, 10, 0, 0)),
    )


if __name__ == "__main__":
    ft.run(main)