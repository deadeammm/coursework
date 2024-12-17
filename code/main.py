import pygame
from chessboard import Board
import threading
from config import Config
from tkinter import ttk, Tk, messagebox, StringVar
import json
from pathlib import Path
from resloader import ResLoader
import queue
import bcrypt


class SettingsWindow:

    def __init__(self):
        self.cfg = Config.get()
        self._accounts_f = Path(__file__).with_name('accounts.json')

        self.result = False

    def center_window(self, width=None, height=None):
        """Центрирует окно по экрану."""
        self.root.update_idletasks()
        width = self.root.winfo_width() if width is None else width
        height = self.root.winfo_height() if height is None else height
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):

        def enter():
            """Обрабатывает вход пользователя."""
            if self._accounts_f.is_file() and user_var.get() and pass_var.get():
                with self._accounts_f.open('r') as fp:
                    acc = json.load(fp)
                    stored_hash = acc.get(user_var.get())
                    if stored_hash and bcrypt.checkpw(pass_var.get().encode(), stored_hash.encode()):
                        self.result = True
                        self.root.destroy()
                    else:
                        messagebox.showerror("Ошибка", "Неверный логин или пароль.")

        def registr():
            """Обрабатывает регистрацию пользователя."""
            if user_var.get() and pass_var.get():
                hashed_password = bcrypt.hashpw(pass_var.get().encode(), bcrypt.gensalt()).decode()
                acc = {user_var.get(): hashed_password}
                if self._accounts_f.is_file():
                    with self._accounts_f.open('r') as fp:
                        acc.update(json.load(fp))

                with self._accounts_f.open('w') as fp:
                    json.dump(acc, fp)
                reg_btn.config(state='disabled')
                messagebox.showinfo("Регистрация", "Регистрация успешна!")

        def on_closing():
            """Закрытие окна."""
            self.result = False
            self.root.destroy()

        # Настройка окна
        self.result = False
        self.root = Tk()
        self.root.title('Авторизация')
        self.root.resizable(False, False)

        # Переменные для полей ввода
        user_var = StringVar()
        pass_var = StringVar()

        # Главный фрейм
        frm = ttk.Frame(self.root, padding=20)
        frm.grid(sticky="nsew")

        # Заголовок
        ttk.Label(frm, text="Добро пожаловать!", font=("Helvetica", 16)).grid(column=0, row=0, columnspan=2, pady=10)

        # Поле ввода логина
        ttk.Label(frm, text="Логин:", font=("Helvetica", 12)).grid(column=0, row=1, sticky="w", pady=5)
        user_entry = ttk.Entry(frm, textvariable=user_var, font=("Helvetica", 12), width=25)
        user_entry.grid(column=1, row=1, pady=5)

        # Поле ввода пароля
        ttk.Label(frm, text="Пароль:", font=("Helvetica", 12)).grid(column=0, row=2, sticky="w", pady=5)
        pass_entry = ttk.Entry(frm, textvariable=pass_var, font=("Helvetica", 12), show="*", width=25)
        pass_entry.grid(column=1, row=2, pady=5)

        # Кнопки
        login_btn = ttk.Button(frm, text="Войти", command=enter)
        login_btn.grid(column=1, row=3, sticky="e", pady=10)

        reg_btn = ttk.Button(frm, text="Регистрация", command=registr)
        reg_btn.grid(column=0, row=3, sticky="w", pady=10)

        # Привязка обработчиков
        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        # Центрируем окно
        self.center_window()

        return self

    def choose_enemy(self):
        """Метод выбора противника с созданием компактного окна."""
        # Создаем новое окно
        self.root = Tk()
        self.result = 'bot'
        self.root.title("Выбор противника")
        self.root.resizable(False, False)

        # Переменная для выбора
        enemy_choice = StringVar(value=self.result)

        def on_submit():
            """Обработчик подтверждения выбора."""
            self.result = enemy_choice.get()
            self.cfg.ENEMY_IS_PLAYER = self.result == "player"
