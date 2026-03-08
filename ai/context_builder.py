"""
Constructor de contexto para Athena.
Recopila información del proyecto para incluir en los prompts.
Accede recursivamente a todos los archivos dentro de la carpeta del proyecto.
"""
import os
from typing import List, Optional, Dict
from project.project_manager import ProjectManager


class ContextBuilder:
    """
    Construye el contexto del proyecto para enviar a Athena.
    Recopila estructura, archivos relevantes y estado actual.
    Accede a archivos dentro de subcarpetas del proyecto.
    """
    
    # Extensiones que Athena puede procesar
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
        '.html', '.css', '.scss', '.md', '.txt', '.sh', '.bat', '.ps1',
        '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.rb',
        '.sql', '.xml', '.toml', '.ini', '.cfg', '.env', '.gitignore',
        '.dockerfile', '.vue', '.svelte', '.php', '.swift', '.kt'
    }
    
    # Directorios a excluir
    EXCLUDED_DIRS = {
        '__pycache__', 'node_modules', '.git', '.venv', 'venv',
        'env', '.idea', '.vscode', 'dist', 'build', '.athena_backups',
        '.next', '.nuxt', 'coverage', '.pytest_cache', '.mypy_cache',
        'egg-info', '.eggs', '.tox', 'htmlcov', '.cache'
    }
    
    # Archivos a excluir
    EXCLUDED_FILES = {
        '.DS_Store', 'Thumbs.db', '.gitkeep', 'package-lock.json',
        'yarn.lock', 'poetry.lock', 'Pipfile.lock'
    }
    
    # Límite de tamaño por archivo (caracteres)
    MAX_FILE_SIZE = 4000
    
    # Límite total de contexto
    MAX_CONTEXT_SIZE = 12000
    
    def __init__(self, project: ProjectManager):
        self.project = project
    
    def get_project_tree(self, max_depth: int = 6) -> str:
        """
        Genera el árbol de archivos del proyecto.
        Incluye subcarpetas recursivamente.
        """
        lines = []
        self._build_tree(self.project.root, "", 0, max_depth, lines)
        return "\n".join(lines)
    
    def _build_tree(self, path: str, prefix: str, depth: int, max_depth: int, lines: list):
        """Construye el árbol recursivamente."""
        if depth > max_depth:
            return
        
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return
        
        # Separar directorios y archivos
        dirs = []
        files = []
        
        for entry in entries:
            full_path = os.path.join(path, entry)
            
            if entry in self.EXCLUDED_FILES:
                continue
            if entry.startswith('.') and entry not in ('.env', '.gitignore'):
                continue
            
            if os.path.isdir(full_path):
                if entry not in self.EXCLUDED_DIRS:
                    dirs.append(entry)
            else:
                files.append(entry)
        
        # Añadir directorios primero
        for i, dir_name in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and len(files) == 0
            connector = "└── " if is_last_dir else "├── "
            lines.append(f"{prefix}{connector}📁 {dir_name}/")
            
            # Recursión
            new_prefix = prefix + ("    " if is_last_dir else "│   ")
            self._build_tree(
                os.path.join(path, dir_name),
                new_prefix,
                depth + 1,
                max_depth,
                lines
            )
        
        # Añadir archivos
        for i, file_name in enumerate(files):
            is_last = (i == len(files) - 1)
            connector = "└── " if is_last else "├── "
            
            ext = os.path.splitext(file_name)[1].lower()
            icon = self._get_file_icon(ext)
            lines.append(f"{prefix}{connector}{icon} {file_name}")
    
    def _get_file_icon(self, ext: str) -> str:
        """Retorna un icono según la extensión del archivo."""
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.jsx': '⚛️',
            '.tsx': '⚛️',
            '.json': '📋',
            '.html': '🌐',
            '.css': '🎨',
            '.md': '📝',
            '.txt': '📄',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.sql': '🗃️',
            '.sh': '🖥️',
            '.bat': '🖥️',
        }
        return icons.get(ext, '📄')
    
    def list_all_files(self, extensions: set = None) -> List[str]:
        """
        Lista todos los archivos del proyecto recursivamente.
        
        Args:
            extensions: Set de extensiones a incluir (None = todas las de código)
        
        Returns:
            Lista de rutas relativas
        """
        if extensions is None:
            extensions = self.CODE_EXTENSIONS
        
        files = []
        
        for root, dirs, filenames in os.walk(self.project.root):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS and not d.startswith('.')]
            
            for filename in filenames:
                if filename in self.EXCLUDED_FILES:
                    continue
                
                ext = os.path.splitext(filename)[1].lower()
                if ext in extensions or filename in ('.gitignore', '.env.example'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.project.root)
                    files.append(rel_path)
        
        return sorted(files)
    
    def read_file_safe(self, path: str) -> Optional[str]:
        """Lee un archivo de forma segura, respetando límites."""
        try:
            # Manejar rutas relativas y absolutas
            if os.path.isabs(path):
                full_path = path
                rel_path = os.path.relpath(path, self.project.root)
            else:
                full_path = os.path.join(self.project.root, path)
                rel_path = path
            
            if not os.path.exists(full_path):
                return None
            
            if not os.path.isfile(full_path):
                return None
            
            # Verificar que está dentro del proyecto
            if not full_path.startswith(self.project.root):
                return f"[Archivo fuera del proyecto: {path}]"
            
            # Verificar extensión
            ext = os.path.splitext(path)[1].lower()
            basename = os.path.basename(path)
            
            if ext not in self.CODE_EXTENSIONS and basename not in ('.gitignore', '.env.example'):
                return f"[Archivo binario o no soportado: {path}]"
            
            # Verificar tamaño
            size = os.path.getsize(full_path)
            if size > self.MAX_FILE_SIZE * 2:
                return f"[Archivo muy grande: {path} ({size} bytes)]"
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if len(content) > self.MAX_FILE_SIZE:
                return content[:self.MAX_FILE_SIZE] + f"\n\n... [Truncado: {len(content)} caracteres total]"
            
            return content
        
        except Exception as e:
            return f"[Error leyendo {path}: {str(e)}]"
    
    def find_files_by_name(self, name: str) -> List[str]:
        """
        Busca archivos por nombre en todo el proyecto.
        
        Args:
            name: Nombre o parte del nombre a buscar
        
        Returns:
            Lista de rutas relativas que coinciden
        """
        matches = []
        name_lower = name.lower()
        
        for root, dirs, files in os.walk(self.project.root):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
            
            for filename in files:
                if name_lower in filename.lower():
                    rel_path = os.path.relpath(os.path.join(root, filename), self.project.root)
                    matches.append(rel_path)
        
        return matches
    
    def find_files_by_content(self, pattern: str, max_results: int = 10) -> List[Dict]:
        """
        Busca archivos que contengan un patrón de texto.
        
        Args:
            pattern: Texto a buscar
            max_results: Máximo de resultados
        
        Returns:
            Lista de {path, line_number, line_content}
        """
        results = []
        pattern_lower = pattern.lower()
        
        for file_path in self.list_all_files():
            if len(results) >= max_results:
                break
            
            content = self.read_file_safe(file_path)
            if not content or content.startswith('['):
                continue
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if pattern_lower in line.lower():
                    results.append({
                        'path': file_path,
                        'line': i,
                        'content': line.strip()[:100]
                    })
                    if len(results) >= max_results:
                        break
        
        return results
    
    def get_related_files(self, main_file: str, depth: int = 1) -> List[str]:
        """
        Encuentra archivos relacionados al archivo principal.
        Busca imports en Python, requires en JS, etc.
        """
        related = set()
        content = self.read_file_safe(main_file)
        
        if not content or content.startswith('['):
            return list(related)
        
        ext = os.path.splitext(main_file)[1].lower()
        base_dir = os.path.dirname(main_file)
        
        if ext == '.py':
            import re
            # from x import y
            for match in re.finditer(r'^from\s+(\.+)?(\w+(?:\.\w+)*)\s+import', content, re.MULTILINE):
                dots = match.group(1) or ""
                module = match.group(2)
                
                if dots:
                    # Import relativo
                    levels_up = len(dots) - 1
                    current = base_dir
                    for _ in range(levels_up):
                        current = os.path.dirname(current)
                    path = os.path.join(current, module.replace('.', os.sep) + '.py')
                else:
                    path = module.replace('.', os.sep) + '.py'
                
                if self.read_file_safe(path):
                    related.add(path)
            
            # import x
            for match in re.finditer(r'^import\s+(\w+(?:\.\w+)*)', content, re.MULTILINE):
                module = match.group(1)
                path = module.replace('.', os.sep) + '.py'
                if self.read_file_safe(path):
                    related.add(path)
        
        elif ext in ('.js', '.ts', '.jsx', '.tsx'):
            import re
            for match in re.finditer(r'(?:import|require)\s*\(?[\'"]([./][^\'"]+)[\'"]', content):
                imp = match.group(1)
                if imp.startswith('.'):
                    path = os.path.normpath(os.path.join(base_dir, imp))
                    for test_ext in ['', '.js', '.ts', '.jsx', '.tsx', '/index.js', '/index.ts']:
                        test_path = path + test_ext
                        if self.read_file_safe(test_path):
                            related.add(test_path)
                            break
        
        return list(related)[:10]
    
    def build_context(self, 
                      instruction: str,
                      selected_code: Optional[str] = None,
                      current_file: Optional[str] = None,
                      include_files: Optional[List[str]] = None,
                      auto_include_related: bool = True) -> Dict:
        """
        Construye el contexto completo para Athena.
        
        Args:
            instruction: Instrucción del usuario
            selected_code: Código seleccionado en el editor
            current_file: Archivo actualmente abierto
            include_files: Lista de archivos adicionales a incluir
            auto_include_related: Si incluir archivos relacionados automáticamente
        
        Returns:
            Dict con toda la información de contexto
        """
        context = {
            "project_tree": self.get_project_tree(),
            "instruction": instruction,
            "selected_code": selected_code,
            "current_file": current_file,
            "files": {},
            "all_project_files": self.list_all_files()
        }
        
        files_to_read = set()
        
        # Añadir archivo actual
        if current_file:
            files_to_read.add(current_file)
            if auto_include_related:
                related = self.get_related_files(current_file)
                files_to_read.update(related)
        
        # Añadir archivos específicos
        if include_files:
            files_to_read.update(include_files)
        
        # Auto-detectar archivos importantes del proyecto
        important_files = ['athena_plan.md', 'README.md', 'requirements.txt', 'package.json', 
                          'pyproject.toml', 'setup.py', 'main.py', 'index.js',
                          'app.py', 'config.py', 'settings.py']
        for imp_file in important_files:
            matches = self.find_files_by_name(imp_file)
            if matches:
                files_to_read.add(matches[0])
        
        # Leer archivos respetando límite total
        total_size = 0
        for path in sorted(files_to_read):
            if total_size > self.MAX_CONTEXT_SIZE:
                break
            content = self.read_file_safe(path)
            if content and not content.startswith('['):
                context["files"][path] = content
                total_size += len(content)
        
        return context
    
    def context_to_text(self, context: Dict) -> str:
        """Convierte el contexto a texto para el prompt."""
        text = f"## Estructura del Proyecto\n```\n{context['project_tree']}\n```\n\n"
        
        # Lista de todos los archivos disponibles
        if context.get('all_project_files'):
            text += f"## Archivos Disponibles ({len(context['all_project_files'])} archivos)\n"
            # Mostrar solo algunos para no saturar
            sample = context['all_project_files'][:30]
            text += "```\n" + "\n".join(sample)
            if len(context['all_project_files']) > 30:
                text += f"\n... y {len(context['all_project_files']) - 30} archivos más"
            text += "\n```\n\n"
        
        if context.get('current_file'):
            text += f"## Archivo Actual: `{context['current_file']}`\n\n"
        
        if context.get('selected_code'):
            text += f"## Código Seleccionado\n```\n{context['selected_code']}\n```\n\n"
        
        if context.get('files'):
            text += "## Contenido de Archivos Relevantes\n\n"
            for path, content in context['files'].items():
                ext = os.path.splitext(path)[1].lstrip('.')
                text += f"### `{path}`\n```{ext}\n{content}\n```\n\n"
        
        return text
