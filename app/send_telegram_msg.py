import datetime
import logging
import os
import traceback

import requests
from browser import BrowserManager
from data_processing import DataProcessor

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
browser_manager = BrowserManager('data')
download_path = browser_manager.clean_download_directory('data')


def send_telegram_message(message, max_retries=3):
    telegram_token = os.getenv(
        'TELEGRAM_TOKEN', '7946551520:AAGJ0Xj2lQbjX48ysHmJ6oVejn9KdavyTvg'
    )
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '2065343573')
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}

    for attempt in range(1, max_retries):
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            logging.info('Responde acessado com sucesso!')
            return
        except requests.HTTPError as e:
            logging.error(
                f'HTTP error occurred: {e.response.status_code} - {e.response.text}'
            )
            traceback.print_exc()
        except requests.RequestException as e:
            logging.exception('Erro ao enviar mensagem: %s', e)
        logging.info(
            f'Tentativa {attempt} de {max_retries} falhou, tentando novamente...'
        )
    logging.error('Falha ao enviar a mensagem após várias tentativas.')


def send_informational_message(
    driver, tme_xpath, tef_xpath, backlog_xpath, relatorio_path, dashboard_name
):
    try:
        # Usar o caminho correto passado como argumento (relatorio_path)
        data_processor = DataProcessor(relatorio_path)
        metrics = data_processor.analyze_data()

        # Garantir que dashboard_name esteja em maiúsculas
        dashboard_name_upper = dashboard_name.upper()

        # Definir o link correto com base no dashboard
        if dashboard_name == 'mvp1':
            link_detalhes = 'https://e-bots.co/grafana/goto/2BJnrGrSR?orgId=1'
        elif dashboard_name == 'mvp3':
            link_detalhes = 'https://e-bots.co/grafana/goto/aUehNBRNR?orgId=1'
        else:
            link_detalhes = (
                'https://e-bots.co/grafana'  # Link genérico de fallback
            )

        if metrics == 'no_data':
            message = (
                f'🤖 *Automação PAP - {dashboard_name_upper}*\n{datetime.date.today().strftime("%d/%m/%Y")}\n\n'
                'Robô Ocioso (Sem Dados)'
            )
            send_telegram_message(message)
            logging.info(
                f'Mensagem de ociosidade enviada para {dashboard_name_upper}!'
            )
            return

        count_success = metrics.get('count_success', 0)
        count_business_error = metrics.get('count_business_error', 0)
        count_system_failure = metrics.get('count_system_failure', 0)
        total_processos = (
            count_success + count_business_error + count_system_failure
        )

        if total_processos > 0:
            percent_success = (count_success / total_processos) * 100
            percent_business_error = (
                count_business_error / total_processos
            ) * 100
            percent_system_failure = (
                count_system_failure / total_processos
            ) * 100
        else:
            percent_success = (
                percent_business_error
            ) = percent_system_failure = 0

        message = (
            f'🤖 *Automação PAP - {dashboard_name_upper}*\n{datetime.date.today().strftime("%d/%m/%Y")}\n\n'
            f'*Status do robô*: Operando ✅\n\n'
            f'📓*Informacional até {datetime.datetime.now().strftime("%Hh%M")}*\n'
            f'🗂*Backlog*: {backlog_xpath}\n'
            f'✅*Concluído com sucesso:* {count_success} ({percent_success:.2f}%)\n'
            f'⚠️*Erro de negócio:* {count_business_error} ({percent_business_error:.2f}%)\n'
            f'❌*Falha de sistema:* {count_system_failure} ({percent_system_failure:.2f}%)\n\n'
            f'⏱*Tempo médio de execução:* {tme_xpath}\n'
            f'⏱*Tempo de fila:* {tef_xpath}\n\n'
            f'🌐*Link para mais detalhes*: {link_detalhes}\n\n'
            f'🔰 Informacional desenv. - Projetos Tahto Aut/IA 🔰'
        )
        send_telegram_message(message)
        logging.info(
            f'Mensagem processada e enviada para {dashboard_name_upper}!'
        )
    except KeyError as e:
        logging.exception('Chave ausente nos dados: %s', e)
    except Exception as e:
        logging.exception(
            f'Erro inesperado ao enviar mensagem informativa para {dashboard_name_upper}: %s',
            e,
        )
