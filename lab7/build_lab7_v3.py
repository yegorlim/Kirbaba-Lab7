import json, docx
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.shared import Pt, Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

D = json.load(open("data.json", encoding="utf-8"))
seq = D["seq"]
doc = docx.Document()
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(2)
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(14)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

def P(t, bold=False, align=AL.JUSTIFY, indent=True, size=14, after=6):
    p = doc.add_paragraph(); p.alignment = align
    p.paragraph_format.line_spacing = 1.0
    if indent: p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(t); r.bold = bold; r.font.size = Pt(size)
    return p

def H(t): return P(t, bold=True, align=AL.LEFT, indent=False, after=6)

def CAP(t):
    p = P(t, align=AL.LEFT, indent=False, size=14)
    p.paragraph_format.keep_with_next = True
    return p

def CELL(cell, t, bold=False, size=12, center=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = AL.CENTER if center else AL.LEFT
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(t); r.bold = bold; r.font.size = Pt(size)

def header_row(t):
    t._tbl.tr_lst[0].get_or_add_trPr().append(OxmlElement("w:tblHeader"))

def no_split(row):
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))

def grid(t, widths):
    t.autofit = False
    g = t._tbl.tblGrid
    for j, gc in enumerate(g.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(widths[j] * 567)))
    for row in t.rows:
        for j, c in enumerate(row.cells):
            c.width = Cm(widths[j])

def simple_table(rows, widths, center_cols=()):
    t = doc.add_table(rows=len(rows), cols=len(widths)); t.style = doc.styles["Table Grid"]
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            CELL(t.cell(i, j), str(val), bold=(i == 0), center=(j in center_cols or i == 0))
    grid(t, widths); header_row(t)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t

def pic_table(items, widths, first_hdr, pic_w):
    """items: list of (label, explanation, [pic1, pic2]) ; first_hdr: list of headers"""
    t = doc.add_table(rows=1, cols=len(widths)); t.style = doc.styles["Table Grid"]
    for j, h in enumerate(first_hdr): CELL(t.cell(0, j), h, bold=True, center=True)
    header_row(t)
    for label, expl, pics in items:
        r1 = t.add_row(); no_split(r1)
        CELL(r1.cells[0], label, center=True)
        for j, pth in enumerate(pics, 1):
            c = r1.cells[j]; c.text = ""; c.paragraphs[0].alignment = AL.CENTER
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
            c.paragraphs[0].add_run().add_picture(pth, width=Cm(pic_w))
        r2 = t.add_row(); no_split(r2)
        m = r2.cells[0].merge(r2.cells[len(widths) - 1])
        CELL(m, expl)
    grid(t, widths)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t

def code(lines):
    for ln in lines:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.5)
        r = p.add_run(ln); r.font.name = "Courier New"; r.font.size = Pt(10)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)

EXTRA = {
 24: "Перефарбування: 24 стає чорним, 1 і 29 – червоними (властивості 4 і 5 відновлено).",
 69: "Корінь 24 після перефарбування став червоним; за властивістю 2 його фарбуємо в чорний.",
 52: "Перефарбування: 52 стає чорним, 29 і 69 – червоними.",
 88: "Перефарбування: 88 стає чорним, 69 і 97 – червоними.",
}

def cols(t):
    out = []
    def w(n):
        if n is None: return
        w(n["l"]); out.append(f"{n['k']} ({'ч' if n['c'] == 'B' else 'р'})"); w(n["r"])
    w(t)
    return ", ".join(out)

def bh(tree):
    if tree is None: return 1
    return bh(tree["l"]) + (1 if tree["c"] == "B" else 0)

def height(tree):
    if tree is None: return 0
    return 1 + max(height(tree["l"]), height(tree["r"]))

def find(tree, key):
    if tree is None: return None
    if tree["k"] == key: return tree
    return find(tree["l"], key) or find(tree["r"], key)

def black_children(tree, key):
    n = find(tree, key)
    return sum(1 for c in (n["l"], n["r"]) if c is not None and c["c"] == "B")

