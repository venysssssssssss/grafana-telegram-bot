from action_manager import ActionManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from dashboard_xpaths import DASHBOARD_XPATHS
from browser import BrowserManager
from send_telegram_msg import send_informational_message
from authentication import Authenticator
from monitor_falhas import monitor_falhas
from execute_download_actions import execute_download_actions
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def collect_data_from_dashboard(driver, dashboard_name, actions, browser_manager, download_path, initial_run=True):
    xpaths = DASHBOARD_XPATHS.get(dashboard_name)
    
    if not xpaths:
        logger.error(f"Dashboard {dashboard_name} não encontrado!")
        return None

    try:
        if initial_run:
            # Interagir com os elementos específicos do dashboard apenas na primeira vez
            actions.click_element(xpaths['var_exibir'])
            actions.click_element(xpaths['opcao_exibir'])
        
        # Scroll até a tabela - Executado sempre antes de coletar dados ou fazer download
        browser_manager.scroll_to_table()
        logger.info("Scroll até a tabela concluído")

        if initial_run:
            # Executar ações de download apenas na primeira vez
            relatorio_path = execute_download_actions(actions, browser_manager, download_path)
            logger.info(f"Relatório baixado para o {dashboard_name} no caminho: {relatorio_path}")
        else:
            relatorio_path = None

        # Coletar TME, TEF, e Backlog
        tme_element = actions.find_element(xpaths['tme'])
        tme_xpath = tme_element.text if tme_element.text != 'No data' else '00:00:00'

        tef_element = actions.find_element(xpaths['tef'])
        tef_xpath = tef_element.text if tef_element.text != 'No data' else '00:00:00'

        backlog_xpath = actions.find_element(xpaths['backlog']).text

        if initial_run:
            logger.info(f"KPIs coletados para {dashboard_name}: TME={tme_xpath}, TEF={tef_xpath}, Backlog={backlog_xpath}")
        else:
            logger.info(f"KPIs coletados para {dashboard_name} durante monitoramento: TME={tme_xpath}, TEF={tef_xpath}, Backlog={backlog_xpath}")
        
        return {
            "tme": tme_xpath,
            "tef": tef_xpath,
            "backlog": backlog_xpath,
            "relatorio_path": relatorio_path
        }
    except NoSuchElementException as e:
        logger.error(f"Elemento não encontrado durante a coleta de dados no {dashboard_name}: {e}")
        return None
    except WebDriverException as e:
        logger.error(f"Erro no WebDriver durante a coleta de dados no {dashboard_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao coletar dados do {dashboard_name}: {e}")
        return None

def process_dashboard(driver, dashboard_name, dashboard_url, actions, browser_manager, download_path, initial_run=True):
    try:
        if initial_run:
            driver.get(dashboard_url)
            logger.info(f"Acessando o {dashboard_name}: {dashboard_url}")
            time.sleep(5)

            # Realizar autenticação somente para mvp1
            if dashboard_name == "mvp1":
                auth = Authenticator(driver)
                auth.authenticate()
                logger.info(f"Autenticação concluída para {dashboard_name}")
        else:
            # Durante o monitoramento, apenas atualize a página
            driver.refresh()
            time.sleep(5)
    except NoSuchElementException as e:
        logger.error(f"Erro de autenticação no {dashboard_name}: {e}")
        return
    except WebDriverException as e:
        logger.error(f"Erro de WebDriver ao tentar acessar {dashboard_name}: {e}")
        return
    except Exception as e:
        logger.error(f"Erro inesperado ao tentar acessar {dashboard_name}: {e}")
        return

    try:
        result = collect_data_from_dashboard(driver, dashboard_name, actions, browser_manager, download_path, initial_run)
        if result:
            return result
        else:
            logger.error(f"Falha ao coletar dados do {dashboard_name}")
            return None
    except Exception as e:
        logger.error(f"Erro ao processar o dashboard {dashboard_name}: {e}")
        return None

def main():
    # URLs e nomes dos dashboards MVP1 e MVP3
    dashboards = {
        "mvp1": "https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas",
        "mvp3": "https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd"
    }

    # Iniciar o navegador em uma única instância
    browser_manager = BrowserManager('data')
    driver = browser_manager.driver
    download_path = browser_manager.clean_download_directory('data')

    try:
        # Abrir a primeira aba para MVP1
        driver.get(dashboards["mvp1"])
        actions_mvp1 = ActionManager(driver)
        result_mvp1 = process_dashboard(driver, "mvp1", dashboards["mvp1"], actions_mvp1, browser_manager, download_path, initial_run=True)

        # Abrir uma nova aba para MVP3 na mesma sessão do navegador
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(dashboards["mvp3"])
        actions_mvp3 = ActionManager(driver)
        result_mvp3 = process_dashboard(driver, "mvp3", dashboards["mvp3"], actions_mvp3, browser_manager, download_path, initial_run=True)

        # Iniciar o monitoramento
        logger.info("Iniciando monitoramento de falhas para MVP1 e MVP3")

        # Variável para controlar o intervalo de tempo
        monitoramento_intervalo = 60  # 1 minuto em segundos

        while True:
            # Monitorar MVP1
            driver.switch_to.window(driver.window_handles[0])
            logger.info("Monitorando MVP1")
            # Recriar o objeto actions para a aba atual
            actions_mvp1 = ActionManager(driver)
            # Processar o dashboard sem executar os XPaths iniciais
            result_mvp1 = process_dashboard(driver, "mvp1", dashboards["mvp1"], actions_mvp1, browser_manager, download_path, initial_run=False)
            if result_mvp1:
                monitor_falhas(driver, result_mvp1["tme"], result_mvp1["tef"], result_mvp1["backlog"], actions_mvp1, browser_manager)
                logger.info("Monitoramento de falhas finalizado para MVP1")
            else:
                logger.error("Falha ao coletar dados para MVP1 durante o monitoramento")

            # Monitorar MVP3
            driver.switch_to.window(driver.window_handles[1])
            logger.info("Monitorando MVP3")
            # Recriar o objeto actions para a aba atual
            actions_mvp3 = ActionManager(driver)
            # Processar o dashboard sem executar os XPaths iniciais
            result_mvp3 = process_dashboard(driver, "mvp3", dashboards["mvp3"], actions_mvp3, browser_manager, download_path, initial_run=False)
            if result_mvp3:
                monitor_falhas(driver, result_mvp3["tme"], result_mvp3["tef"], result_mvp3["backlog"], actions_mvp3, browser_manager)
                logger.info("Monitoramento de falhas finalizado para MVP3")
            else:
                logger.error("Falha ao coletar dados para MVP3 durante o monitoramento")

            # Aguarde 1 minuto antes de repetir o monitoramento
            time.sleep(monitoramento_intervalo)
    except Exception as e:
        logger.error(f"Erro durante o processo principal: {e}")
    finally:
        driver.quit()
        logger.info("Todas as páginas foram acessadas e o navegador foi fechado.")

if __name__ == '__main__':
    main()
