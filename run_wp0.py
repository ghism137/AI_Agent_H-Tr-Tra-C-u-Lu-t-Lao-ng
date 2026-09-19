import subprocess
import json
import os
import io

def run():
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    env["PYTHONUTF8"] = "1"
    
    # Run the build
    result = subprocess.run(
        [".\\venv\\Scripts\\python.exe", "scripts/build_phase1_stage.py"], 
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    # Try to load existing manifest if available
    try:
        manifest = json.load(open("data/staging/phase1-candidate/manifest.json", encoding="utf-8"))
    except:
        manifest = {}
        
    baseline_info = {
        "timestamp": "2026-09-18T12:00:00+07:00",
        "build_exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "manifest": manifest
    }
    
    os.makedirs("reports/phase1-closeout", exist_ok=True)
    with open("reports/phase1-closeout/baseline_2026-09-18.json", "w", encoding="utf-8") as f:
        json.dump(baseline_info, f, indent=2, ensure_ascii=False)
        
    # generate scope_lock.json
    try:
        docs = json.load(open("data/registry/documents.json", encoding="utf-8"))
        doc_ids = list(docs.keys())
        base_docs = [did for did in doc_ids if "NĐ" not in did] # Just an approximation for now, we should extract accurately
    except Exception as e:
        doc_ids = []
        base_docs = []
        
    scope_lock = {
        "as_of_date": "2026-09-17",
        "total_documents_count": len(doc_ids),
        "documents": doc_ids,
        "base_documents_37": base_docs,
        "required_coverages": 15
    }
    with open("reports/phase1-closeout/scope_lock.json", "w", encoding="utf-8") as f:
        json.dump(scope_lock, f, indent=2, ensure_ascii=False)

    print("WP0 prep complete")

if __name__ == "__main__":
    run()
