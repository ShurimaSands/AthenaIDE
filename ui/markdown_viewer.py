"""
Widget de visualización de Markdown.
Renderiza texto Markdown con formato visual.
"""
import re
from PySide6.QtWidgets import QTextBrowser
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from PySide6.QtCore import Qt, QTimer

from ui.theme import get_colors


class MarkdownViewer(QTextBrowser):
    """
    Widget que renderiza Markdown con formato visual.
    Soporta: headers, bold, italic, code, code blocks, lists y Message Bubbles.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(False)  # Cambiado a False para interceptar clic en anclas internamente
        self.anchorClicked.connect(self._on_anchor_clicked)
        self.setFont(QFont("Segoe UI", 11))
        # Auto-scroll robusto basado en el scrollbar
        self.verticalScrollBar().rangeChanged.connect(self._on_range_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_value_changed)
        self._auto_scroll = True
        
        # Estado de los bloques de pensamiento (colapsado o expandido)
        self._think_states = {}
        self._current_raw_markdown = ""

        self._apply_style()
        
    def _on_value_changed(self, value):
        """Detecta si el usuario hizo scroll manual hacia arriba para pausar el auto-scroll."""
        scrollbar = self.verticalScrollBar()
        # Si está en el fondo (con un margen de 15px), reactivar auto-scroll
        if value >= scrollbar.maximum() - 15:
            self._auto_scroll = True
        else:
            # El usuario scrolleó hacia arriba, detener auto-scroll
            self._auto_scroll = False

    def _on_range_changed(self, min, max):
        """Cuando se añade contenido y el rango crece, scrollea al fondo si auto_scroll está activo."""
        if self._auto_scroll:
            self.verticalScrollBar().setValue(max)
    
    def _apply_style(self):
        """Aplica estilos basados en el tema actual."""
        c = get_colors()
        self.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {c['bg_primary']};  /* Cambiado a primario para mejor contraste de burbujas */
                color: {c['text_primary']};
                border: none; /* Quitamos borde feo */
                padding: 16px;
            }}
        """)
    
    def set_markdown(self, text: str):
        """Convierte Markdown a HTML y lo muestra."""
        self._current_raw_markdown = text
        
        # Comprobar si debemos mantener el auto-scroll antes de actualizar
        scrollbar = self.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 15:
            self._auto_scroll = True
            
        html = self._markdown_to_html(text)
        self.setHtml(html)
        
        # Forzamos mover el cursor al final para ayudar al layout rendering
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
    
    def append_markdown(self, text: str):
        """Añade texto Markdown al final."""
        self.set_markdown(self._current_raw_markdown + text)
    
    def append_text(self, text: str):
        """Añade texto plano al final (para streaming)."""
        self._current_raw_markdown += text
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        
    def _on_anchor_clicked(self, url):
        """Maneja clics en enlaces."""
        url_str = url.toString()
        if url_str.startswith("think_toggle:"):
            # Es un botón de razonamiento
            idx = int(url_str.split(":")[1])
            # Cambiar estado
            self._think_states[idx] = not self._think_states.get(idx, False)
            # Re-renderizar completo para aplicar el cambio
            self.set_markdown(self._current_raw_markdown)
        else:
            # Enlace externo normal, abrir en navegador
            import webbrowser
            webbrowser.open(url_str)
            
    def _markdown_to_html(self, text: str) -> str:
        """Convierte Markdown básico a HTML."""
        c = get_colors()
        
        # Estilos CSS inline
        css = f"""
        <style>
            body {{
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: {c['text_primary']};
                margin: 0;
                padding: 0;
            }}
            h1 {{ color: {c['accent_purple']}; font-size: 20px; margin: 16px 0 8px 0; border-bottom: 1px solid {c['border']}; padding-bottom: 4px; }}
            h2 {{ color: {c['accent_blue']}; font-size: 17px; margin: 14px 0 6px 0; }}
            h3 {{ color: {c['accent_teal']}; font-size: 15px; margin: 12px 0 4px 0; }}
            code {{
                background-color: {c['bg_hover']};
                color: {c['accent_orange']};
                padding: 3px 6px;
                border-radius: 4px;
                font-family: 'Consolas', 'JetBrains Mono', monospace;
                font-size: 12.5px;
            }}
            pre {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 14px;
                overflow-x: auto;
                margin: 12px 0;
            }}
            pre code {{
                background: none;
                padding: 0;
                color: {c['text_primary']};
            }}
            strong {{ color: {c['accent_yellow']}; }}
            em {{ color: {c['text_secondary']}; font-style: italic; }}
            ul, ol {{ margin: 8px 0; padding-left: 24px; }}
            li {{ margin: 4px 0; }}
            blockquote {{
                border-left: 4px solid {c['accent_purple']};
                background-color: {c['bg_secondary']};
                padding: 10px 14px;
                border-radius: 4px;
                margin: 12px 0;
                color: {c['text_secondary']};
            }}
            hr {{ border: none; border-top: 1px solid {c['border']}; margin: 20px 0; }}
            a {{ color: {c['accent_blue']}; text-decoration: none; }}
            
            /* Enhanced Bubble Styles */
            .bubble-container {{ margin-bottom: 18px; display: flex; flex-direction: column; }}
            
            .user-bubble {{
                background-color: {c['bg_selected']};
                color: {c['text_primary']};
                border-radius: 12px;
                border-top-right-radius: 2px;
                padding: 12px 16px;
                margin-left: 20px;
                margin-bottom: 8px;
                align-self: flex-end;
            }}
            
            .athena-bubble {{
                background-color: transparent;
                color: {c['text_primary']};
                margin-right: 10px;
                margin-bottom: 12px;
                padding: 8px 0;
            }}
            
            .athena-header {{
                color: {c['accent_purple']};
                font-weight: bold;
                font-size: 15px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
            }}
            
            .user-header {{
                color: {c['accent_green']};
                font-weight: bold;
                font-size: 15px;
                margin-bottom: 8px;
            }}
            
            /* Styles for <think> blocks (interactive python approach) */
            .think-toggle {{
                color: {c['text_muted']};
                font-weight: bold;
                text-decoration: none;
                display: block;
                padding: 6px 10px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin: 10px 0 2px 0;
            }}
            .think-toggle:hover {{
                color: {c['text_primary']};
                background-color: rgba(255, 255, 255, 0.1);
            }}
            .think-content {{
                color: {c['text_secondary']};
                font-size: 13.5px;
                font-style: italic;
                padding: 10px;
                border-left: 2px solid {c['text_muted']};
                margin-left: 4px;
                margin-bottom: 10px;
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 0 4px 4px 0;
            }}
            
        </style>
        """
        
        html = text
        
        # Encontrar y extraer los bloques "<think>" temporalmente
        think_blocks = []
        def extract_think_blocks(match):
            content = match.group(1)
            idx = len(think_blocks)
            think_blocks.append(content)
            return f"__THINK_BLOCK_{idx}__"
            
        html = re.sub(r'<think>(.*?)</think>', extract_think_blocks, html, flags=re.DOTALL | re.IGNORECASE)
        # Y si ya venía escapado del LLM o parser
        html = re.sub(r'&lt;think&gt;(.*?)&lt;/think&gt;', extract_think_blocks, html, flags=re.DOTALL | re.IGNORECASE)
        
        # Escapar HTML peligroso restante
        html = html.replace("&", "&amp;")
        html = html.replace("<", "&lt;")
        html = html.replace(">", "&gt;")
        
        # Re-insertar bloques de think usando botones ancla de pyqt interactivos
        def restore_think_blocks(match):
            idx = int(match.group(1))
            content = think_blocks[idx]
            
            # Limpiar HTML dentro del think por seguridad ya que me salté el escape global
            content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            is_expanded = self._think_states.get(idx, False)
            if is_expanded:
                # Mostrar botón para "Ocultar" y mostrar el texto abajo
                # Reemplazamos saltos de linea dentro del content
                content_html = content.replace('\n\n', '<br><br>').replace('\n', '<br>')
                return f'<a href="think_toggle:{idx}" class="think-toggle">[-] Ocultar Razonamiento 🧠</a><div class="think-content">{content_html}</div>'
            else:
                # Mostrar solo botón para "Mostrar"
                return f'<a href="think_toggle:{idx}" class="think-toggle">[+] Mostrar Razonamiento 🧠</a>'
                
        html = re.sub(r'__THINK_BLOCK_(\d+)__', restore_think_blocks, html)
        
        # Code blocks (```) - procesar primero
        def replace_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)
            return f'<pre><code class="language-{lang}">{code}</code></pre>'
        
        html = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, html, flags=re.DOTALL)
        
        # Inline code (`)
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold y Italic
        html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Listas
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
        
        # Agrupar <li> en <ul>
        html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', html)
        
        # Blockquotes
        html = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # Horizontal rules
        html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Extraer mensajes en burbujas
        # Dividir por los tokens especiales **Tú**: y **Athena**:
        parts = re.split(r'(\*\*Tú\*\*:|\*\*Athena\*\*:)', html)
        
        structured_html = ""
        current_speaker = None
        
        for part in parts:
            if part == "**Tú**:":
                if current_speaker == "athena":
                    structured_html += "</div>" # close athena bubble
                current_speaker = "user"
                structured_html += f'<div class="bubble-container"><div class="user-bubble"><div class="user-header">Tú</div>'
            elif part == "**Athena**:":
                if current_speaker == "user":
                    structured_html += "</div></div>" # close user bubble & container
                elif current_speaker == "athena":
                    structured_html += "</div>"
                current_speaker = "athena"
                structured_html += f'<div class="bubble-container"><div class="athena-bubble"><div class="athena-header">🦉 Athena</div>'
            elif part.strip() != "":
                # Convertir blockquote en divs para que no se arruinen en las burbujas
                part = part.strip()
                if part.startswith("---\n\n**📋 Instrucción**:"):
                    # Instrucción de Plan (System) - treated similar to user
                    if current_speaker:
                        structured_html += "</div></div>" if current_speaker == "user" else "</div>"
                    current_speaker = None
                    text_only = part.replace("---\n\n**📋 Instrucción**:", "").strip()
                    structured_html += f'<hr><div class="bubble-container"><div class="user-bubble"><div class="user-header">📋 Plan Solicitado</div>{text_only}</div></div>'
                else:
                    if part.startswith("---"):
                        part = part.replace("---", "<hr>")
                    
                    # Limpiar line breaks molestos que rompen div styling
                    part_cleaned = re.sub(r'\n\n+', '</p><p>', f"<p>{part}</p>")
                    structured_html += part_cleaned
        
        if current_speaker == "user":
            structured_html += "</div></div>"
        elif current_speaker == "athena":
            structured_html += "</div></div>"
        
        # Sustituir emojis codificados rotos de read original si los hay
        html = structured_html
        
        # Párrafos (líneas vacías) - Only for text outside parts logic
        if not parts or len(parts) == 1:
             html = re.sub(r'\n\n+', '</p><p>', html)
        
        # Emojis de estado
        html = html.replace("✅", "✅")
        html = html.replace("❌", "❌")
        html = html.replace("⚠️", "⚠️")
        html = html.replace("📋", "📋")
        html = html.replace("🦉", "🦉")
        
        return f"<html><head>{css}</head><body><p>{html}</p></body></html>"
    
    def refresh_style(self):
        """Refresca los estilos cuando cambia el tema."""
        self._apply_style()
        # Re-renderizar contenido actual
        current = self.toPlainText()
        if current:
            self.set_markdown(current)
