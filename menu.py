from finance import (
    add_category,
    show_categories,
    add_transaction,
    show_transactions,
    calculate_balance,
    get_monthly_expenses,
    set_budget,
    check_budget_limits
)


def menu():
    while True:
        print("\n=== Personal Finance Manager ===")
        print("1. Добавить категорию")
        print("2. Показать категории")
        print("3. Добавить транзакцию")
        print("4. Показать все транзакции")
        print("5. Показать баланс")
        print("6. Показать расходы за месяц")
        print("7. Установить лимит")
        print("8. Проверить лимиты")
        print("9. Выход")

        choice = input("Выберите пункт меню: ")

        if choice == "1":
            name = input("Введите название категории: ").strip()
            category_type = input("Введите тип (income/expense): ").strip().lower()

            if category_type not in ("income", "expense"):
                print("Ошибка: тип должен быть income или expense.")
                continue

            add_category(name, category_type)

        elif choice == "2":
            show_categories()

        elif choice == "3":
            try:
                amount = float(input("Введите сумму: "))
                category_id = int(input("Введите ID категории: "))
                date = input("Введите дату (YYYY-MM-DD): ").strip()
                description = input("Введите описание: ").strip()

                add_transaction(amount, category_id, date, description)
            except ValueError:
                print("Ошибка: сумма должна быть числом, ID должен быть числом.")

        elif choice == "4":
            show_transactions()

        elif choice == "5":
            calculate_balance()

        elif choice == "6":
            month = input("Введите месяц в формате YYYY-MM: ").strip()
            get_monthly_expenses(month)

        elif choice == "7":
            try:
                category_id = int(input("Введите ID категории: "))
                month = input("Введите месяц в формате YYYY-MM: ").strip()
                limit_amount = float(input("Введите лимит: "))

                set_budget(category_id, month, limit_amount)
            except ValueError:
                print("Ошибка: ID должен быть числом, лимит должен быть числом.")

        elif choice == "8":
            month = input("Введите месяц в формате YYYY-MM: ").strip()
            check_budget_limits(month)

        elif choice == "9":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")