# ---------- Title page ----------
C = AL.CENTER; R = AL.RIGHT
P("Міністерство освіти і науки України", align=C, indent=False, after=0)
P("Національний університет «Одеська політехніка»", align=C, indent=False, after=0)
P("Навчально-науковий інститут комп’ютерних систем", align=C, indent=False, after=0)
P("Кафедра інформаційних систем", align=C, indent=False, after=0)
for _ in range(6): P("", indent=False, after=0)
P("Лабораторна робота № 7", bold=True, align=C, indent=False, after=6)
P("з дисципліни: «Теорія алгоритмів»", align=C, indent=False, after=6)
P("Тема: «Робота з бінарним та червоно-чорним деревами пошуку»", align=C, indent=False, after=6)
P("Варіант № 8", align=C, indent=False, after=6)
for _ in range(7): P("", indent=False, after=0)
P("Виконав:", align=R, indent=False, after=0)
P("Студент групи АІ-252", align=R, indent=False, after=0)
P("Кірбаба Є.Д.", align=R, indent=False, after=12)
P("Перевірили:", align=R, indent=False, after=0)
P("Смик С. Ю.", align=R, indent=False, after=0)
P("Арсірій О.О.", align=R, indent=False, after=12)
for _ in range(5): P("", indent=False, after=0)
P("Одеса 2026", align=C, indent=False, after=0)
doc.add_page_break()

# ---------- Body ----------
H("Мета роботи:")
P("Метою виконання лабораторної роботи є набуття практичних навичок із проектування, реалізації, тестування та аналізу алгоритмів пошуку, вставки та видалення елементів із деревоподібних структур даних. В якості структур даних для задачі пошуку розглядаються бінарне дерево пошуку та червоно-чорне дерево.")

H("Завдання:")
P("Варіант 8: послідовність ключів для побудови дерев – " + ", ".join(map(str, seq)) + ".")
for t in [
    "1. Побудувати бінарне дерево пошуку (BST) та червоно-чорне дерево (RB-дерево) за покроковим описом вставки.",
    "2. Навести результати симетричного (inorder), прямого (preorder) та зворотного (postorder) обходів обох дерев. Для симетричного обходу навести стан стека викликів рекурсивної функції inorderTraversal.",
    "3. Видалити з бінарного дерева пошуку по черзі три кореневі елементи в такому порядку: правий корінь піддерева, лівий корінь піддерева, основний кореневий елемент.",
    "4. Видалити з червоно-чорного дерева по черзі три чорні елементи, які мають переважно чорних синів, і описати процедуру видалення.",
]:
    P(t, indent=False)

H("Результати виконання завдання:")

# 1. Build
P("1. Побудова дерев", bold=True, align=AL.LEFT, indent=False)
P("Вставка в BST виконується так: перший елемент стає коренем, кожен наступний порівнюється з вузлами, починаючи з кореня; менший елемент іде в ліве піддерево, більший – у праве, доки не знайдеться вільне місце. Вставка в RB-дерево виконується як вставка в BST з наступним відновленням властивостей: новий вузол фарбується в червоний колір, після чого застосовуються перефарбування і повороти за випадками (дядько червоний; дядько чорний з прямою лінією; дядько чорний з ламаною лінією), як у методичних вказівках.")
P("Як приклад на таблиці 7.1 наведено покрокову побудову обох дерев: після кожної вставки показано стан BST і RB-дерева та пояснення дій. Побудова дерев за послідовністю " + ", ".join(map(str, seq)) + " завершується такими результатами: висота BST дорівнює " + str(height(D["build"][-1]["bst"])) + ", RB-дерево має корінь " + str(D["build"][-1]["rb"]["k"]) + " (чорний) і висоту " + str(height(D["build"][-1]["rb"])) + ".")
CAP("Таблиця 7.1 – Покрокова побудова BST та RB-дерева за послідовністю варіанта 8")
items = []
for i, b in enumerate(D["build"], 1):
    rb_log = list(b["rb_log"]) + ([EXTRA[b["key"]]] if b["key"] in EXTRA else [])
    items.append((f"Вставка {b['key']}", "BST: " + b["bst_text"] + "\nRB: " + " ".join(rb_log),
                  [f"figs/b{i:02d}_bst.png", f"figs/b{i:02d}_rb.png"]))
