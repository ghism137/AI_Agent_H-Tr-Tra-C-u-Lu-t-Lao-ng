import json
import subprocess

print('Running build_phase1_stage.py to see if gate 3 fails...')
result = subprocess.run(['.\\venv\\Scripts\\python.exe', 'scripts/build_phase1_stage.py'], capture_output=True, text=True)

print(f'Stdout: {result.stdout}')
print(f'Stderr: {result.stderr}')

try:
    with open('data/staging/phase1-candidate/manifest.json', 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    print(f'Gate 3: {manifest.get("gate3")}')
except Exception as e:
    print(f'Error reading manifest: {e}')
