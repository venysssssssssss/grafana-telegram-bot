import requests
import datetime

def send_telegram_message(message):
    telegram_token = '7226155746:AAEBPeOtzJrD_KQyeZinNBjh5HMmvHTBZLs'  # Substitua pelo token do seu bot do Telegram
    chat_id = '-1002165188451'  # Substitua pelo seu chat ID
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

# Função para enviar mensagens informacionais
def send_informational_message(metrics, tme_xpath, tef_xpath, backlog_xpath):
    count_success = metrics['count_success']
    count_business_error = metrics['count_business_error']
    count_system_failure = metrics['count_system_failure']
    falha_detectada = metrics['falha_detectada']

    if count_success is not None:
        total_processos = count_success + count_business_error + count_system_failure
        if total_processos > 0:
            percent_success = (count_success / total_processos) * 100
            percent_business_error = (count_business_error / total_processos) * 100
            percent_system_failure = (count_system_failure / total_processos) * 100
        else:
            percent_success = percent_business_error = percent_system_failure = 0

        message = (
            '🤖 *Automação PAP - MVP2*\n'
            f"{datetime.date.today().strftime('%d/%m/%Y')}\n\n"
            f'*Status do robô*: Operando ✅\n\n'
            f"📓*Informacional até {datetime.datetime.now().strftime('%Hh%M')}*\n"
            f'🗂*Backlog*: {backlog_xpath}\n'
            f'✅*Concluído com sucesso:* {count_success} ({percent_success:.2f}%)\n'
            f'⚠️*Erro de negócio:* {count_business_error} ({percent_business_error:.2f}%)\n'
            f'❌*Falha de sistema:* {count_system_failure} ({percent_system_failure:.2f}%)\n\n'
            f'⏱*Tempo médio de execução:* {tme_xpath}\n'
            f'⏱*Tempo de fila:* {tef_xpath}\n\n'
            f'🌐*Link para mais detalhes*: https://e-bots.co/grafana/goto/Fj3MALXIR?orgId=1 \n\n'
            f'🔰 Informacional desenv. - Projetos Tahto Aut/IA 🔰'
        )
        # send_telegram_message(message)
        print(message)