pic_table(items, [2.2, 7.4, 7.4], ["Крок", "BST", "RB-дерево"], 6.8)

# 2. Traversals
tr = D["trav"]
P("2. Обходи дерев", bold=True, align=AL.LEFT, indent=False)
P("Результати трьох обходів обох дерев наведено в таблиці 7.2.")
CAP("Таблиця 7.2 – Результати обходів BST та RB-дерева")
simple_table([
    ["Обхід", "BST", "RB-дерево"],
    ["Симетричний (inorder)", ", ".join(map(str, tr["bst"]["in"])), ", ".join(map(str, tr["rb"]["in"]))],
    ["Прямий (preorder)", ", ".join(map(str, tr["bst"]["pre"])), ", ".join(map(str, tr["rb"]["pre"]))],
    ["Зворотний (postorder)", ", ".join(map(str, tr["bst"]["post"])), ", ".join(map(str, tr["rb"]["post"]))],
], [4.4, 6.3, 6.3])
P("Симетричний обхід обох дерев дає однакову відсортовану послідовність " + ", ".join(map(str, tr["bst"]["in"])) + ", що підтверджує коректність побудови. Прямий і зворотний обходи відрізняються, оскільки форма дерев різна: корінь BST дорівнює " + str(D["build"][-1]["bst"]["k"]) + ", а корінь RB-дерева після побудови – " + str(D["build"][-1]["rb"]["k"]) + ". Ключі однакові, змінюється лише порядок обходу та структура дерева.")
P("Стан стека викликів функції inorderTraversal наведено в таблиці 7.3 для обох дерев. Кожен вузол дає три події: виклик (вузол додається в стек), друк (після обходу лівого піддерева) і повернення (вузол знімається зі стека). У таблиці вершина стека записана першою.")
CAP("Таблиця 7.3 – Стан стека викликів inorderTraversal")
rows = [["Крок", "Подія (BST)", "Стек BST", "Подія (RB)", "Стек RB"]]
for i, (eb, er) in enumerate(zip(D["stack_bst"], D["stack_rb"]), 1):
    rows.append([str(i), f"{eb[0]} {eb[1]}", " ".join(map(str, reversed(eb[2]))) or "–",
                 f"{er[0]} {er[1]}", " ".join(map(str, reversed(er[2]))) or "–"])
simple_table(rows, [1.5, 3.6, 4.0, 3.6, 4.0], center_cols=(0,))
mb = max(len(s) for _, _, s in D["stack_bst"]); mr = max(len(s) for _, _, s in D["stack_rb"])
P(f"Максимальна глибина стека дорівнює {mb} для BST і {mr} для RB-дерева; вона визначається висотою відповідного дерева при зростанні шляху обходу.")

# 3. BST deletions
P("3. Видалення кореневих елементів з BST", bold=True, align=AL.LEFT, indent=False)
P("Видалення у BST виконується за стандартним алгоритмом: вузол без дочірніх елементів просто вилучається; вузол з одним дочірнім елементом замінюється цим піддеревом; вузол з двома дочірніми елементами замінюється мінімальним елементом правого піддерева, який потім видаляється з цього піддерева. Послідовні видалення трьох кореневих елементів за завданням наведено в таблиці 7.4.")
CAP("Таблиця 7.4 – Видалення кореневих елементів з BST")
expl_bst = [
 "Правий корінь піддерева основного кореня 29 – вузол 69 (два дочірні). Замінюючий ключ – 88 (мінімум правого піддерева): він займає місце 69, а 88 видаляється з правого піддерева.",
 "Лівий корінь піддерева основного кореня – вузол 1, який має одне праве піддерево з коренем 24. Воно займає місце 1 (замінюючий ключ – 24).",
 "Основний кореневий елемент 29 має два дочірні вузли. Замінюючий ключ – 52 (мінімум правого піддерева): він займає місце кореня, а 52 видаляється з правого піддерева.",
]
items = [(f"{i+1}. Видаляємо {D['bst_del_keys'][i]}", expl_bst[i], [f"figs/d{i+1}_bst_before.png", f"figs/d{i+1}_bst_after.png"]) for i in range(3)]
pic_table(items, [2.6, 7.2, 7.2], ["Крок", "До видалення", "Після видалення"], 6.8)
P("Після трьох видалень BST містить ключі " + ", ".join(map(str, D["bst_final_inorder"])) + ". Симетричний обхід повертає відсортовану послідовність, отже властивість пошуку збережено.")

