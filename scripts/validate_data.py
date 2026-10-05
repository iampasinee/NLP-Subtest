import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rag import load_recipes

def validate(folder):
    files = list(Path(folder).glob('recipes.md'))
    recipes = load_recipes(folder)
    # Count actual fields, excluding Markdown/table formatting and duplicated metadata.
    chars = sum(len(r['name']) + len(str(r['servings'])) + len(r['notes']) + len(r['source'])
                + sum(len(i['name']) + len(i['quantity']) for i in r['ingredients'])
                + sum(map(len, r['equipment'])) + sum(map(len, r['steps'])) for r in recipes)
    if len(files) != 1 or chars < 15000 or len(recipes) < 20:
        raise ValueError(f'คลังเอกสารไม่ผ่าน: {len(files)} files, {chars} characters, {len(recipes)} recipes')
    return dict(files=len(files), recipes=len(recipes), content_characters=chars, schema_valid=True)

if __name__ == '__main__':
    print(json.dumps(validate(ROOT / 'data'), ensure_ascii=False, indent=2))
