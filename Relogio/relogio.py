import time
import threading
import requests

class Relogio:
    def __init__(self, drift, relogios, id_relogio):
        self.id = id_relogio  # ID do relógio atual
        self.time = 0  # Tempo inicial do relógio
        self.drift = drift  # Drift do relógio
        self.running = False  # Flag para controlar se o relógio está rodando
        self.relogios = relogios  # Dicionário de relógios na rede
        self.master = False  # Flag para indicar se o relógio é mestre
        self.last_sync_time = time.time()

    def start(self):
        self.running = True
        # Inicia a thread para incrementar o tempo do relógio
        threading.Thread(target=self.run).start()
        # Inicia a thread para sincronizar o relógio automaticamente
        threading.Thread(target=self.auto_synchronize).start()
        # Inicia a thread para monitorar o mestre
        threading.Thread(target=self.monitor_master).start()

    def run(self):
        while self.running:
            time.sleep(self.drift)  # Espera pelo intervalo de drift
            self.time += 1  # Incrementa o tempo do relógio

    def stop(self):
        self.running = False  # Para a execução do relógio

    def alter_drift(self, drift):
        self.drift = drift  # Altera o drift do relógio

    def alter_time(self, time):
        self.time = time  # Altera o tempo do relógio

    def get_time(self):
        return self.time  # Retorna o tempo atual do relógio

    def synchronize(self):
        start_time = time.time()  # Marca o início da sincronização

        # Coleta os tempos dos outros relógios
        request_times = self.collect_times()

        # Calcula os novos tempos baseados nos tempos coletados
        new_times, times = self.calculate_new_times(request_times)

        # Ajusta todos os relógios com os novos tempos calculados
        self.adjust_all_clocks(new_times, request_times)

        end_time = time.time()  # Marca o fim da sincronização
        self.last_sync_time = end_time  # Atualiza o tempo da última sincronização
        print(f"Sincronização completa em {end_time - start_time:.2f} segundos")

    def collect_times(self):
        request_times = {}  # Dicionário para armazenar os tempos das requisições
        threads = []  # Lista para armazenar as threads de requisição

        for relogio_id, relogio_info in self.relogios.items():
            if relogio_id != self.id:  # Evita requisitar o próprio tempo
                # Cria uma thread para requisitar o tempo do relógio
                thread = threading.Thread(target=self.request_time, args=(relogio_id, relogio_info, request_times))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()  # Espera todas as threads terminarem

        return request_times

    def calculate_new_times(self, request_times):
        new_times = {}  # Dicionário para armazenar os novos tempos calculados
        times = {}  # Dicionário para armazenar os tempos médios

        for relogio_id, relogio_info in self.relogios.items():
            if relogio_id != self.id and relogio_id in request_times and 'response_time' in request_times[relogio_id]:
                # Calcula o tempo médio de resposta para o relógio
                time0 = request_times[relogio_id]['request_time']
                time1 = request_times[relogio_id]['response_time']
                avg_time = int((time1 - time0) / 2)
                new_times[relogio_id] = request_times[relogio_id]['time'] + avg_time  # Novo tempo ajustado
                times[relogio_id] = avg_time

        times[self.id] = self.get_time()  # Adiciona o tempo do relógio atual

        return new_times, times

    def adjust_all_clocks(self, new_times, request_times):
        for relogio_id, relogio_info in self.relogios.items():
            if relogio_id != self.id and relogio_id in request_times and 'response_time' in request_times[relogio_id]:
                # Calcula o ajuste necessário e realiza o ajuste no relógio
                request_times[relogio_id]['time'] = request_times[relogio_id]['time'] + request_times[relogio_id]['avg_time']
                self.adjust_time(relogio_info, new_times)

    def auto_synchronize(self):
        while self.running:
            if self.master:  # Apenas sincroniza se o relógio for mestre
                self.synchronize()
            time.sleep(4)  # Espera 4 segundos antes de sincronizar novamente

    def request_time(self, relogio_id, relogio_info, request_times):
        try:
            request_times[relogio_id] = {
                'request_time': self.get_time()  # Marca o tempo da requisição
            }
            # Realiza a requisição para obter o tempo do relógio
            response = requests.get(f"{relogio_info['url']}/get_time/{relogio_id}")
            if response.status_code == 200:
                request_times[relogio_id]['response_time'] = self.get_time()  # Marca o tempo da resposta
                request_times[relogio_id]['avg_time'] = int((self.get_time() - request_times[relogio_id]['request_time']) / 2)
                request_times[relogio_id]['time'] = float(response.json()['time'])  # Armazena o tempo do relógio
        except requests.exceptions.RequestException:
            pass  # Ignora exceções de requisição

    def adjust_time(self, relogio_info, new_times):
        try:
            # Realiza a requisição para ajustar o tempo do relógio
            new_times[f'{self.id}'] = self.get_time()
            requests.post(f"{relogio_info['url']}/adjust_time", json={'new_times': new_times})
            # Atualiza os tempos na instância local se new_times for fornecido
            if new_times:
                for rid, time_value in new_times.items():
                    if rid in self.relogios:
                        self.relogios[rid]['time'] = time_value
        except requests.exceptions.RequestException:
            pass  # Ignora exceções de requisição

    def monitor_master(self):
        while self.running:
            if not self.master:  # Apenas monitora se não for mestre
                #print('Eu não sou o mestre')
                time_since_last_sync = time.time() - self.last_sync_time
                if time_since_last_sync > 10:  # Se passaram mais de 10 segundos desde a última sincronização
                    print('verificando')
                    # Verifica se o mestre ainda está online
                    if not self.is_master_alive():
                        # Tenta se eleger como novo mestre
                        self.elect_new_master()
            time.sleep(4)  # Verifica a cada 4 segundos
            #print('Eu sou o mestre')

    def is_master_alive(self):
        max_time = 0
        master_id = None
        #print(self.relogios)
        # Encontrar o relógio com o maior tempo
        for relogio_id, relogio_info in self.relogios.items():
            if relogio_id != self.id and 'time' in relogio_info:
                if relogio_info['time'] > max_time:
                    max_time = relogio_info['time']
                    master_id = relogio_id

        # Verificar se o relógio com o maior tempo está vivo
        if master_id:
            try:
                response = requests.get(f"{self.relogios[master_id]['url']}/get_time/{master_id}")
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                return False

        return False

    def elect_new_master(self):
        highest_time = self.get_time()
        potential_master_id = self.id

        for relogio_id, relogio_info in self.relogios.items():
            if relogio_id != self.id:
                relogio_time = relogio_info['time']
                if relogio_time > highest_time:
                    highest_time = relogio_time
                    potential_master_id = relogio_id

        if potential_master_id == self.id:
            self.master = True
            print("Este relógio agora é o novo mestre.")
        else:
            print(f"O relógio {potential_master_id} foi eleito como o novo mestre.")