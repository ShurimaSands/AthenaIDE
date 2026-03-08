"""
Syntax Highlighter para el editor de código.
Soporta Python, JavaScript, JSON y otros lenguajes comunes.
"""
import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import Qt

from ui.theme import COLORS


class SyntaxHighlighter(QSyntaxHighlighter):
    """
    Highlighter multi-lenguaje para el editor de código.
    Detecta el lenguaje por extensión y aplica reglas correspondientes.
    """
    
    def __init__(self, document, language: str = "python"):
        super().__init__(document)
        self.language = language.lower()
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Configura los formatos de texto para cada tipo de token."""
        self.formats = {}
        
        # Keyword format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_keyword"]))
        fmt.setFontWeight(QFont.Weight.Bold)
        self.formats["keyword"] = fmt
        
        # String format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_string"]))
        self.formats["string"] = fmt
        
        # Comment format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_comment"]))
        fmt.setFontItalic(True)
        self.formats["comment"] = fmt
        
        # Number format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_number"]))
        self.formats["number"] = fmt
        
        # Function format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_function"]))
        self.formats["function"] = fmt
        
        # Class format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_class"]))
        fmt.setFontWeight(QFont.Weight.Bold)
        self.formats["class"] = fmt
        
        # Decorator format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_decorator"]))
        self.formats["decorator"] = fmt
        
        # Operator format
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["syntax_operator"]))
        self.formats["operator"] = fmt
    
    def _setup_rules(self):
        """Configura las reglas de highlighting según el lenguaje."""
        self.rules = []
        
        if self.language == "python":
            self._setup_python_rules()
        elif self.language in ("javascript", "js", "typescript", "ts"):
            self._setup_javascript_rules()
        elif self.language == "json":
            self._setup_json_rules()
        else:
            # Reglas genéricas
            self._setup_generic_rules()
    
    def _setup_python_rules(self):
        """Reglas para Python."""
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield'
        ]
        
        # Keywords
        for kw in keywords:
            self.rules.append((rf'\b{kw}\b', self.formats["keyword"]))
        
        # Tipos built-in
        builtins = ['int', 'str', 'list', 'dict', 'set', 'tuple', 'bool', 'float', 'type', 'object']
        for bt in builtins:
            self.rules.append((rf'\b{bt}\b', self.formats["class"]))
        
        # Decoradores
        self.rules.append((r'@\w+', self.formats["decorator"]))
        
        # Funciones (nombre seguido de paréntesis)
        self.rules.append((r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()', self.formats["function"]))
        
        # Definición de clase
        self.rules.append((r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)', self.formats["class"]))
        
        # Números
        self.rules.append((r'\b[0-9]+\.?[0-9]*\b', self.formats["number"]))
        self.rules.append((r'\b0x[0-9a-fA-F]+\b', self.formats["number"]))
        
        # Strings (dobles y simples, incluyendo f-strings)
        self.rules.append((r'f?"[^"\\]*(\\.[^"\\]*)*"', self.formats["string"]))
        self.rules.append((r"f?'[^'\\]*(\\.[^'\\]*)*'", self.formats["string"]))
        
        # Triple quotes
        self.rules.append((r'""".*?"""', self.formats["string"]))
        self.rules.append((r"'''.*?'''", self.formats["string"]))
        
        # Comentarios
        self.rules.append((r'#.*$', self.formats["comment"]))
    
    def _setup_javascript_rules(self):
        """Reglas para JavaScript/TypeScript."""
        keywords = [
            'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue',
            'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends',
            'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'let',
            'new', 'return', 'static', 'super', 'switch', 'this', 'throw', 'try',
            'typeof', 'var', 'void', 'while', 'with', 'yield'
        ]
        
        for kw in keywords:
            self.rules.append((rf'\b{kw}\b', self.formats["keyword"]))
        
        # Valores especiales
        for val in ['true', 'false', 'null', 'undefined', 'NaN', 'Infinity']:
            self.rules.append((rf'\b{val}\b', self.formats["keyword"]))
        
        # Funciones
        self.rules.append((r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()', self.formats["function"]))
        
        # Números
        self.rules.append((r'\b[0-9]+\.?[0-9]*\b', self.formats["number"]))
        
        # Strings
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', self.formats["string"]))
        self.rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", self.formats["string"]))
        self.rules.append((r'`[^`]*`', self.formats["string"]))  # Template literals
        
        # Comentarios
        self.rules.append((r'//.*$', self.formats["comment"]))
        self.rules.append((r'/\*.*?\*/', self.formats["comment"]))
    
    def _setup_json_rules(self):
        """Reglas para JSON."""
        # Keys
        self.rules.append((r'"[^"]*"\s*:', self.formats["function"]))
        
        # Strings
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', self.formats["string"]))
        
        # Números
        self.rules.append((r'\b-?[0-9]+\.?[0-9]*\b', self.formats["number"]))
        
        # Booleanos y null
        for val in ['true', 'false', 'null']:
            self.rules.append((rf'\b{val}\b', self.formats["keyword"]))
    
    def _setup_generic_rules(self):
        """Reglas genéricas para otros lenguajes."""
        # Números
        self.rules.append((r'\b[0-9]+\.?[0-9]*\b', self.formats["number"]))
        
        # Strings
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', self.formats["string"]))
        self.rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", self.formats["string"]))
    
    def highlightBlock(self, text: str):
        """Aplica el highlighting a un bloque de texto."""
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)
    
    def set_language(self, language: str):
        """Cambia el lenguaje y reconfigura las reglas."""
        if language.lower() != self.language:
            self.language = language.lower()
            self._setup_rules()
            self.rehighlight()


def get_language_from_extension(extension: str) -> str:
    """Detecta el lenguaje según la extensión del archivo."""
    ext_map = {
        '.py': 'python',
        '.pyw': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.json': 'json',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'css',
        '.md': 'markdown',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sh': 'bash',
        '.bat': 'batch',
        '.ps1': 'powershell',
    }
    return ext_map.get(extension.lower(), 'text')
