import subprocess
import ollama
import sys

NAMESPACE = "default"
DEPLOYMENT = "broken-app"
CONTAINER = "app"

def safe_run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

def get_status():
    return safe_run(f"kubectl get pods -l app=broken-app -n {NAMESPACE}")

def get_logs():
    return safe_run(f"kubectl logs deployment/{DEPLOYMENT} -n {NAMESPACE}")

def get_events():
    return safe_run(f"kubectl describe pod -l app=broken-app -n {NAMESPACE}")

def ask_ai(logs, events):
    prompt = f"""
You are a Kubernetes SRE.

LOGS:
{logs}

EVENTS:
{events}

TASK:
Choose ONE fix type.

Allowed FIX_TYPE:
SET_IMAGE
SET_ENV
SET_MEMORY
NONE

Rules:
- Do not write kubectl commands
- Only classify the fix

FORMAT STRICTLY:

ISSUE:
ROOT_CAUSE:
FIX_TYPE:
FIX_VALUE:
"""

    response = ollama.chat(
        model="gemma:2b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def parse_response(text):
    data = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()
    return data

def build_fix(fix_type, fix_value):
    if fix_type == "SET_IMAGE":
        return f"kubectl set image deployment/{DEPLOYMENT} {CONTAINER}={fix_value}"
    if fix_type == "SET_ENV":
        return f"kubectl set env deployment/{DEPLOYMENT} {fix_value}"
    if fix_type == "SET_MEMORY":
        return f"kubectl set resources deployment/{DEPLOYMENT} --limits=memory={fix_value}"
    return None

def fallback(logs, events):
    if "ImagePullBackOff" in events:
        return "kubectl set image deployment/broken-app app=nginx:latest"
    if "OOMKilled" in events:
        return "kubectl set resources deployment/broken-app --limits=memory=256Mi"
    if "DB_URL" in logs:
        return "kubectl set env deployment/broken-app DB_URL=postgres://db:5432/app"
    return None

print("\n🔍 POD STATUS")
print(get_status())

logs = get_logs()
events = get_events()

print("\n📄 LOGS\n", logs)
print("\n📄 EVENTS\n", events)

analysis = ask_ai(logs, events)
print("\n🤖 AI SRE ANALYSIS\n", analysis)

parsed = parse_response(analysis)
cmd = build_fix(parsed.get("FIX_TYPE"), parsed.get("FIX_VALUE"))

if not cmd:
    cmd = fallback(logs, events)

if not cmd:
    print("❌ No safe fix available")
    sys.exit(1)

print("\n✅ Proposed Fix:\n", cmd)

approve = input("\nApprove fix? (yes/no): ").lower()
if approve == "yes":
    print("\n🚀 Applying fix...\n")
    subprocess.run(cmd, shell=True)
else:
    print("❌ Fix skipped")