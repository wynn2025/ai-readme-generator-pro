class ProjectAnalyzer:
    """Analyze project structure and extract metadata."""

    def __init__(self, path):
        self.path = Path(path).resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"Not found: {self.path}")
        self.files = []
        self.lang = "generic"
        self.name = self.path.name
        self.has_req = self.has_pkg = self.has_setup = self.has_lic = False
        self.has_tests = self.has_ci = False
        self.entry = None
        self.funcs = defaultdict(list)
        self.classes = defaultdict(list)
        self.total_lines = 0

    def scan(self):
        """Walk project directory, detect language, find entry point."""
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in IGNORE and not d.startswith(".")]
            for f in files:
                fp = Path(root) / f
                rel = fp.relative_to(self.path)
                self.files.append(rel)
                ext = fp.suffix.lower()
                for lang, exts in LANG_EXT.items():
                    if ext in exts:
                        self.lang = lang
                fn = f.lower()
                if fn == "requirements.txt":
                    self.has_req = True
                elif fn == "package.json":
                    self.has_pkg = True
                elif fn in ("setup.py", "setup.cfg", "pyproject.toml"):
                    self.has_setup = True
                elif fn.startswith("license"):
                    self.has_lic = True
                elif "test" in fn:
                    self.has_tests = True
                if ext in (".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".h"):
                    try:
                        self.total_lines += fp.read_text(encoding="utf-8", errors="ignore").count(NL) + 1
                    except Exception:
                        pass
        py = [f for f in self.files if f.suffix == ".py" and not f.name.startswith("_")]
        if py:
            self.entry = max(py, key=lambda f: (self.path / f).stat().st_size)
        self._analyze()
        return self

    def _analyze(self):
        """Extract functions and classes from source files."""
        for rel in self.files:
            if rel.suffix not in (".py", ".js", ".ts"):
                continue
            try:
                content = (self.path / rel).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if rel.suffix == ".py":
                for m in re.finditer(r"^def\s+(\w+)\s*\(([^)]*)\)", content, re.M):
                    n, p = m.group(1), m.group(2)
                    if not n.startswith("_"):
                        self.funcs[str(rel)].append({"name": n, "params": p.strip()})
                for m in re.finditer(r"^class\s+(\w+)", content, re.M):
                    self.classes[str(rel)].append({"name": m.group(1)})
            else:
                for m in re.finditer(r"(?:function|const|let)\s+(\w+)", content):
                    if not m.group(1).startswith("_"):
                        self.funcs[str(rel)].append({"name": m.group(1), "params": ""})

    def summary(self):
        """Return project metadata dictionary."""
        return {
            "name": self.name,
            "lang": self.lang,
            "files": len(self.files),
            "lines": self.total_lines,
            "funcs": sum(len(v) for v in self.funcs.values()),
            "classes": sum(len(v) for v in self.classes.values()),
            "entry": str(self.entry) if self.entry else "N/A",
            "tests": self.has_tests,
            "ci": self.has_ci,
            "license": self.has_lic,
        }
