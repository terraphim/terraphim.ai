from pathlib import Path
import argparse, json
parser=argparse.ArgumentParser(description="Validate the fictional Harbour project brief")
parser.add_argument("--check",action="store_true",required=True)
args=parser.parse_args()
text=Path("brief.md").read_text()
assert all(x in text for x in ("Decision:","Risk:","Owner:")), "Brief is missing a required field"
result={"project":"Harbour", "status":"valid", "fields":["Decision","Risk","Owner"]}
Path("validation.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
