import os
import json
from typing import Dict, Any, Set

ROOT_DIR = r"C:\Users\joaqu\Desktop\Prueba Ia\extractions"

def flatten(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten(v, new_key, sep))
        else:
            items[new_key] = v
    return items

def unflatten(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    result = {}
    for k, v in d.items():
        keys = k.split(sep)
        current = result
        for part in keys[:-1]:
            current = current.setdefault(part, {})
        current[keys[-1]] = v
    return result

def read_all_jsons(root_dir: str):
    jsons = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(subdir, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        jsons.append((path, data))
                except Exception as e:
                    print(f"❌ Error al leer {path}: {e}")
    return jsons

def compute_common_keys(jsons: list) -> Set[str]:
    sets = []
    for _, data in jsons:
        flat = flatten(data)
        sets.append(set(flat.keys()))
    return set.intersection(*sets)

def filter_json_by_keys(original: Dict[str, Any], common_keys: Set[str]) -> Dict[str, Any]:
    flat = flatten(original)
    reduced = {k: v for k, v in flat.items() if k in common_keys}
    return unflatten(reduced)

def main():
    print("🔍 Cargando JSONs...")
    raw_jsons = read_all_jsons(ROOT_DIR)
    print(f"📦 Total archivos: {len(raw_jsons)}")

    print("🔑 Calculando claves comunes...")
    common_keys = compute_common_keys(raw_jsons)
    print(f"✔️ Total claves comunes: {len(common_keys)}")

    output_dir = os.path.join(ROOT_DIR, "reduced")
    os.makedirs(output_dir, exist_ok=True)

    for path, data in raw_jsons:
        reduced = filter_json_by_keys(data, common_keys)
        filename = os.path.basename(path)
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reduced, f, indent=2, ensure_ascii=False)

    print(f"✅ Archivos reducidos guardados en: {output_dir}")

if __name__ == "__main__":
    main()


