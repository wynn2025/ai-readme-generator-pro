class ReadmeGenerator:
    BADGES = {
        "python": ("Python", "3776AB", "white"),
        "node": ("Node.js", "339933", "white"),
        "go": ("Go", "00ADD8", "white"),
        "rust": ("Rust", "000000", "white"),
        "java": ("Java", "ED8B00", "white"),
        "cpp": ("C%2B%2B", "00599C", "white"),
    }

    def __init__(self, analyzer, template="professional", api_key=None):
        self.a = analyzer
        self.tpl = template
        self.api_key = api_key
        self.sections = []

    def generate(self):
        s = self.a.summary()
        for m in [self._header, self._badges, self._description, self._toc,
                 self._features, self._structure, self._install, self._usage,
                 self._api_section, self._testing, self._contributing,
                 self._license, self._footer]:
            m(s)
        return chr(10).join(self.sections) + chr(10)

    def _header(self, s):
        self.sections.append("# " + s["name"])
        self.sections.append("")

    def _badges(self, s):
        lang = s.get("lang", "generic")
        if lang in self.BADGES:
            name, color, _ = self.BADGES[lang]
            self.sections.append("![" + name + "](https://img.shields.io/badge/" + name.replace(" ", "%20") + "-" + color + "?style=for-the-badge)")
        self.sections.append("![Files](https://img.shields.io/badge/files-" + str(s["files"]) + "-blue)")
        self.sections.append("![Lines](https://img.shields.io/badge/lines-" + str(s["lines"]) + "-green)")
        if s.get("license"):
            self.sections.append("![License](https://img.shields.io/badge/license-MIT-yellow)")
        self.sections.append("")
    def _description(self, s):
        lang = s.get("lang", "generic")
        funcs = s.get("funcs", 0)
        classes = s.get("classes", 0)
        desc = "A " + lang + " project with " + str(s["files"]) + " files (" + str(s["lines"]) + " lines). "
        if funcs: desc += str(funcs) + " functions"
        if classes: desc += " and " + str(classes) + " classes"
        if funcs or classes: desc += "."
        self.sections.append("> " + desc)
        self.sections.append("")

    def _toc(self):
        if self.tpl not in ("professional", "full"): return
        self.sections.append("## Table of Contents")
        self.sections.append("")
        for item in ["Features", "Project Structure", "Installation", "Usage", "API Reference", "Testing", "Contributing", "License"]:
            self.sections.append("- [" + item + "]( #" + item.lower().replace(" ", "-") + ")" )
        self.sections.append("")

    def _features(self, s):
        self.sections.append("## Features")
        self.sections.append("")
        feats = []
        if s.get("funcs", 0) > 0: feats.append("- " + str(s["funcs"]) + " functions")
        if s.get("classes", 0) > 0: feats.append("- " + str(s["classes"]) + " classes")
        if s.get("tests"): feats.append("- Test suite included")
        if s.get("license"): feats.append("- MIT Licensed")
        feats.append("- Written in " + s.get("lang", "generic"))
        feats.append("- " + str(s["files"]) + " files, " + str(s["lines"]) + " lines")
        for f in feats: self.sections.append(f)
        self.sections.append("")

    def _structure(self, s):
        self.sections.append("## Project Structure")
        self.sections.append("")
        BT = chr(96)
        TB = BT * 3
        self.sections.append(TB)
        self.sections.append(s["name"] + "/")
        from collections import defaultdict
        dirmap = defaultdict(list)
        for rel in self.a.files:
            parent = str(rel.parent) if str(rel.parent) != "." else ""
            dirmap[parent].append(rel.name)
        for d in sorted(dirmap.keys()):
            files = sorted(dirmap[d])
            if d:
                self.sections.append("|-- " + d + "/")
                for fn in files: self.sections.append("|   |-- " + fn)
            else:
                for fn in files: self.sections.append("|-- " + fn)
        self.sections.append(TB)
        self.sections.append("")
    def _install(self, s):
        self.sections.append("## Installation")
        self.sections.append("")
        TB = chr(96) * 3
        lang = s.get("lang", "generic")
        cmds = ["git clone <repo-url>", "cd " + s["name"]]
        if lang == "python" and self.a.has_req: cmds.append("pip install -r requirements.txt")
        elif lang == "node": cmds.append("npm install")
        self.sections.append(TB)
        self.sections.append("bash")
        for c in cmds: self.sections.append(c)
        self.sections.append(TB)
        self.sections.append("")

    def _usage(self, s):
        self.sections.append("## Usage")
        self.sections.append("")
        TB = chr(96) * 3
        entry = s.get("entry", "main.py")
        lang = s.get("lang", "generic")
        self.sections.append(TB)
        self.sections.append("bash")
        if lang == "python": self.sections.append("python " + entry)
        elif lang == "node": self.sections.append("node index.js")
        else: self.sections.append("# Build and run")
        self.sections.append(TB)
        self.sections.append("")

    def _api_section(self):
        if not self.a.funcs and not self.a.classes: return
        self.sections.append("## API Reference")
        self.sections.append("")
        BT = chr(96)
        TB = BT * 3
        for fp in sorted(self.a.funcs.keys()):
            funcs = self.a.funcs[fp]
            if not funcs: continue
            self.sections.append("### " + fp)
            self.sections.append("")
            for fn in funcs:
                params = fn.get("params", "")
                self.sections.append(TB)
                self.sections.append("python")
                self.sections.append("def " + fn["name"] + "(" + params + ")")
                self.sections.append("    ...")
                self.sections.append(TB)
                self.sections.append("")
        self.sections.append("")

    def _testing(self, s):
        if not s.get("tests"): return
        self.sections.append("## Testing")
        self.sections.append("")
        TB = chr(96) * 3
        lang = s.get("lang", "generic")
        self.sections.append(TB)
        self.sections.append("bash")
        if lang == "python": self.sections.append("python -m pytest")
        elif lang == "node": self.sections.append("npm test")
        else: self.sections.append("make test")
        self.sections.append(TB)
        self.sections.append("")

    def _contributing(self):
        if self.tpl not in ("professional", "full"): return
        self.sections.append("## Contributing")
        self.sections.append("")
        for step in ["1. Fork the repository", "2. Create feature branch",
                     "3. Commit changes", "4. Push to branch", "5. Open Pull Request"]:
            self.sections.append(step)
        self.sections.append("")

    def _license(self, s):
        if not s.get("license"): return
        self.sections.append("## License")
        self.sections.append("")
        self.sections.append("MIT License")
        self.sections.append("")

    def _footer(self, s):
        self.sections.append("---")
        self.sections.append("Generated by [AI README Generator Pro](https://github.com/wynn2025/ai-readme-generator-pro)")
        self.sections.append("")
