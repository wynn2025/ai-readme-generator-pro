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
