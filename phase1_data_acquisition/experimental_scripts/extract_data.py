import json
from bs4 import BeautifulSoup

def main():
    with open("sample.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    data = json.loads(script_tag.string)
    props = data.get("props", {}).get("pageProps", {})
    
    mf = props.get("mutualFundsDetailData", {})
    out_lines = []
    
    def get_all_keys(d, prefix=""):
        keys = []
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = prefix + "." + k if prefix else k
                keys.append(full_key)
                if isinstance(v, dict):
                    keys.extend(get_all_keys(v, full_key))
                elif isinstance(v, list) and v and isinstance(v[0], dict):
                    keys.extend(get_all_keys(v[0], full_key + "[0]"))
        return keys
        
    all_keys = get_all_keys(mf)
    for k in all_keys:
        if any(t in k.lower() for t in ["expense", "exit", "lock", "risk", "benchmark", "sip", "nav"]):
            out_lines.append(k)

    with open("keys_found.txt", "w", encoding="utf-8") as f:
        for line in out_lines:
            f.write("!!! " + line + "\n")
            
    # Also dump some specific primitive values just in case
    def find_values(d, path=""):
        if isinstance(d, dict):
            for k, v in d.items():
                p = f"{path}.{k}" if path else k
                if any(t in k.lower() for t in ["expense", "exit", "lock", "risk", "benchmark", "sip", "nav"]):
                    if isinstance(v, (str, int, float, bool)):
                         out_lines.append(f"VALUE: {p} = {v}")
                find_values(v, p)
        elif isinstance(d, list) and d and isinstance(d[0], dict):
            for i, i_d in enumerate(d):
                find_values(i_d, f"{path}[{i}]")
                
    out_lines.append("\nVALUES FOUND:")
    find_values(mf)
    with open("keys_found.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
        
    print("Done writing keys_found.txt")

if __name__ == "__main__":
    main()
