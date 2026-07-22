from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/agendamentos')
def get_agendamentos():
    # Retorna os dados mockados com os campos exigidos
    return jsonify([
        {"paciente": "Carlos Silva", "cpf": "111.222.333-44", "medico": "Dra. Ana Costa", "especialidade": "Cardiologia", "data": "25/07/2026", "horario": "09:00", "convenio": "Unimed", "status": "Confirmado"},
        {"paciente": "Mariana Souza", "cpf": "555.666.777-88", "medico": "Dr. João Pedro", "especialidade": "Ortopedia", "data": "26/07/2026", "horario": "14:30", "convenio": "Amil", "status": "Pendente"},
        {"paciente": "José Pereira", "cpf": "999.888.777-66", "medico": "Dra. Ana Costa", "especialidade": "Cardiologia", "data": "26/07/2026", "horario": "16:00", "convenio": "Bradesco", "status": "Cancelado"}
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)