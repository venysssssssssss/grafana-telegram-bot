import logging
import os
import time
from threading import Thread

import schedule
from action_manager import ActionManager
from authentication import Authenticator
from browser import BrowserManager
from dashboard_xpaths import DASHBOARD_XPATHS
from execute_download_actions import execute_download_actions
from monitor_falhas import (iniciar_monitoramento, monitor_falhas,
                            pausar_monitoramento)
from process_dashboard import process_dashboard
from schedule_regular import \
    schedule_regular_collections  # Importar o agendamento
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from send_telegram_msg import send_informational_message

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


def main():
    # URLs e nomes dos dashboards MVP1 e MVP3
    dashboards = {
        'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas',
        'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd',
    }

    # Iniciar o navegador em uma única instância
    browser_manager = BrowserManager(os.path.join(os.getcwd(), 'data'))
    driver_mvp1 = browser_manager.driver
    driver_mvp3 = browser_manager.driver
    download_path = browser_manager.clean_download_directory('data')

    # Configurar o gerenciador de ações para MVP1 e MVP3
    actions_mvp1 = ActionManager(driver_mvp1)
    actions_mvp3 = ActionManager(driver_mvp3)

    try:
        logger.info('Iniciando o agendamento das tarefas...')

        # Coletar KPIs iniciais (se necessário)
        kpis_mvp1 = process_dashboard(
            driver_mvp1,
            'mvp1',
            dashboards['mvp1'],
            actions_mvp1,
            browser_manager,
            download_path,
            initial_run=True,
        )

        kpis_mvp3 = process_dashboard(
            driver_mvp3,
            'mvp3',
            dashboards['mvp3'],
            actions_mvp3,
            browser_manager,
            download_path,
            initial_run=True,
        )

        # Configurar o agendamento regular das tarefas
        schedule_regular_collections(
            driver_mvp1,
            actions_mvp1,
            actions_mvp3,
            browser_manager,
            kpis_mvp1,
            kpis_mvp3,
        )

        # Iniciar monitoramento de falhas em uma thread separada
        monitor_falhas_thread = Thread(
            target=monitor_falhas,
            args=(
                driver_mvp1,
                driver_mvp3,
                dashboards['mvp1'],
                dashboards['mvp3'],
            ),
        )
        monitor_falhas_thread.start()
        logger.info('Monitoramento de falhas iniciado em thread separada')

        while True:
            schedule.run_pending()
            time.sleep(5)

    except Exception as e:
        logger.error(f'Erro durante o processo principal: {e}')
    finally:
        driver_mvp1.quit()
        driver_mvp3.quit()
        logger.info(
            'Todas as páginas foram acessadas e os navegadores foram fechados.'
        )


if __name__ == '__main__':
    main()
