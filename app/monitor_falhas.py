# Função para monitorar falhas e enviar mensagens de falha e recuperação
def monitor_falhas(driver):
    while True:
        (
            count_success,
            count_business_error,
            count_system_failure,
            falha_detectada,
            _,
            _,
            _,
        ) = collect_info(driver)

        if falha_detectada:
            send_telegram_message(
                'Falha de sistema\n\nℹ️ Informação: falha ao importar pedidos'
            )
            while falha_detectada:
                time.sleep(60)
                _, _, _, falha_detectada, _, _, _ = collect_info(driver)
            send_telegram_message(
                '✅ Robô retomado para produção - MVP1 ✅\n\n⏰ Status: operando normalmente'
            )

        time.sleep(60)  # Aguarda um minuto antes de verificar novamente
