import re
import json
import os

def parse_receipt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    def clean_price(price_str):
        if not price_str:
            return 0.0
        clean = price_str.replace(' ', '').replace(',', '.')
        return float(clean)

    item_pattern = re.compile(
        r'(?P<index>\d+)\.\n'
        r'(?P<name>.+)\n'
        r'(?P<count>[\d\s]+,\d{3})\s*x\s*'
        r'(?P<price>[\d\s]+,\d{2})\n'
        r'(?P<total>[\d\s]+,\d{2})',
        re.MULTILINE
    )

    datetime_pattern = re.search(
        r'Время:\s*(?P<date>\d{2}\.\d{2}\.\d{4})\s+(?P<time>\d{2}:\d{2}:\d{2})', 
        text
    )

    total_pattern = re.search(
        r'ИТОГО:\n(?P<total>[\d\s]+,\d{2})', 
        text
    )

    store_pattern = re.search(r'Филиал\s+(.+)', text)

    payment_method_pattern = re.search(
        r'(Банковская карта|Наличные):\n(?P<amount>[\d\s]+,\d{2})', 
        text
    )

    items = []
    matches = item_pattern.finditer(text)
    
    calculated_total = 0.0

    for match in matches:
        item = {
            "index": int(match.group("index")),
            "name": match.group("name").strip(),
            "quantity": clean_price(match.group("count")),
            "unit_price": clean_price(match.group("price")),
            "total_price": clean_price(match.group("total"))
        }
        items.append(item)
        calculated_total += item["total_price"]

    receipt_data = {
        "store_name": store_pattern.group(1).strip() if store_pattern else "Unknown",
        "date": datetime_pattern.group("date") if datetime_pattern else None,
        "time": datetime_pattern.group("time") if datetime_pattern else None,
        "items": items,
        "total_receipt": clean_price(total_pattern.group("total")) if total_pattern else 0.0,
        "total_calculated": round(calculated_total, 2),
        "payment_method": payment_method_pattern.group(1) if payment_method_pattern else "Unknown"
    }

    return receipt_data

if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        file_path = os.path.join(script_dir, "raw.txt")
        
        print(f"Ищу файл здесь: {file_path}")

        data = parse_receipt(file_path)
        
        json_output = json.dumps(data, ensure_ascii=False, indent=4)
        print(json_output)
        
        output_path = os.path.join(script_dir, "parsed_receipt.json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_output)
            
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл не найден по пути: {file_path}")
        print("Убедитесь, что файл называется именно raw.txt (без скрытых расширений)")
    except Exception as e:
        print(f"Произошла ошибка: {e}")