from helpers.globals import global_config

class SearchFragment:
    def html(self):
        last_query = global_config.query
        
        msg_left = f"<p>Última busca acionada: <strong>{last_query}</strong></p>" if last_query else "<p>Nenhuma busca ativa.</p>"
        msg_right = f"<p>Resultados para: <strong>{last_query}</strong></p>" if last_query else "<p>Aguardando busca...</p>"

        # Script to open the modal automatically when this fragment is loaded
        script = "<script>showSearchModal();</script>"
        
        return {
            "left": f"{msg_left} {script}",
            "right": msg_right
        }
