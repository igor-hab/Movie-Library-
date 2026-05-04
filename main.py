import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.root.geometry("900x600")

        # Данные фильмов
        self.movies = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Фрейм для ввода данных
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        # Поле названия фильма
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=5)

        # Поле жанра
        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, padx=5, sticky="w")
        self.genre_combo = ttk.Combobox(
            input_frame,
            values=["Драма", "Комедия", "Фантастика", "Ужасы", "Боевик", "Мелодрама", "Документальный"],
            width=15
        )
        self.genre_combo.grid(row=0, column=3, padx=5)

        # Поле года выпуска
        ttk.Label(input_frame, text="Год выпуска:").grid(row=0, column=4, padx=5, sticky="w")
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=0, column=5, padx=5)

        # Поле рейтинга
        ttk.Label(input_frame, text="Рейтинг (0–10):").grid(row=0, column=6, padx=5, sticky="w")
        self.rating_entry = ttk.Entry(input_frame, width=8)
        self.rating_entry.grid(row=0, column=7, padx=5)

        # Кнопка добавления фильма
        add_button = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        add_button.grid(row=0, column=8, padx=10)

        # Кнопка удаления фильма
        delete_button = ttk.Button(input_frame, text="Удалить выбранный", command=self.delete_movie)
        delete_button.grid(row=0, column=9, padx=5)

        # Таблица для отображения фильмов
        columns = ("ID", "Название", "Жанр", "Год выпуска", "Рейтинг")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Название":
                self.tree.column(col, width=250)
            elif col == "Жанр":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=100)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Фрейм для фильтрации
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Фильтрация по жанру
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5)
        self.filter_genre = ttk.Combobox(
            filter_frame,
            values=["Все"] + ["Драма", "Комедия", "Фантастика", "Ужасы", "Боевик", "Мелодрама", "Документальный"]
        )
        self.filter_genre.set("Все")
        self.filter_genre.grid(row=0, column=1, padx=5)


        # Фильтрация по году выпуска
        ttk.Label(filter_frame, text="Год не ранее:").grid(row=0, column=2, padx=5)
        self.min_year_entry = ttk.Entry(filter_frame, width=10)
        self.min_year_entry.insert(0, "1900")
        self.min_year_entry.grid(row=0, column=3, padx=5)

        # Кнопки фильтрации
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=5)

        clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_button.grid(row=0, column=5, padx=5)

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_next_id(self):
        """Получение следующего ID для фильма"""
        if not self.movies:
            return 1
        return max(movie["id"] for movie in self.movies) + 1

    def validate_input(self, title, year_str, rating_str):
        """Проверка корректности ввода"""
        if not title.strip():
            messagebox.showerror("Ошибка", "Название фильма не может быть пустым")
            return False

        try:
            year = int(year_str)
            if year < 1888 or year > 2100:  # Первый фильм — 1888 год
                messagebox.showerror("Ошибка", "Год должен быть в диапазоне 1888–2100")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом")
            return False

        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом")
            return False

        return True

    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_combo.get().strip()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()

        if not genre:
            messagebox.showerror("Ошибка", "Выберите жанр фильма")
            return

        if not self.validate_input(title, year_str, rating_str):
            return

        movie = {
            "id": self.get_next_id(),
            "title": title,
            "genre": genre,
            "year": int(year_str),
            "rating": float(rating_str)
        }

        self.movies.append(movie)
        self.save_data()
        self.refresh_table()
        self.clear_input()

    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления")
            return

        item = selected[0]
        movie_id = int(self.tree.item(item, "values")[0])

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            self.movies = [m for m in self.movies if m["id"] != movie_id]
            self.save_data()
            self.refresh_table()

    def clear_input(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.genre_combo.set("")
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

    def refresh_table(self, data=None):
        """Обновление таблицы с фильмами"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_data = data if data is not None else self.movies

        for movie in display_data:
            self.tree.insert("", "end", values=(
                movie["id"],
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))

    def apply_filter(self):
        """Применение фильтров"""
        filtered = self.movies

        # Фильтр по жанру
        genre_filter = self.filter_genre.get()
        if genre_filter != "Все":
            filtered = [m for m in filtered if m["genre"] == genre_filter]

        # Фильтр по году выпуска
        min_year_str = self.min_year_entry.get().strip()
        if min_year_str:
            try:
                min_year = int(min_year_str)
                filtered = [m for m in filtered if m["year"] >= min_year]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат минимального года")
                return

        self.refresh_table(filtered)

    def clear_filter(self):
        """Сброс фильтров и обновление таблицы"""
        self.filter_genre.set("Все")
        self.min_year_entry.delete(0, tk.END)
        self.min_year_entry.insert(0, "1900")
        self.refresh_table()

    def save_data(self):
        """Сохранение данных в JSON-файл"""
        try:
            with open("movies.json", "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
        """Загрузка данных из JSON-файла"""
        if os.path.exists("movies.json"):
            try:
                with open("movies.json", "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                self.movies = []
        else:
            self.movies = []

    def on_closing(self):
        """Обработка закрытия окна с подтверждением"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти? Данные будут сохранены."):
            self.save_data()
            self.root.destroy()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