#             print("Выбор противника:", "Игрок" if self.cfg.ENEMY_IS_PLAYER else "Бот")

            self.root.destroy()

        # Создание стиля для радио-кнопок
        style = ttk.Style()
        style.configure("Custom.TRadiobutton", font=("Helvetica", 10))

        # Главный фрейм
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky="nsew")

        # Заголовок окна
        ttk.Label(
            frm,
            text="Выберите противника",
            font=("Helvetica", 12, "bold"),
            anchor="center"
        ).grid(column=0, row=0, columnspan=2, pady=10)

        # Радио-кнопки
        ttk.Radiobutton(
            frm,
            text="Играть против игрока",
            variable=enemy_choice,
            value="player",
            style="Custom.TRadiobutton"
        ).grid(column=0, row=1, columnspan=2, sticky="w", pady=5)

        ttk.Radiobutton(
            frm,
            text="Играть против бота",
            variable=enemy_choice,
            value="bot",
            style="Custom.TRadiobutton"
        ).grid(column=0, row=2, columnspan=2, sticky="w", pady=5)

        # Кнопка подтверждения
        submit_btn = ttk.Button(frm, text="Подтвердить", command=on_submit)
        submit_btn.grid(column=0, row=3, columnspan=2, pady=10)

        # Центрирование окна
        self.center_window(200, 170)
        return self

    def show(self):
        self.root.mainloop()
        return self.result


class Chess():

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Шахматы')

        self.screen = pygame.display.set_mode((int(800 * pygame.display.get_desktop_sizes()[0][0]
                                                   / pygame.display.get_desktop_sizes()[0][1]), 800))
        pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()

        self.board = Board(self.screen, 800, 600)
        self.board.new_game()
        self.bot_thread = None
        self.resources = ResLoader.get_instance()

        self.running = False

    def draw(self, events):
        if self.bot_thread is None:
            bkg = self.resources.getImage(Path(__file__).parent / "resources" / "background.jpg", *pygame.display.get_desktop_sizes()[0])
            self.screen.blit(bkg, pygame.Rect(0, 0, *pygame.display.get_desktop_sizes()[0]))
            self.board.draw()

        self.board.infopanel.draw(events, self.bot_thread is not None)

        pygame.display.update()

    def bot_move(self, bot, qres):
        if self.bot_thread is None:
            self.bot_thread = threading.Thread(target=bot.getBestMove, args=[qres], daemon=True)
            self.bot_thread.start()

        if not qres.empty():
            self.bot_thread = None
            f, t = qres.get()
            if f and t:
                self.board.selected_figure = self.board(f).figure
                self.board.clicked_square = self.board(t)
                pygame.time.wait(250)

                return self.board.selected_figure.move(self.board.clicked_square)

    def player_move(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # нажата кнопка мыши
                if event.button == 1:
                    return self.board.on_click(*pygame.mouse.get_pos())

    def start_game(self):
        self.running = True
        qres = queue.Queue(maxsize=1)
        while self.running:
            res = False
            events = pygame.event.get()
            self.draw(events)

            if not self.board.game_over():
                if self.board.turn == self.board.bot_color:
                    # ход соперника
                    if self.board.cfg.ENEMY_IS_PLAYER:
                        res = self.player_move(events)
                    else:
                        res = self.bot_move(self.board.enemy_bot, qres)
                else:
                    # ход игрока
                    if self.board.cfg.PLAYER_IS_BOT:
                        res = self.bot_move(self.board.player_bot, qres)
                    else:
                        res = self.player_move(events)

                self.board.infopanel.timers.update(self.board.turn, self.clock.get_time())

                if res:
                    self.resources.play_sound(Path(__file__).parent / "resources" / "sound.mp3")
                    print(f"Оценка позиции игрока = ", self.board.enemy_bot.evaluateBoard())

                    self.board.change_side()
                    print(self.board.is_in_game_over())

            for event in events:
                # Выход
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # нажата кнопка мыши
                    if event.button == 1:
                        self.board.infopanel.on_click(*pygame.mouse.get_pos())

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False  # Закрытие игры на Esc

            self.clock.tick(30)
        pygame.quit()  # Завершаем Pygame при выходе


if __name__ == '__main__':
    sw = SettingsWindow()
    if sw.login().show():
        sw.choose_enemy().show()
        chess = Chess()
        chess.start_game()
