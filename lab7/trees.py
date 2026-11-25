RED, BLACK = "R", "B"

class BNode:
    def __init__(self, key, color=None):
        self.key = key; self.left = None; self.right = None; self.color = color; self.parent = None

def bst_insert(root, key):
    if root is None:
        return BNode(key)
    cur = root
    while True:
        if key < cur.key:
            if cur.left is None:
                cur.left = BNode(key); cur.left.parent = cur; break
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = BNode(key); cur.right.parent = cur; break
            cur = cur.right
    return root

class RB:
    def __init__(self):
        self.root = None; self.nil_like = None
    def _rot_left(self, x):
        y = x.right; x.right = y.left
        if y.left: y.left.parent = x
        y.parent = x.parent
        if x.parent is None: self.root = y
        elif x is x.parent.left: x.parent.left = y
        else: x.parent.right = y
        y.left = x; x.parent = y
    def _rot_right(self, x):
        y = x.left; x.left = y.right
        if y.right: y.right.parent = x
        y.parent = x.parent
        if x.parent is None: self.root = y
        elif x is x.parent.right: x.parent.right = y
        else: x.parent.left = y
        y.right = x; x.parent = y
    def insert(self, key):
        z = BNode(key, RED)
        y = None; x = self.root
        while x is not None:
            y = x; x = x.left if key < x.key else x.right
        z.parent = y
        if y is None: self.root = z
        elif key < y.key: y.left = z
        else: y.right = z
        self._fix_insert(z)
    def _fix_insert(self, z):
        while z.parent is not None and z.parent.color == RED:
            p = z.parent; g = p.parent
            if p is g.left:
                u = g.right
                if u is not None and u.color == RED:
                    p.color = BLACK; u.color = BLACK; g.color = RED; z = g
                else:
                    if z is p.right:
                        z = p; self._rot_left(z); p = z.parent
                    p.color = BLACK; g.color = RED; self._rot_right(g)
            else:
                u = g.left
                if u is not None and u.color == RED:
                    p.color = BLACK; u.color = BLACK; g.color = RED; z = g
                else:
                    if z is p.left:
                        z = p; self._rot_right(z); p = z.parent
                    p.color = BLACK; g.color = RED; self._rot_left(g)
        self.root.color = BLACK

def bst_items(n):
    return [] if n is None else bst_items(n.left) + [n.key] + bst_items(n.right)

def fmt(n):
    if n is None: return "-"
    return f"{n.key}{n.color or ''}"
