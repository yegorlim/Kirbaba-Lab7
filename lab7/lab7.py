import json
RED, BLACK = "R", "B"

class N:
    __slots__ = ("key", "color", "left", "right", "parent")
    def __init__(self, key, color=None):
        self.key = key; self.color = color; self.left = None; self.right = None; self.parent = None

def col(n):
    return BLACK if n is None else n.color

def inorder(n, out=None):
    if out is None: out = []
    if n is not None:
        inorder(n.left, out); out.append(n.key); inorder(n.right, out)
    return out

def ser(n):
    if n is None: return None
    return {"k": n.key, "c": n.color, "l": ser(n.left), "r": ser(n.right)}

def count_black_children(n):
    return sum(1 for c in (n.left, n.right) if c is not None and c.color == BLACK)

def path_desc(n):
    return str(n.key)

class BST:
    def __init__(self):
        self.root = None; self.log = []
    def insert(self, key):
        if self.root is None:
            self.root = N(key); self.log.append({"op": "ins", "key": key, "text": f"Вставляємо елемент {key}. Дерево порожнє, елемент стає коренем."}); return
        cur = self.root; path = []
        while True:
            path.append(cur.key)
            if key < cur.key:
                if cur.left is None:
                    cur.left = N(key); cur.left.parent = cur; side = "лівим"; break
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = N(key); cur.right.parent = cur; side = "правим"; break
                cur = cur.right
        cmp = " → ".join(map(str, path))
        self.log.append({"op": "ins", "key": key, "text": f"Вставляємо елемент {key}. Шлях пошуку: {cmp}. Елемент стає {side} дочірнім елементом вузла {cur.key}."})
    def _min(self, n):
        while n.left is not None: n = n.left
        return n
    def delete_key(self, key):
        self.root = self._del(self.root, key)
    def _del(self, n, key):
        if n is None: return None
        if key < n.key: n.left = self._del(n.left, key)
        elif key > n.key: n.right = self._del(n.right, key)
        else:
            if n.left is None: return n.right
            if n.right is None: return n.left
            m = self._min(n.right)
            self.log.append({"op": "del", "key": key, "text": f"Вузол {key} має два дочірні вузли. Крайній лівий елемент правого піддерева – {m.key}: ставимо його на місце {key} і рекурсивно видаляємо {m.key} з правого піддерева."})
            n.key = m.key
            n.right = self._del(n.right, m.key)
        return n

