import os
import threading
import logging 
from flask import Flask, request, jsonify, render_template
from relogio import Relogio
import time 

app = Flask(__name__)

# Configurações de logging para suprimir logs de requisição do Flask
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

# Configurações do Relógio e Rede
# ID do relógio corrente obtido de variáveis de ambiente (padrão: '2')
ID_RELOGIO = os.getenv('ID_RELOGIO', '2')

# IP e porta dos relógios configurados via variáveis de ambiente (com valores padrão)
IP_RELOGIO1 = os.getenv('IP_RELOGIO1', "0.0.0.0")
PORTA_RELOGIO1 = os.getenv('PORTA_RELOGIO1', '4578')
URL_RELOGIO1 = f"http://{IP_RELOGIO1}:{PORTA_RELOGIO1}"

IP_RELOGIO2 = os.getenv('IP_RELOGIO2', "0.0.0.0")
PORTA_RELOGIO2 = os.getenv('PORTA_RELOGIO2', '4574')
URL_RELOGIO2 = f"http://{IP_RELOGIO2}:{PORTA_RELOGIO2}"

IP_RELOGIO3 = os.getenv('IP_RELOGIO3', "0.0.0.0")
PORTA_RELOGIO3 = os.getenv('PORTA_RELOGIO3', '4572')
URL_RELOGIO3 = f"http://{IP_RELOGIO3}:{PORTA_RELOGIO3}"

# Dicionário contendo informações dos relógios
RELOGIOS = {
    '1': {'url': URL_RELOGIO1, 'time': 0},
    '2': {'url': URL_RELOGIO2, 'time': 0},
    '3': {'url': URL_RELOGIO3, 'time': 0}
}

# Instanciação do objeto Relogio com drift de 1, a configuração dos relógios e o ID do relógio
relogio = Relogio(1, RELOGIOS, ID_RELOGIO)

# Rota para obter a hora do relógio
@app.route('/get_time/<id>', methods=['GET'])
def get_time(id):
    if not id:
        return jsonify({'message': 'ID é obrigatório'}), 400
    return jsonify({'time': f'{relogio.get_time()}'}), 200

# Rota para ajustar a hora do relógio
@app.route('/adjust_times', methods=['POST'])
def adjust_time():
    data = request.get_json()
    new_times = data.get('new_times', {})

    try:
        # Atualiza os tempos dos relógios na instância de Relogio
        for relogio_id, new_time in new_times.items():
            if relogio_id in relogio.relogios:
                relogio.relogios[relogio_id]['time'] = new_time 

        new_time = relogio.elect_new_master() 

        relogio.time = new_time

        return jsonify({'message': 'Tempo ajustado com sucesso', 'new_times': relogio.relogios}), 200
    except Exception as e:
        print(f"Ocorreu uma exceção {e}")
        return jsonify({'message': 'Erro ao tentar ajustar o tempo'}), 500

@app.route('/is_master_alive', methods=['GET'])
def is_master_alive():
    print('entrou cá')
    return jsonify({'master_alive': relogio.is_master_alive()}), 200

@app.route('/elect_new_master', methods=['POST'])
def elect_new_master():
    relogio.elect_new_master()
    return jsonify({'message': 'Eleição de novo mestre realizada'}), 200

# Rota para alterar o horário do relógio
@app.route('/alter_time', methods=['POST'])
def alter_time(): 
    data = request.get_json()
    new_time = data.get('new_time')

    if new_time is None:
        return jsonify({'message': 'Novo horário é obrigatório'}), 400

    try:
        relogio.alter_time(float(new_time))
        return jsonify({'message': 'Horário alterado com sucesso', 'new_time': new_time}), 200
    except Exception as e:
        print(f"Ocorreu uma exceção {e}")
        return jsonify({'message': 'Erro ao tentar alterar o horário'}), 500

# Rota para alterar o drift do relógio
@app.route('/alter_drift', methods=['POST'])
def alter_drift(): 
    data = request.get_json()
    new_drift = data.get('new_drift')

    if new_drift is None:
        return jsonify({'message': 'Novo drift é obrigatório'}), 400

    try:
        relogio.alter_drift(float(new_drift))
        return jsonify({'message': 'Drift alterado com sucesso', 'new_drift': new_drift}), 200
    except Exception as e:
        print(f"Ocorreu uma exceção {e}")
        return jsonify({'message': 'Erro ao tentar alterar o drift'}), 500

@app.route('/get_clock_id', methods=['GET'])
def get_clock_id():
    return jsonify({'clock_id': ID_RELOGIO}), 200

@app.route('/')
def index():
    return render_template('index.html')


# Função para monitorar a hora do relógio em tempo real
def monitor_clock():
    print("\nModo de Monitoramento de Hora do Relógio (Pressione qualquer tecla para voltar ao menu):")
    while True:
        current_time = relogio.get_time()
        print(f"\rHora atual do relógio: {current_time:.2f} segundos", end='', flush=True)
        time.sleep(1)
        if input('\r') != '':
            break

# Função para exibir o menu e capturar as opções do usuário
def show_menu():
    while True:
        print("\nMenu:")
        print("1. Inserir um novo valor de drift do relógio")
        print("2. Inserir um novo valor para a hora do relógio")
        print("3. Monitorar hora do relógio")
        print("4. Sair")

        option = input("\nEscolha uma opção: ")

        if option == '1':
            new_drift = float(input("Insira o novo valor de drift: "))
            relogio.alter_drift(new_drift)
            print(f"Novo valor de drift ajustado para: {new_drift}")
        elif option == '2':
            new_time = float(input("Insira o novo valor para a hora: "))
            relogio.alter_time(new_time)
            print(f"Novo valor da hora ajustado para: {new_time}")
        elif option == '3':
            relogio.master = True
            print("Este relógio agora é mestre.")
        elif option == '4':
            monitor_clock()
        elif option == '5':
            relogio.stop()
            print("Encerrando...")
            break
        else:
            print("Opção inválida. Tente novamente.")




# Função principal que inicia o relógio e exibe o menu
def main():
    relogio.start()
    #show_menu()

# Execução do servidor Flask em uma thread separada e início da função principal
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host=eval(f"IP_RELOGIO{ID_RELOGIO}"), port=eval(f"PORTA_RELOGIO{ID_RELOGIO}"))).start()
    main()
