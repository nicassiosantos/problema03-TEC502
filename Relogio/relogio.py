import time
import threading

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


def show_menu():
    print("\nMenu:")
    print("1. Observar a hora atual do relógio")
    print("2. Inserir um novo valor de drift do relógio")
    print("3. Inserir um novo valor para a hora do relógio")
    print("4. Sair")
    return input("Escolha uma opção: ")


def main():
    relogio = Relogio(1.2)

    relogio.start()

    while True:
        option = show_menu()

        if option == '1':
            print(f"Hora atual do relógio: {relogio.get_time():.2f} segundos")
        elif option == '2':
            new_drift = float(input("Insira o novo valor de drift: "))
            relogio.alter_drift(new_drift)
            print(f"Novo valor de drift ajustado para: {new_drift}")
        elif option == '3':
            new_time = float(input("Insira o novo valor para a hora: "))
            relogio.alter_time(new_time)
            print(f"Novo valor da hora ajustado para: {new_time}")
        elif option == '4':
            relogio.stop()
            print("Encerrando...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()