class RB:
    def __init__(self):
        self.root = None; self.log = []
    def _rl(self, x):
        y = x.right; x.right = y.left
        if y.left: y.left.parent = x
        y.parent = x.parent
        if x.parent is None: self.root = y
        elif x is x.parent.left: x.parent.left = y
        else: x.parent.right = y
        y.left = x; x.parent = y
    def _rr(self, x):
        y = x.left; x.left = y.right
        if y.right: y.right.parent = x
        y.parent = x.parent
        if x.parent is None: self.root = y
        elif x is x.parent.right: x.parent.right = y
        else: x.parent.left = y
        y.right = x; x.parent = y
    def insert(self, key):
        z = N(key, RED); y = None; x = self.root
        while x is not None:
            y = x; x = x.left if key < x.key else x.right
        z.parent = y
        if y is None: self.root = z
        elif key < y.key: y.left = z
        else: y.right = z
        self.log.append({"op": "ins", "key": key, "text": f"Вставляємо елемент {key}" + (" – корінь." if y is None else f" як {'лівий' if key < y.key else 'правий'} дочірній елемент вузла {y.key}; фарбуємо його в червоний колір.")})
        self._fix_ins(z)
        self.root.color = BLACK
    def _fix_ins(self, z):
        while z.parent is not None and z.parent.color == RED:
            p = z.parent; g = p.parent
            if p is g.left:
                u = g.right
                if col(u) == RED:
                    self.log.append({"op": "case", "text": f"Дядько {u.key} червоний: Випадок 1. Перефарбовуємо {p.key} і {u.key} у чорний, {g.key} – у червоний; перевіряємо далі від {g.key}."})
                    p.color = BLACK; u.color = BLACK; g.color = RED; z = g
                else:
                    if z is p.right:
                        self.log.append({"op": "case", "text": f"Дядько {u.key if u else 'nil'} чорний, ланцюжок {g.key}-{p.key}-{z.key} утворює кут: подвійний поворот."})
                        z = p; self._rl(z); p = z.parent
                        self.log.append({"op": "rot", "text": "Лівий поворот навколо " + str(z.key) + " (перша частина подвійного повороту)."})
                    else:
                        self.log.append({"op": "case", "text": f"Дядько {u.key if u else 'nil'} чорний, ланцюжок {z.key}-{p.key}-{g.key} утворює пряму лінію: Випадок 2 (одинарний правий поворот)."})
                    p.color = BLACK; g.color = RED; self._rr(g)
                    self.log.append({"op": "rot", "text": f"Правий поворот навколо {g.key}, {p.key} стає коренем піддерева."})
            else:
                u = g.left
                if col(u) == RED:
                    self.log.append({"op": "case", "text": f"Дядько {u.key} червоний: Випадок 1. Перефарбовуємо {p.key} і {u.key} у чорний, {g.key} – у червоний; перевіряємо далі від {g.key}."})
                    p.color = BLACK; u.color = BLACK; g.color = RED; z = g
                else:
                    if z is p.left:
                        self.log.append({"op": "case", "text": f"Дядько {u.key if u else 'nil'} чорний, ланцюжок {g.key}-{p.key}-{z.key} утворює кут: подвійний поворот."})
                        z = p; self._rr(z); p = z.parent
                        self.log.append({"op": "rot", "text": "Правий поворот навколо " + str(z.key) + " (перша частина подвійного повороту)."})
                    else:
                        self.log.append({"op": "case", "text": f"Дядько {u.key if u else 'nil'} чорний, ланцюжок {z.key}-{p.key}-{g.key} утворює пряму лінію: Випадок 2 (одинарний лівий поворот)."})
                    p.color = BLACK; g.color = RED; self._rl(g)
                    self.log.append({"op": "rot", "text": f"Лівий поворот навколо {g.key}, {p.key} стає коренем піддерева."})
    def _min(self, n):
        while n.left is not None: n = n.left
        return n
    def _transplant(self, u, v):
        if u.parent is None: self.root = v
        elif u is u.parent.left: u.parent.left = v
        else: u.parent.right = v
        if v is not None: v.parent = u.parent
    def delete_node(self, z):
        y = z; y_color = y.color; x = None; x_parent = None
        if z.left is None:
            x = z.right; x_parent = z.parent; self._transplant(z, z.right)
        elif z.right is None:
            x = z.left; x_parent = z.parent; self._transplant(z, z.left)
        else:
            y = self._min(z.right); y_color = y.color; x = y.right
            if y.parent is z:
                x_parent = y
                if x is not None: x.parent = y
            else:
                x_parent = y.parent
                self._transplant(y, y.right); y.right = z.right; y.right.parent = y
            self._transplant(z, y); y.left = z.left; y.left.parent = y; y.color = z.color
            self.log.append({"op": "del", "key": z.key, "text": f"Вузол {z.key} має два дочірні вузли. Крайній лівий елемент правого піддерева – {y.key} ({'чорний' if y_color == BLACK else 'червоний'}): ставимо його на місце {z.key} і видаляємо {y.key} з його початкової позиції."})
        if y_color == BLACK:
            self._fix_del(x, x_parent)
    def _fix_del(self, x, xp):
        while x is not self.root and col(x) == BLACK:
            if x is xp.left:
                w = xp.right
                if col(w) == RED:
                    self.log.append({"op": "case", "text": f"Брат {w.key} червоний: Випадок 4. Перефарбовуємо {w.key} у чорний, {xp.key} – у червоний, лівий поворот навколо {xp.key}."})
                    w.color = BLACK; xp.color = RED; self._rl(xp); w = xp.right
                if col(w.left) == BLACK and col(w.right) == BLACK:
                    case = "Випадок 1" if xp.color == RED else "Випадок 5"
                    self.log.append({"op": "case", "text": f"Брат {w.key} чорний, його діти чорні: {case}. "
                        + ("Батько червоний – перефарбовуємо брата і батька." if xp.color == RED else "Перефарбовуємо брата у червоний і піднімаємось далі від батька " + str(xp.key) + ".")})
                    w.color = RED; x = xp; xp = x.parent
                else:
                    if col(w.right) == BLACK:
                        self.log.append({"op": "case", "text": f"Брат {w.key} чорний, близький син {w.left.key} червоний, далекий син чорний: Випадок 3. Правий поворот навколо {w.key}, перефарбування {w.left.key} і {w.key}."})
                        w.left.color = BLACK; w.color = RED; self._rr(w); w = xp.right
                    else:
                        self.log.append({"op": "case", "text": f"Брат {w.key} чорний, далекий син {w.right.key} червоний: Випадок 2. Лівий поворот навколо {xp.key}."})
                    w.color = xp.color; xp.color = BLACK
                    if w.right: w.right.color = BLACK
                    self._rl(xp); x = self.root
            else:
                w = xp.left
                if col(w) == RED:
                    self.log.append({"op": "case", "text": f"Брат {w.key} червоний: Випадок 4. Перефарбовуємо {w.key} у чорний, {xp.key} – у червоний, правий поворот навколо {xp.key}."})
                    w.color = BLACK; xp.color = RED; self._rr(xp); w = xp.left
                if col(w.right) == BLACK and col(w.left) == BLACK:
                    case = "Випадок 1" if xp.color == RED else "Випадок 5"
                    self.log.append({"op": "case", "text": f"Брат {w.key} чорний, його діти чорні: {case}. "
                        + ("Батько червоний – перефарбовуємо брата і батька." if xp.color == RED else "Перефарбовуємо брата у червоний і піднімаємось далі від батька " + str(xp.key) + ".")})
                    w.color = RED; x = xp; xp = x.parent
                else:
                    if col(w.left) == BLACK:
                        self.log.append({"op": "case", "text": f"Брат {w.key} чорний, близький син {w.right.key} червоний, далекий син чорний: Випадок 3. Лівий поворот навколо {w.key}, перефарбування {w.right.key} і {w.key}."})
                        w.right.color = BLACK; w.color = RED; self._rl(w); w = xp.left
                    else:
                        self.log.append({"op": "case", "text": f"Брат {w.key} чорний, далекий син {w.left.key} червоний: Випадок 2. Правий поворот навколо {xp.key}."})
                    w.color = xp.color; xp.color = BLACK
                    if w.left: w.left.color = BLACK
                    self._rr(xp); x = self.root
        if x is not None: x.color = BLACK
    def delete_key(self, key):
        n = self.root
        while n is not None and n.key != key:
            n = n.left if key < n.key else n.right
        self.delete_node(n)

def bst_from(seq):
    t = BST()
    for k in seq: t.insert(k)
    return t

def rb_from(seq):
    t = RB()
    for k in seq: t.insert(k)
    return t
