from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, get_connection

app = Flask(__name__)


@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.type, COALESCE(SUM(t.amount), 0)
        FROM categories c
        LEFT JOIN transactions t ON t.category_id = c.id
        GROUP BY c.type
    """)
    rows = cursor.fetchall()
    conn.close()

    income = 0
    expense = 0

    for row in rows:
        if row[0] == "income":
            income = row[1]
        elif row[0] == "expense":
            expense = row[1]

    balance = income - expense

    return render_template(
        "index.html",
        income=income,
        expense=expense,
        balance=balance
    )


@app.route("/categories")
def categories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, type FROM categories ORDER BY type, name")
    categories_list = cursor.fetchall()

    conn.close()
    return render_template("add_category.html", categories=categories_list)


@app.route("/add_category", methods=["POST"])
def add_category():
    name = request.form.get("name", "").strip()
    category_type = request.form.get("type", "").strip().lower()

    if not name or category_type not in ("income", "expense"):
        return redirect(url_for("categories"))

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO categories (name, type) VALUES (?, ?)",
            (name, category_type)
        )
        conn.commit()
    except Exception as e:
        print("Ошибка при добавлении категории:", e)
    finally:
        conn.close()

    return redirect(url_for("categories"))


@app.route("/transactions", methods=["GET", "POST"])
def transactions():
    selected_month = request.form.get("month", "").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if selected_month:
        cursor.execute("""
            SELECT t.id, t.amount, c.name, c.type, t.date, t.description
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE substr(t.date, 1, 7) = ?
            ORDER BY t.date DESC, t.id DESC
        """, (selected_month,))
    else:
        cursor.execute("""
            SELECT t.id, t.amount, c.name, c.type, t.date, t.description
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            ORDER BY t.date DESC, t.id DESC
        """)

    transactions_list = cursor.fetchall()
    conn.close()

    return render_template(
        "transactions.html",
        transactions=transactions_list,
        selected_month=selected_month
    )


@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        category_id = request.form.get("category_id", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        try:
            amount = float(amount)
            category_id = int(category_id)

            cursor.execute("""
                INSERT INTO transactions (amount, category_id, date, description)
                VALUES (?, ?, ?, ?)
            """, (amount, category_id, date, description))
            conn.commit()
        except Exception as e:
            print("Ошибка при добавлении транзакции:", e)
        finally:
            conn.close()

        return redirect(url_for("transactions"))

    cursor.execute("SELECT id, name, type FROM categories ORDER BY type, name")
    categories_list = cursor.fetchall()
    conn.close()

    return render_template("add_transaction.html", categories=categories_list)

@app.route("/edit_transaction/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        category_id = request.form.get("category_id", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        try:
            amount = float(amount)
            category_id = int(category_id)

            cursor.execute("""
                UPDATE transactions
                SET amount = ?, category_id = ?, date = ?, description = ?
                WHERE id = ?
            """, (amount, category_id, date, description, transaction_id))
            conn.commit()
        except Exception as e:
            print("Ошибка при редактировании транзакции:", e)
        finally:
            conn.close()

        return redirect(url_for("transactions"))

    cursor.execute("""
        SELECT id, amount, category_id, date, description
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))
    transaction = cursor.fetchone()

    cursor.execute("""
        SELECT id, name, type
        FROM categories
        ORDER BY type, name
    """)
    categories_list = cursor.fetchall()

    conn.close()

    if not transaction:
        return redirect(url_for("transactions"))

    return render_template(
        "edit_transaction.html",
        transaction=transaction,
        categories=categories_list
    )


@app.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
    except Exception as e:
        print("Ошибка при удалении транзакции:", e)
    finally:
        conn.close()

    return redirect(url_for("transactions"))


@app.route("/monthly_report", methods=["GET", "POST"])
def monthly_report():
    selected_month = request.form.get("month", "").strip()

    report_data = []
    total_expense = 0
    total_income = 0

    if selected_month:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.name, c.type, COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE substr(t.date, 1, 7) = ?
            GROUP BY c.name, c.type
            ORDER BY c.type, SUM(t.amount) DESC
        """, (selected_month,))
        report_data = cursor.fetchall()

        cursor.execute("""
            SELECT c.type, COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE substr(t.date, 1, 7) = ?
            GROUP BY c.type
        """, (selected_month,))
        totals = cursor.fetchall()

        conn.close()

        for row in totals:
            if row[0] == "income":
                total_income = row[1]
            elif row[0] == "expense":
                total_expense = row[1]

    balance = total_income - total_expense

    return render_template(
        "monthly_report.html",
        selected_month=selected_month,
        report_data=report_data,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )


@app.route("/analytics")
def analytics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.date, COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE c.type = 'expense'
        GROUP BY t.date
        ORDER BY t.date
    """)
    daily_rows = cursor.fetchall()

    cursor.execute("""
        SELECT substr(t.date, 1, 7) || '-W' || strftime('%W', t.date), COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE c.type = 'expense'
        GROUP BY strftime('%Y-%W', t.date)
        ORDER BY t.date
    """)
    weekly_rows = cursor.fetchall()

    cursor.execute("""
        SELECT substr(t.date, 1, 7), COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE c.type = 'expense'
        GROUP BY substr(t.date, 1, 7)
        ORDER BY substr(t.date, 1, 7)
    """)
    monthly_rows = cursor.fetchall()

    conn.close()

    daily_labels = [row[0] for row in daily_rows]
    daily_values = [row[1] for row in daily_rows]

    weekly_labels = [row[0] for row in weekly_rows]
    weekly_values = [row[1] for row in weekly_rows]

    monthly_labels = [row[0] for row in monthly_rows]
    monthly_values = [row[1] for row in monthly_rows]

    return render_template(
        "analytics.html",
        daily_labels=daily_labels,
        daily_values=daily_values,
        weekly_labels=weekly_labels,
        weekly_values=weekly_values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values
    )


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)