import sys

print("""
Entropic Fingerprint — run options:

  python run.py collect      - collect commit data (requires internet)
  python run.py analyze      - run correlation analysis on all repos  
  python run.py model        - run predictive model
  python run.py significance - run permutation significance tests
  python run.py visualize    - generate all charts
""")

if len(sys.argv) < 2:
    sys.exit(0)

cmd = sys.argv[1]

if cmd == "collect":
    exec(open("src/collect.py").read())
elif cmd == "analyze":
    exec(open("src/findings.py").read())
    exec(open("src/analyze_django.py").read())
    exec(open("src/analyze_cpython.py").read())
elif cmd == "model":
    exec(open("src/model.py").read())
elif cmd == "significance":
    exec(open("src/significance.py").read())
elif cmd == "visualize":
    exec(open("src/visualize_combined.py").read())
else:
    print(f"Unknown command: {cmd}")