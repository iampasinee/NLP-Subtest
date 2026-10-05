import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rag import load_recipes, sections

def validate(folder):
    files = list(Path(folder).glob('*.json'))
    recipes = load_recipes(folder)
    # Count substantive decoded content, not JSON padding/escaping.
    chars = sum(len(r['name']) + sum(len(v) for v in sections(r).values()) for r in recipes)
    if len(files) < 10 or chars < 15000 or len(recipes) < 20:
        raise ValueError(f'คลังเอกสารไม่ผ่าน: {len(files)} files, {chars} characters, {len(recipes)} recipes')
    return dict(files=len(files), recipes=len(recipes), content_characters=chars, schema_valid=True)

if __name__ == '__main__':
    print(json.dumps(validate(ROOT / 'data'), ensure_ascii=False, indent=2))
