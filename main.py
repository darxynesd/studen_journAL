import sqlite3
from tabulate import tabulate

DM_NAME= "university.db"


def get_connection():
    conn= sqlite3.connect(DM_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn= get_connection()
    cur= conn.cursor()


    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            major TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            instructor TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
            UNIQUE(student_id, course_id)
        );
    """)

    conn.commit()
    conn.close()




def add_student():
    name= input("имя пользователя:").strip()
    age_str = input("age:").strip()
    major = input("major:").strip()


    try:
        age= int(age_str)
    except ValueError:
        print('need numd')
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, age, major) VALUES (?, ?, ?);",
        (name, age, major)
    )
    conn.commit()
    conn.close()
    print("Студента додано.")


def list_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, major FROM students;")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Поки що студентів немає.")
        return

    print(tabulate(rows, headers=["ID", "Name", "Age", "Major"], tablefmt="github"))


def update_student():
    list_students()
    sid = input("Введіть ID студента для редагування: ").strip()
    try:
        sid_int = int(sid)
    except ValueError:
        print("❌ Невірний ID.")
        return

    name = input("Нове ім'я (Enter — лишити без змін): ").strip()
    age_str = input("Новий вік (Enter — лишити без змін): ").strip()
    major = input("Нова спеціальність (Enter — лишити без змін): ").strip()

    conn = get_connection()
    cur = conn.cursor()

    # дістаємо поточні дані
    cur.execute("SELECT name, age, major FROM students WHERE id = ?;", (sid_int,))
    row = cur.fetchone()
    if not row:
        print("❌ Студента з таким ID не знайдено.")
        conn.close()
        return

    current_name, current_age, current_major = row

    if name == "":
        name = current_name
    if age_str == "":
        age = current_age
    else:
        try:
            age = int(age_str)
        except ValueError:
            print("❌ Вік має бути числом. Зміни не збережені.")
            conn.close()
            return
    if major == "":
        major = current_major

    cur.execute("""
        UPDATE students
        SET name = ?, age = ?, major = ?
        WHERE id = ?;
    """, (name, age, major, sid_int))

    conn.commit()
    conn.close()
    print("✅ Дані студента оновлено.")


# ---------- ОПЕРАЦІЇ З КУРСАМИ ----------

def add_course():
    name = input("Назва курсу: ").strip()
    instructor = input("Викладач: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (course_name, instructor) VALUES (?, ?);",
        (name, instructor)
    )
    conn.commit()
    conn.close()
    print("✅ Курс додано.")


def list_courses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id, course_name, instructor FROM courses;")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Поки що курсів немає.")
        return

    print(tabulate(rows, headers=["Course ID", "Course Name", "Instructor"], tablefmt="github"))


def update_course():
    list_courses()
    cid = input("Введіть ID курсу для редагування: ").strip()
    try:
        cid_int = int(cid)
    except ValueError:
        print("Невірний ID.")
        return

    name = input("Нова назва курсу (Enter — лишити без змін): ").strip()
    instructor = input("Новий викладач (Enter — лишити без змін): ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT course_name, instructor FROM courses WHERE course_id = ?;", (cid_int,))
    row = cur.fetchone()
    if not row:
        print("Курс з таким ID не знайдено.")
        conn.close()
        return

    current_name, current_instructor = row

    if name == "":
        name = current_name
    if instructor == "":
        instructor = current_instructor

    cur.execute("""
        UPDATE courses
        SET course_name = ?, instructor = ?
        WHERE course_id = ?;
    """, (name, instructor, cid_int))

    conn.commit()
    conn.close()
    print("Дані курсу оновлено.")



def enroll_student_to_course():
    print("\n--- Список студентів ---")
    list_students()
    sid = input("ID студента: ").strip()

    print("\n--- Список курсів ---")
    list_courses()
    cid = input("ID курсу: ").strip()

    try:
        sid_int = int(sid)
        cid_int = int(cid)
    except ValueError:
        print("ID мають бути числами.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # перевіримо, чи існує студент і курс
    cur.execute("SELECT id FROM students WHERE id = ?;", (sid_int,))
    if not cur.fetchone():
        print("Студента з таким ID не знайдено.")
        conn.close()
        return

    cur.execute("SELECT course_id FROM courses WHERE course_id = ?;", (cid_int,))
    if not cur.fetchone():
        print("Курсу з таким ID не знайдено.")
        conn.close()
        return

    try:
        cur.execute("""
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?);
        """, (sid_int, cid_int))
        conn.commit()
        print("Студента зареєстровано на курс.")
    except sqlite3.IntegrityError:
        print("⚠ Цей студент вже зареєстрований на цей курс.")
    finally:
        conn.close()


def list_students_by_course():
    print("\n--- Курси ---")
    list_courses()
    cid = input("Введіть ID курсу: ").strip()
    try:
        cid_int = int(cid)
    except ValueError:
        print("Невірний ID курсу.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.course_name, s.id, s.name, s.age, s.major
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.course_id
        WHERE c.course_id = ?;
    """, (cid_int,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("На цей курс ще ніхто не записаний або курс не існує.")
        return

    course_name = rows[0][0]
    print(f"\nСтуденти, зареєстровані на курс: {course_name}")
    # rows: (course_name, id, name, age, major)
    data = [r[1:] for r in rows]
    print(tabulate(data, headers=["ID", "Name", "Age", "Major"], tablefmt="github"))




def print_menu():
    print("\n=== Журнал студентів університету ===")
    print("1. Додати студента")
    print("2.Показати всіх студентів")
    print("3. Редагувати студента")
    print("4.Додати курс")
    print("5. Показати всі курси")
    print("6.Редагувати курс")
    print("7.Записати студента на курс")
    print("8. Показати студентів конкретного курсу")
    print("0. Вихід")


def main():
    init_db()

    while True:
        print_menu()
        choice = input("Ваш вибір:" ).strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            list_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            add_course()
        elif choice == "5":
            list_courses()
        elif choice == "6":
            update_course()
        elif choice == "7":
            enroll_student_to_course()
        elif choice == "8":
            list_students_by_course()
        elif choice == "0":
            print("До побачення!")
            break
        else:
            print("Невірний вибір, спробуйте ще раз")

if __name__ == "__main__":
    main()
    