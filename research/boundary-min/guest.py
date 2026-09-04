"""Guest: sandboxed. Only stdin/stdout. Emits proposals; never touches effects. Scenario chosen by argv."""
import sys, json, os
def say(o): sys.stdout.write(json.dumps(o)+"\n"); sys.stdout.flush()
def ask(o):
    say(o); line=sys.stdin.readline(); return json.loads(line) if line else None
scenario=sys.argv[1]; report={"scenario":scenario,"steps":[]}
def step(name,res): report["steps"].append({"name":name,"result":res})
if scenario=="confinement":
    try: open("/tmp/boundary-min-canary.txt","w").write("x"); step("direct_write","ALLOWED")
    except Exception as e: step("direct_write","REFUSED:"+type(e).__name__)
    try:
        import socket; socket.create_connection(("127.0.0.1",9),timeout=1); step("direct_net","ALLOWED")
    except Exception as e: step("direct_net","REFUSED:"+type(e).__name__)
    try: open(os.environ["KEY_DIR_HINT"]+"/issuer.pem").read(); step("read_issuer_key","ALLOWED")
    except Exception as e: step("read_issuer_key","REFUSED:"+type(e).__name__)
    step("env_has_key", any("PRIVATE KEY" in v for v in os.environ.values()))
elif scenario=="allowlist":
    step("bad_tool",ask({"kind":"propose","tool":"delete_everything","args":{"path":"/"}}))
    step("good_tool",ask({"kind":"propose","tool":"write_note","args":{"text":"hello from guest"}}))
elif scenario=="replay":
    r=ask({"kind":"propose","tool":"write_note","args":{"text":"replay me"}}); step("first",r)
    step("replay_same_nonce",ask({"kind":"replay","nonce":r.get("nonce")}))
elif scenario=="tamper":
    step("tampered",ask({"kind":"propose","tool":"write_note","args":{"text":"tamper"},"_test_tamper":True}))
    step("clean",ask({"kind":"propose","tool":"write_note","args":{"text":"tamper control"}}))
elif scenario=="semantic":
    step("substituted_impl",ask({"kind":"propose","tool":"write_note","args":{"text":"semantic"}}))
elif scenario=="amend":
    step("amend",ask({"kind":"amend","new_allowlist":{"delete_everything":"x"}}))
    step("after_amend",ask({"kind":"propose","tool":"delete_everything","args":{}}))
elif scenario=="selfissue":
    step("hand_minted",ask({"kind":"raw_grant","operation":{"tool":"write_note","args_digest":"00","impl_digest":"00","statement_digest":"00","nonce":"deadbeef"},"signature":"00"*64}))
say({"kind":"report","report":report})
