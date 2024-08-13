from action_manager import ActionManager
from browser import BrowserManager

from venv import logger


browser_manager = BrowserManager('data')
actions = ActionManager(browser_manager.driver)

def execute_download_actions(actions, browser_manager, download_path):
    """
    Executa uma sequência de ações para mover e interagir com elementos da página,
    realizar o download de um arquivo e renomeá-lo, e finaliza com o fechamento de um elemento.

    Args:
        actions (ActionManager): Instância do gerenciador de ações para interagir com a página.
        browser_manager (BrowserManager): Instância do gerenciador do navegador para gerenciar downloads.
        download_path (str): Caminho do diretório de download onde o arquivo será salvo.

    Returns:
        str: Caminho completo do arquivo baixado e renomeado.
    """

    actions.move_to_and_interact('//*[@id=":rl:"]', 'i')
    actions.click_element(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div/div[1]/button'
    )
    actions.click_element(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/label'
    )
    actions.click_element(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/div[2]/div/div/label'
    )
    actions.click_element(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/button'
    )
    logger.info("Ações para download concluídas")

    # Aguarda o download ser concluído
    browser_manager.wait_for_download_complete(download_path)
    relatorio_path = browser_manager.rename_latest_file(download_path, 'relatorio.csv')
    logger.info("Download concluído e arquivo renomeado")

    actions.click_element(
        '//*[@id="reactRoot"]/div[1]/div/div[3]/div[3]/div/div/div[1]/div[1]/button'
    )

    return relatorio_path
