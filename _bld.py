import os
G = chr(10)
BT = chr(96)
TB = BT * 3

# Read template sections from _sections
# Each section is a separate .py file
parts = []
for name in ["_hdr", "_analyzer", "_generator", "_cli"]:
    with open(name + ".py", "r", encoding="utf-8") as f:
        parts.append(f.read())
final = G.join(parts)
with open("ai_readme_generator_pro.py", "w", encoding="utf-8") as f:
    f.write(final)
import py_compile
py_compile.compile("ai_readme_generator_pro.py", doraise=True)
print("Build OK!")
