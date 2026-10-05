"""Serialize original fields without changing quantities, steps or ingredient order."""
SEASONINGS = {'น้ำมันพืช', 'ซีอิ๊วขาว', 'น้ำปลา', 'เกลือ', 'เนย', 'มายองเนส', 'ซอสมะเขือเทศ'}

def recipes_to_markdown(recipes):
    blocks = ['# คลังสูตรอาหารตัวอย่างสำหรับโครงงาน RAG']
    for r in recipes:
        parts = [f"## {r['recipe_id']} — {r['name']}"]
        for title, seasoning in [('วัตถุดิบ', False), ('เครื่องปรุง', True)]:
            rows = [f"| {n} | {i['name']} | {i['quantity']} |"
                    for n, i in enumerate(r['ingredients'], 1) if (i['name'] in SEASONINGS) == seasoning]
            body = '\n'.join(['| ลำดับ | รายการ | ปริมาณ |', '| --- | --- | --- |', *rows]) if rows else 'ไม่มีรายการ'
            parts.append(f'### {title}\n\n{body}')
        parts.extend([
            f"### จำนวนเสิร์ฟ\n\n{r['servings']} เสิร์ฟ",
            '### อุปกรณ์\n\n' + ('\n'.join('- ' + e for e in r['equipment']) or 'ไม่ระบุ'),
            '### ขั้นตอน\n\n' + '\n\n'.join(f'{n}. {s}' for n, s in enumerate(r['steps'], 1)),
            '### หมายเหตุ\n\n' + r['notes'],
            '### แหล่งที่มา\n\n' + r['source'],
        ])
        blocks.append('\n\n'.join(parts))
    return '\n\n'.join(blocks) + '\n'
