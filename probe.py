"""Read raw OCF resources from an AC through SmartThings `execute` (GET only)."""
import json, sys, time, st
room = sys.argv[1]
for href in sys.argv[2:]:
    try:
        st.cmd(room, "execute", "execute", href)
        time.sleep(4)
        d = st._req(st.API + st.DEV[room] + "/components/main/capabilities/execute/status")["data"]
        v = d.get("value") or {}
        print(href, "->", json.dumps(v.get("payload", v))[:900], "| data.href=", (d.get("data") or {}).get("href"))
    except Exception as e:
        print(href, "ERR", e)