# 4. RB deletions
P("4. Видалення чорних елементів з RB-дерева", bold=True, align=AL.LEFT, indent=False)
P("Критерій вибору: серед чорних вузлів беремо ті, що мають хоча б одного чорного сина (порожні листи nil не враховуються), і вибираємо вузол з найбільшою кількістю чорних синів; при однаковій кількості – вузол, ближчий до кореня. Критерій динамічний: після кожного видалення структура дерева змінюється, тому кандидати для наступного кроку визначаються заново. Після побудови такий вузол один – 24 (чорний, його чорний син 1); інші кандидати з’являються лише після видалень. Процедура видалення в RB-дереві виконує заміну вузла наступником, а потім відновлення властивостей за випадками. Результати наведено в таблиці 7.5.")
CAP("Таблиця 7.5 – Видалення чорних елементів з RB-дерева")
items = []
for i, d in enumerate(D["rb_del"]):
    cnt = black_children(d["before"], d["key"])
    log = list(d["log"])
    if d["key"] == 24:
        log.append("Вузол, що займає місце 24, має колір позиції 24 – чорний. Вилучений червоний вузол 27 не змінює чорної висоти, тому відновлення не потрібне.")
    expl = f"Чорних синів у вузла: {cnt}. " + ("\n".join(log) if log else "Відновлення не потрібне.")
    expl += f"\nДо видалення (ключ, колір): {cols(d['before'])}.\nПісля видалення: {cols(d['after'])}."
    items.append((f"{i+1}. Видаляємо {d['key']}", expl, [f"figs/r{i+1}_rb_before.png", f"figs/r{i+1}_rb_after.png"]))
pic_table(items, [2.6, 7.2, 7.2], ["Крок", "До видалення", "Після видалення"], 6.8)
P("Після трьох видалень RB-дерево містить ключі " + ", ".join(map(str, D["rb_final_inorder"])) + ", його корінь – " + str(D["rb_root"]) + ". Симетричний обхід повертає відсортовану послідовність, отже дерево залишається деревом пошуку. Кінцеве дерево (корінь 52) перевірено вручну: немає двох червоних вузлів поспіль (червоний 10 має чорного батька 1, червоний 88 – чорного батька 52), а кількість чорних вузлів на шляху від кореня до nil дорівнює 2 на всіх чотирьох шляхах.")

# Listing
P("Лістинг 7.1 наведено для функції inorderTraversal, стан стека якої описано в таблиці 7.3.")
CAP("Лістинг 7.1 – Симетричний обхід (inorderTraversal)")
code([
    "function inorderTraversal(x : Node):",
    "    if x == null",
    "        return",
    "    inorderTraversal(x.left)",
    "    print(x.key)",
    "    inorderTraversal(x.right)",
])

H("Висновки:")
P("У ході роботи побудовано бінарне дерево пошуку та червоно-чорне дерево за послідовністю варіанта 8, виконано симетричний, прямий та зворотний обходи, розглянуто стан стека рекурсивного обходу, а також виконано видалення трьох кореневих елементів з BST і трьох чорних елементів з RB-дерева.")
P("Симетричний обхід обох дерев дає однакову відсортовану послідовність, що підтверджує коректність вставки і видалення. Видалення в BST прості, але для вироджених дерев висота може зростати до O(n). Червоно-чорне дерево відновлює баланс після вставки і видалення: поворотів не більше двох (O(1)), а перефарбування може підніматися вгору по шляху до O(log n) разів, тому висота залишається O(log n). Для цієї невеликої послідовності висоти дерев близькі, але на великих наборах перевага RB-дерева зростає.")

H("Посилання на GitHub:")
P("https://github.com/<логін>/<репозиторій>/tree/main/lab7", indent=False)

doc.save("ЛР7_08_АІ-252_Кірбаба_Єгор.docx")
print("saved")
