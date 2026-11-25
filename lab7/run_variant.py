import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lab7 import *

SEQ = [29, 1, 24, 69, 52, 97, 27, 10, 88]

def walk_nodes(n, out):
    if n is None: return out
    walk_nodes(n.left, out); out.append(n); walk_nodes(n.right, out)
    return out

def depth_map(root):
    d = {}
    def rec(n, dep):
        if n is None: return
        d[id(n)] = dep; rec(n.left, dep + 1); rec(n.right, dep + 1)
    rec(root, 0); return d

def draw(tree_ser, title, fname, is_rb):
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.axis("off")
    if tree_ser is None:
        ax.text(0.5, 0.5, "порожньо", ha="center", va="center", fontsize=14)
    else:
        pos = {}; order = []
        def rec(n, dep):
            if n is None: return
            rec(n["l"], dep + 1); pos[id(n)] = (len(order), -dep); order.append(n); rec(n["r"], dep + 1)
        rec(tree_ser, 0)
        def edges(n):
            if n is None: return
            for c in (n["l"], n["r"]):
                if c is not None:
                    ax.plot([pos[id(n)][0], pos[id(c)][0]], [pos[id(n)][1], pos[id(c)][1]], color="#555", lw=1.2, zorder=1)
                edges(c)
        edges(tree_ser)
        for n in order:
            x, y = pos[id(n)]
            if is_rb:
                fc = "#d62828" if n["c"] == "R" else "#1d1d1d"
                tc = "white"
            else:
                fc, tc = "white", "black"
            ax.scatter([x], [y], s=900, c=fc, edgecolors="#1d1d1d", linewidths=1.2, zorder=2)
            ax.text(x, y, str(n["k"]), ha="center", va="center", fontsize=11, color=tc, zorder=3, weight="bold")
        xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs) - 0.7, max(xs) + 0.7); ax.set_ylim(min(ys) - 0.7, max(ys) + 0.7)
    ax.set_title(title, fontsize=12)
    fig.tight_layout(); fig.savefig(fname, dpi=160); plt.close(fig)

def stack_trace(root):
    events = []; stack = []
    def rec(x):
        if x is None: return
        stack.append(x.key); events.append(("виклик", x.key, list(stack)))
        rec(x.left)
        events.append(("друк", x.key, list(stack)))
        rec(x.right)
        stack.pop(); events.append(("повернення", x.key, list(stack)))
    rec(root)
    return events

data = {"seq": SEQ, "build": [], "trav": {}, "bst_del": [], "rb_del": []}

# 1. construction
b = BST(); r = RB()
for k in SEQ:
    b.log = []; b.insert(k); bt = b.log[-1]["text"]
    s_b = ser(b.root)
    r.log = []; r.insert(k); rlog = r.log
    s_r = ser(r.root)
    data["build"].append({"key": k, "bst_text": bt, "rb_log": [e["text"] for e in rlog], "bst": s_b, "rb": s_r})

# 2. traversals
def trav(n, mode, out):
    if n is None: return out
    if mode == "pre": out.append(n.key)
    trav(n.left, mode, out)
    if mode == "in": out.append(n.key)
    trav(n.right, mode, out)
    if mode == "post": out.append(n.key)
    return out
for name, root in (("bst", b.root), ("rb", r.root)):
    data["trav"][name] = {m: trav(root, m, []) for m in ("in", "pre", "post")}
data["stack_bst"] = stack_trace(b.root)
data["stack_rb"] = stack_trace(r.root)

# 3. BST deletions: right subtree root, left subtree root, main root
bt = bst_from(SEQ)
order_del = []
right_root = bt.root.right.key
left_root = bt.root.left.key
main_root = bt.root.key
for key in (right_root, left_root, main_root):
    before = ser(bt.root); bt.log = []
    bt.delete_key(key)
    data["bst_del"].append({"key": key, "before": before, "after": ser(bt.root), "log": [e["text"] for e in bt.log]})
data["bst_del_keys"] = [right_root, left_root, main_root]

# 4. RB deletions: successive black nodes with most black children
rt = rb_from(SEQ)
chosen = []
for _ in range(3):
    dep = depth_map(rt.root)
    cands = [n for n in walk_nodes(rt.root, []) if n.color == BLACK and count_black_children(n) >= 1]
    cands.sort(key=lambda n: (-count_black_children(n), dep[id(n)], n.key))
    target = cands[0]
    chosen.append(target.key)
    before = ser(rt.root); rt.log = []
    rt.delete_node(target)
    data["rb_del"].append({"key": target.key, "before": before, "after": ser(rt.root), "log": [e["text"] for e in rt.log]})
data["rb_del_keys"] = chosen
data["rb_final_inorder"] = inorder(rt.root)
data["bst_final_inorder"] = inorder(bt.root)
data["rb_root"] = rt.root.key

json.dump(data, open("data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("BST del keys", data["bst_del_keys"], "RB del keys", data["rb_del_keys"])
print("trav", data["trav"])
print("rb final inorder", data["rb_final_inorder"], "bst final", data["bst_final_inorder"])
for d in data["rb_del"]:
    print("RB del", d["key"], d["log"])
for d in data["bst_del"]:
    print("BST del", d["key"], d["log"])
