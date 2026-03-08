import os

class ProjectManager:
    def __init__(self, root):
        self.root = root

    def tree(self):
        lines = []
        for r, d, f in os.walk(self.root):
            lvl = r.replace(self.root, "").count(os.sep)
            indent = "  " * lvl
            for dd in d:
                lines.append(f"{indent}{dd}/")
            for ff in f:
                lines.append(f"{indent}{ff}")
        return "\n".join(lines)

    def read(self, path):
        with open(os.path.join(self.root, path), encoding="utf-8", errors="ignore") as f:
            return f.read()

    def write(self, path, content):
        with open(os.path.join(self.root, path), "w", encoding="utf-8") as f:
            f.write(content)

    def create_file(self, path):
        open(os.path.join(self.root, path), "w").close()

    def create_dir(self, path):
        os.makedirs(os.path.join(self.root, path), exist_ok=True)
