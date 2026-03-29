from database import get_connection


def add_category(name, category_type):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO categories (name, type)
            VALUES (?, ?)
        """, (name, category_type))
        conn.commit()
        print("Категория успешно добавлена.")
    except Exception as e:
        print(f"Ошибка при добавлении категории: {e}")
    finally:
        conn.close()


def show_categories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, type FROM categories ORDER BY type, name")
    categories = cursor.fetchall()
    conn.close()

    if not categories:
        print("Категорий пока нет.")
        return

    print("\nСписок категорий:")
    for category in categories:
        print(f"ID: {category[0]} | Название: {category[1]} | Тип: {category[2]}")


def add_transaction(amount, category_id, date, description):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO transactions (amount, category_id, date, description)
            VALUES (?, ?, ?, ?)
        """, (amount, category_id, date, description))
        conn.commit()
        print("Операция успешно добавлена.")
    except Exception as e:
        print(f"Ошибка при добавлении операции: {e}")
    finally:
        conn.close()


def show_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.amount, c.name, c.type, t.date, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC, t.id DESC
    """)

    transactions = cursor.fetchall()
    conn.close()

    if not transactions:
        print("Операций пока нет.")
        return

    print("\nИстория операций:")
    for transaction in transactions:
        print(
            f"ID: {transaction[0]} | "
            f"Сумма: {transaction[1]} | "
            f"Категория: {transaction[2]} | "
            f"Тип: {transaction[3]} | "
            f"Дата: {transaction[4]} | "
            f"Описание: {transaction[5]}"
        )


def calculate_balance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.type, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        GROUP BY c.type
    """)

    result = cursor.fetchall()
    conn.close()

    income = 0
    expense = 0

    for row in result:
        if row[0] == "income":
            income = row[1] if row[1] else 0
        elif row[0] == "expense":
            expense = row[1] if row[1] else 0

    balance = income - expense

    print(f"\nОбщий доход: {income}")
    print(f"Общий расход: {expense}")
    print(f"Текущий баланс: {balance}")


def get_monthly_expenses(month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE c.type = 'expense' AND substr(t.date, 1, 7) = ?
        GROUP BY c.name
        ORDER BY SUM(t.amount) DESC
    """, (month,))

    expenses = cursor.fetchall()
    conn.close()

    if not expenses:
        print("За этот месяц расходов нет.")
        return

    print(f"\nРасходы за {month}:")
    total = 0
    for expense in expenses:
        print(f"Категория: {expense[0]} | Сумма: {expense[1]}")
        total += expense[1]

    print(f"Общая сумма расходов за месяц: {total}")


def set_budget(category_id, month, limit_amount):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO budgets (category_id, month, limit_amount)
            VALUES (?, ?, ?)
            ON CONFLICT(category_id, month)
            DO UPDATE SET limit_amount = excluded.limit_amount
        """, (category_id, month, limit_amount))

        conn.commit()
        print("Лимит успешно установлен.")
    except Exception as e:
        print(f"Ошибка при установке лимита: {e}")
    finally:
        conn.close()


def check_budget_limits(month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name, b.limit_amount, COALESCE(SUM(t.amount), 0)
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN transactions t
            ON t.category_id = b.category_id
            AND substr(t.date, 1, 7) = b.month
        WHERE b.month = ? AND c.type = 'expense'
        GROUP BY c.name, b.limit_amount
    """, (month,))

    results = cursor.fetchall()
    conn.close()

    if not results:
        print("Для этого месяца лимиты не установлены.")
        return

    print(f"\nПроверка лимитов за {month}:")
    for row in results:
        category_name, limit_amount, spent_amount = row
        print(f"Категория: {category_name}")
        print(f"Лимит: {limit_amount}")
        print(f"Потрачено: {spent_amount}")

        if spent_amount > limit_amount:
            print("Статус: Лимит превышен!")
        else:
            print("Статус: Лимит не превышен.")
        print("-" * 30)