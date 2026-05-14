#!/usr/bin/env python3
"""AI README Generator Pro v1.0.0
Scan project source code, analyze structure, generate professional README.md.
Supports Python/Node/Go/Rust/Java/C++. Optional DeepSeek API enhancement.
"""
import os, sys, re, json, argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

VERSION = "1.0.0"
NL = chr(10)
BT = chr(96)
TB = BT * 3
IGNORE = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", ".idea", ".vscode", ".eggs"}
LANG_EXT = {"python": {".py"}, "node": {".js", ".ts"}, "go": {".go"}, "rust": {".rs"}, "java": {".java"}, "cpp": {".cpp", ".hpp", ".h"}}

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

    def _toc(self, s):
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

    def _api_section(self, s):
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

    def _contributing(self, s):
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

def main():
    import argparse
    p = argparse.ArgumentParser(description="AI README Generator Pro v1.0.0")
    p.add_argument("path", help="Project directory path")
    p.add_argument("-t", "--template", default="professional", choices=["minimal", "professional", "full"], help="README template style")
    p.add_argument("-o", "--output", default=None, help="Output file (default: README_generated.md)")
    p.add_argument("--api-key", default=None, help="DeepSeek API key for AI enhancement")
    p.add_argument("--dry-run", action="store_true", help="Print to stdout instead of file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show analysis details")
    args = p.parse_args()

    path = args.path
    if path.startswith("http"):
        import subprocess, tempfile
        tmp = tempfile.mkdtemp(prefix="readme_gen_")
        print("Cloning " + path + " ...")
        r = subprocess.run(["git", "clone", "--depth", "1", path, tmp], capture_output=True, text=True)
        if r.returncode != 0:
            print("Clone failed: " + r.stderr)
            return 1
        path = tmp

    print("Analyzing: " + path)
    analyzer = ProjectAnalyzer(path)
    analyzer.scan()
    s = analyzer.summary()

    if args.verbose:
        print("--- Project Summary ---")
        for k, v in s.items(): print("  " + k + ": " + str(v))
        print("  Functions: " + str(sum(len(v) for v in analyzer.funcs.values())))
        print("  Classes: " + str(sum(len(v) for v in analyzer.classes.values())))
        print("  Entry: " + str(analyzer.entry))

    gen = ReadmeGenerator(analyzer, template=args.template, api_key=args.api_key)
    readme = gen.generate()

    if args.api_key:
        print("Enhancing with DeepSeek API...")
        try:
            import urllib.request, json
            url = "https://api.deepseek.com/v1/chat/completions"
            SEP = chr(10) + chr(10)
            prompt = "Improve this README.md, keep structure but enhance descriptions. Return ONLY markdown:" + SEP + readme
            payload = json.dumps({"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096}).encode()
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer " + args.api_key})
            resp = urllib.request.urlopen(req, timeout=60)
            data = json.loads(resp.read())
            enhanced = data["choices"][0]["message"]["content"]
            if enhanced: readme = enhanced
            print("API enhancement done.")
        except Exception as e:
            print("API enhancement failed: " + str(e) + ". Using generated version.")

    if args.dry_run:
        print(readme)
    else:
        outfile = args.output or "README_generated.md"
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(readme)
        print("Written to: " + outfile + " (" + str(len(readme)) + " chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
