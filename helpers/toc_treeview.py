
def get_tree_data():
    """
    Retorna a estrutura hierárquica da árvore.
    Suporta N níveis de profundidade.
    """
    return [
        {
            "id": "folder_fisica",
            "title": "Física Fundamental",
            "type": "folder",
            "secret_code": "CTX_FOLDER_PHYSICS",
            "children": [
                {
                    "id": "art_newton",
                    "title": "Gravidade Newtoniana",
                    "type": "file",
                    "article_id": 101 # ID para buscar o texto depois
                },
                {
                    "id": "folder_quantica",
                    "title": "Mecânica Quântica",
                    "type": "folder",
                    "secret_code": "CTX_FOLDER_QUANTUM",
                    "children": [
                        {
                            "id": "art_dualidade",
                            "title": "Dualidade Onda-Partícula",
                            "type": "file",
                            "secret_code": "CTX_ART_DUALITY",
                            "article_id": 102
                        },
                        {
                            "id": "art_emaranhamento",
                            "title": "Emaranhamento",
                            "type": "file",
                            "secret_code": "CTX_ART_ENTANGLEMENT",
                            "article_id": 103
                        }
                    ]
                }
            ]
        },
        {
            "id": "folder_config",
            "title": "Configurações",
            "type": "folder",
            "secret_code": "CTX_FOLDER_CONFIG",
            "children": [
                {
                    "id": "act_darkmode",
                    "title": "Modo Escuro",
                    "type": "file", # ou 'action'
                    "secret_code": "CTX_ACT_DARKMODE",
                    "article_id": 999
                }
            ]
        }
    ]
