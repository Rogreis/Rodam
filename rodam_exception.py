import sys
import logging

class RodamException(Exception):
    """
    Exceção base personalizada para erros internos da aplicação Rodam.
    Ao ser instanciada, loga o erro e encerra a aplicação imediatamente.
    """
    def __init__(self, message: str):
        self.message = message
        
        # 1. Impressão na Console com destaque
        print(f"\n{'='*60}")
        print(f"💀 ERRO CRÍTICO (RodamException)")
        print(f"➡️  {message}")
        print(f"{'='*60}\n")
        
        # 2. Log do Erro
        try:
            logger = logging.getLogger("Rodam")
            logger.critical(f"RodamException (Fatal): {message}")
        except Exception:
            pass # Logger pode não estar configurado ainda

        # Inicializa a classe base (embora não vá retornar)
        super().__init__(message)
        
        # 3. Encerra a aplicação
        print("🛑 Encerrando a aplicação...")
        sys.exit(1)
