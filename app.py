from flask import Flask, request, redirect, session
import sqlite3

ShopBoss = Flask(__name__)
ShopBoss.secret_key = "secret123"

# -------- DATABASE --------
def db():
    return sqlite3.connect("shopboss.db")

# -------- COMMON FORM UI --------
def form_ui(title, fields, button):
    inputs = ""
    for f in fields:
        inputs += f

    return f"""
    <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f2f2f2;">
        <form method="post" style="background:white;padding:30px;width:300px;">
            <h2 style="text-align:center;">{title}</h2>
            {inputs}
            <button style="width:100%;padding:10px;background:#ffd814;border:none;">
                {button}
            </button>
        </form>
    </div>
    """
# --------- HEADER ----------
def header():
    cart = session.get("cart", {})
    count = sum(cart.values())

    return f"""
    <div style="background:#131921;color:white;padding:10px;display:flex;align-items:center;">
        
        <div style="color:#ff9900;font-size:22px;font-weight:bold;margin-right:20px;">
            ShopBoss
        </div>

        <form action="/" method="get" style="display:flex;width:80%;">
            <input name="q" placeholder="Search products"
                   style="flex:1;padding:8px;border:none;">
            <button style="background:#febd69;border:none;padding:8px;">
                Search
            </button>
        </form>

        <div style="margin-left:20px;display:flex;gap:15px;">
            <a href="/" style="color:white;">Home</a>
            <a href="/cart" style="color:white;">Cart</a>
            <a href="/admin" style="color:white;">Admin</a>
            <a href="/signup" style="color:white;">SignUp</a>
        </div>
    </div>
    """
# -------- HOME --------
@ShopBoss.route("/")
def home():
    conn = db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    html = header() + '<div style="display:flex;flex-wrap:wrap;padding:25px;background:#eaeded;">'

    for p in products:
        html += f"""
        <div style="background:white;width:120px;margin:10px;padding:20px;">
            <img src="{p[3]}" style="width:100%;height:135px;">
            <h4>{p[1]}</h4>
            <b> ₹{p[2]}</b>
            <a href="/add/{p[0]}" style="display:block;background:#ffd814;padding:10px;text-align:center;color:black;">
                Add to Cart
            </a>
        </div>
        """

    html += "</div>"
    return html

# -------- ADD --------
@ShopBoss.route("/add/<int:id>")
def add(id):
    cart = session.get("cart", {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    session["cart"] = cart
    return redirect("/cart")

# -------- CART --------
@ShopBoss.route("/cart")
def cart():
    cart = session.get("cart", {})
    conn = db()

    total = 0
    html = header() + '<div style="display:flex;padding:30px;background:#eaeded;">'

    html += '<div style="width:70%;">'

    for pid, qty in cart.items():
        p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if p:
            subtotal = p[2] * qty
            total += subtotal

            html += f"""
            <div style="background:white;margin:10px;padding:15px;display:flex;">
                <img src="{p[3]}" style="width:150px;height:170px;margin-right:15px;">
                <div>
                    <h3>{p[1]}</h3>
                    <p>₹{p[2]} × {qty}</p>
                    <b>Subtotal: ₹{subtotal}</b>
                </div>
            </div>
            """

    html += "</div>"

    html += f"""
    <div style="width:30%;">
        <div style="background:white;padding:20px;">
            <h2>Subtotal</h2>
            <h3>₹{total}</h3>
            <a href="/address" style="display:block;background:#ffd814;padding:12px;text-align:center;color:black;">
                Proceed to Buy
            </a>
        </div>
    </div>
    """

    html += "</div>"
    conn.close()
    return html

# -------- LOGIN --------
@ShopBoss.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["u"] == "fayiz" and request.form["p"] == "2026":
            session["user"] = request.form["u"]
            return redirect("/")
        return "Invalid Login"

    return form_ui("----------User Login---------", [
        '<input name="u" placeholder="Username" style="width:100%;padding:10px;margin:10px 0;">',
        '<input name="p" type="password" placeholder="Password" style="width:100%;padding:10px;margin:10px 0;">'
    ], "LOGIN")

# -------- SIGNUP --------
@ShopBoss.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        return redirect("/login")

    return form_ui("----------User Sign Up---------", [
        '<input name="u" placeholder="Username" style="width:100%;padding:10px;margin:10px 0;">',
        '<input name="p" type="password" placeholder="Password" style="width:100%;padding:10px;margin:10px 0;">'
    ], "SIGN UP")

# -------- ADMIN --------
@ShopBoss.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if (request.form["u"] in ["admin","owner"]) and (request.form["p"] in ["admin","owner"]):
            return redirect("/panel")

    return form_ui("----------Admin Login---------", [
        '<input name="u" placeholder="Username" style="width:100%;padding:10px;margin:10px 0;">',
        '<input name="p" type="password" placeholder="Password" style="width:100%;padding:10px;margin:10px 0;">'
    ], "LOGIN")

# -------- PANEL --------
@ShopBoss.route("/panel", methods=["GET","POST"])
def panel():
    conn = db()

    if request.method == "POST":
        if "add" in request.form:
            conn.execute("INSERT INTO products (name,price,image) VALUES (?,?,?)",
                         (request.form["name"], request.form["price"], request.form["image"]))
        if "delete" in request.form:
            conn.execute("DELETE FROM products WHERE id=?", (request.form["id"],))
        conn.commit()

    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    html = header() + "<div style='padding:30px;'>"

    html += """
    <form method="post">
        <input name="name" placeholder="Name">
        <input name="price" placeholder="Price">
        <input name="image" placeholder="Image URL">
        <button name="add">Add</button>
    </form><hr>
    """

    for p in products:
        html += f"""
        <form method="post">
            <input type="hidden" name="id" value="{p[0]}">
            {p[1]} - ₹{p[2]}
            <button name="delete">Delete</button>
        </form>
        """

    html += "</div>"
    return html

# -------- ADDRESS --------
@ShopBoss.route("/address", methods=["GET","POST"])
def address():
    if "user" not in session:
        return redirect("/login")

    if not session.get("cart"):
        return redirect("/")

    if request.method == "POST":
        conn = db()
        cur = conn.cursor()

        for pid, qty in session["cart"].items():
            session["user"], pid, qty, request.form["address"]

        conn.commit()
        conn.close()
        session["cart"] = {}

        return "<h2 style='text-align:center;color:green;'>Order Placed</h2>"

    return form_ui("------Delivery Address-----", [
        '<textarea name="address" style="width:100%;height:30px;margin:10px 0;font-size:18px;"></textarea>'
    ], "PLACE ORDER")

# -------- RUN --------
if __name__ == "__main__":
    ShopBoss.run(debug=True)