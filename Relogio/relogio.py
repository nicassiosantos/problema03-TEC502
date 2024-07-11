import time 
import threading 

class Relogio: 
    def __init__(self, drift): 
        self.time = 0 
        self.drift = drift
        self.running = False

    def start(self):
        self.running= True
        threading.Thread(target=self.run).start()

    def run(self):
        while self.running:
            time.sleep(self.drift)
            self.time += 1

    def stop(self):
        self.running = False

    def alter_drift(self, drift): 
        self.drif = drift 

    def alter_time(self, time): 
        self.time = time 


def main(): 
    relogio = Relogio(1.2) 

    relogio.start()
    for i in range(10): 
        
        print(f"Relógio: {relogio.time:.2f} segundos")

        time.sleep(1)

    relogio.stop()


if __name__ == "__main__":
    main()
