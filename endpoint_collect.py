from fastapi import FastAPI, HTTPException
from selenium.webdriver import Chrome
from app.browser import BrowserManager
from app.process_dashboard import process_dashboard
from app.action_manager import ActionManager

app = FastAPI()

# Inicializar o BrowserManager e os drivers (garantindo que seja reutilizável)
browser_manager = BrowserManager()

driver_mvp1 = browser_manager.driver
driver_mvp3 = browser_manager.driver

# Definição dos dashboards e ações (simulações, ajuste conforme necessário)
dashboards = {
        'mvp1': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?orgId=1&refresh=5m&var-Robot=tahto-pap&var-Robot_id=51&var-exibir_itens=processados&var-exibir_10000&var-exibir_tarefas=todas',
        'mvp3': 'https://e-bots.co/grafana/d/b12d0f69-2249-46c9-9a3d-da56588d47f4/ebots-detalhe-do-robo?var-Robot=tahto-pap-mvp3&orgId=1&refresh=5m&var-Robot_id=92&var-exibir_itens=processados&var-exibir=10000&var-exibir_tarefas=todas&from=now%2Fd&to=now%2Fd',
    }

actions_mvp1 = ActionManager(driver_mvp1)
actions_mvp3 = ActionManager(driver_mvp3)

download_path = browser_manager.clean_download_directory('data')


@app.post('/executar-coleta')
async def executar_coleta():
    """
    Executa a coleta de KPIs para ambos os dashboards (MVP1 e MVP3).
    """
    try:
        # Executa a função process_dashboard para MVP1
        kpis_mvp1 = process_dashboard(
            driver_mvp1,
            'mvp1',
            dashboards['mvp1'],
            actions_mvp1,
            browser_manager,
            download_path,
            initial_run=True,
        )

        # Executa a função process_dashboard para MVP3
        kpis_mvp3 = process_dashboard(
            driver_mvp3,
            'mvp3',
            dashboards['mvp3'],
            actions_mvp3,
            browser_manager,
            download_path,
            initial_run=True,
        )

        return {
            'message': 'Coleta executada com sucesso.',
            'kpis_mvp1': kpis_mvp1,
            'kpis_mvp3': kpis_mvp3,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'Erro ao executar a coleta: {str(e)}'
        )
