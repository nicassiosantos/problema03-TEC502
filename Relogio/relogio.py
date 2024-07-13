import time
import threading
import curses  

class Relogio:
    def __init__(self, drift):
        self.time = 0
        self.drift = drift
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.run).start()

    def run(self):
        while self.running:
            time.sleep(self.drift)
            self.time += 1

    def stop(self):
        self.running = False

    def alter_drift(self, drift):
        self.drift = drift

    def alter_time(self, time):
        self.time = time

    def get_time(self):
        return self.time


def display_time(stdscr, relogio):
    while relogio.running:
        stdscr.addstr(0, 0, f"Hora atual do relógio: {relogio.get_time():.2f} segundos")
        stdscr.refresh()
        time.sleep(1)


def show_menu(stdscr, relogio):
    stdscr.clear()
    stdscr.addstr(2, 0, "Menu:")
    stdscr.addstr(3, 0, "1. Inserir um novo valor de drift do relógio")
    stdscr.addstr(4, 0, "2. Inserir um novo valor para a hora do relógio")
    stdscr.addstr(5, 0, "3. Sair")
    stdscr.addstr(6, 0, "Escolha uma opção: ")
    stdscr.refresh()

    option = stdscr.getstr(7, 0).decode()

    stdscr.addstr(8, 0, f"Opção escolhida: {option}")
    stdscr.refresh()

    time.sleep(1)  # Breve pausa para exibir a opção escolhida

    if option == '1':
        stdscr.addstr(9, 0, "Insira o novo valor de drift: ")
        stdscr.refresh()
        new_drift = float(stdscr.getstr(10, 0).decode())
        relogio.alter_drift(new_drift)
        stdscr.addstr(11, 0, f"Novo valor de drift ajustado para: {new_drift}")
        stdscr.refresh()
    elif option == '2':
        stdscr.addstr(9, 0, "Insira o novo valor para a hora: ")
        stdscr.refresh()
        new_time = float(stdscr.getstr(10, 0).decode())
        relogio.alter_time(new_time)
        stdscr.addstr(11, 0, f"Novo valor da hora ajustado para: {new_time}")
        stdscr.refresh()
    elif option == '3':
        relogio.stop()
        stdscr.addstr(9, 0, "Encerrando...")
        stdscr.refresh()
        return False
    else:
        stdscr.addstr(9, 0, "Opção inválida. Tente novamente.")
        stdscr.refresh()

    time.sleep(1)  # Breve pausa para visualizar a mensagem de resposta

    return True


def main(stdscr):
    curses.curs_set(0)  # Esconde o cursor
    relogio = Relogio(1.2)

    relogio.start()

    # Thread para mostrar o tempo continuamente
    threading.Thread(target=display_time, args=(stdscr, relogio)).start()

    while True:
        if not show_menu(stdscr, relogio):
            break

        time.sleep(0.1)  # Pequena pausa para reduzir a carga de processamento

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
