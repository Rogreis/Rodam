# Viabilidade de Publicação Online do Rodam

## Resumo Executivo

A aplicação já tem base sólida para web porque o núcleo usa FastAPI + Jinja2 + JavaScript no navegador.

Nível de viabilidade: Alto.

A maior parte do esforço não está em reescrever interface, e sim em:
- separar o modo Desktop (PyWebView) do modo Web
- tornar o estado por usuário (hoje é global no servidor)
- preparar inicialização para rodar em ambiente web com múltiplos workers

---

## O que já está pronto para Web

Arquitetura e código reaproveitáveis quase sem mudanças:
- Backend HTTP com FastAPI em [app.py](app.py)
- Templates Jinja2 em [templates/main.html](templates/main.html), [templates/search_modal.html](templates/search_modal.html), [templates/semantic_search_modal.html](templates/semantic_search_modal.html), [templates/settings_modal.html](templates/settings_modal.html)
- Recursos estáticos em [css/main_layout.css](css/main_layout.css), [css/paragraph_status.css](css/paragraph_status.css), [js/search_modal.js](js/search_modal.js)
- Endpoints de navegação e busca já expostos por HTTP (ex.: /api/navigate, /search, /api/semantic_search)
- Estrutura de fragmentos de UI em [ui_fragments](ui_fragments)
- Lógica de busca textual Whoosh em [helpers/search_engine.py](helpers/search_engine.py)

Conclusão: o front já roda em navegador e o backend já responde em padrão web.

---

## Pontos que precisam mudar para produção web

## 1) Inicialização do app para modo servidor

Problema atual:
- A inicialização principal ocorre no bloco if __name__ == '__main__' em [app.py](app.py), junto com criação de janela PyWebView.
- Se publicar com uvicorn app:app, partes críticas de inicialização podem não rodar do jeito esperado.

Alteração recomendada:
- mover inicialização de recursos (helpers.globals.initialize, carga do motor semântico) para evento de startup do FastAPI
- manter bloco desktop separado para execução local com janela

Impacto:
- aplicação previsível em Docker, Linux server, serviços PaaS e múltiplos workers.

## 2) Estado global compartilhado entre usuários

Problema atual:
- Configurações e histórico ficam no objeto global_config e em arquivo único Rodam.json (ver [helpers/config.py](helpers/config.py) e [helpers/globals.py](helpers/globals.py)).
- Em site público, isso mistura estado entre usuários (ex.: último parágrafo, tema, filtros de busca).

Alteração recomendada:
- introduzir estado por usuário/sessão
- persistir preferências em banco (SQLite/PostgreSQL), chaveadas por user_id/session_id
- endpoints de leitura/gravação de settings e histórico devem usar contexto do usuário

Impacto:
- evita vazamento de preferências entre usuários
- permite autenticação no futuro

## 3) Compatibilização de recursos Desktop-only

Trechos que exigem tratamento para Web:
- Integração PyWebView (ex.: window.pywebview.api.copy_to_clipboard) em [templates/main.html](templates/main.html)
- abertura de navegador com target _system em [templates/main.html](templates/main.html)
- classe RodamApi e criação de janela em [app.py](app.py)

Alteração recomendada:
- manter fallback web nativo para clipboard (já existe parcialmente)
- ajustar openSystemBrowser para usar comportamento padrão do navegador quando não estiver em WebView
- isolar funcionalidades desktop atrás de feature flag

## 4) Caminhos de dados e arquivos em ambiente servidor

Problema atual:
- dados em diretórios locais por usuário do sistema (~/.config ou APPDATA), via [helpers/globals.py](helpers/globals.py).
- em hospedagem containerizada, filesystem pode ser efêmero.

Alteração recomendada:
- parametrizar diretórios por variáveis de ambiente
- definir volume persistente para índices Whoosh/modelos semânticos
- separar dados de runtime (cache/index) de dados de configuração por usuário

## 5) Dependências pesadas para semântica

Problema atual:
- stack semântica inclui faiss-cpu, sentence-transformers e torch (ver [requirements.txt](requirements.txt)).
- custo de CPU/memória pode ser alto para hospedagem simples.

Alteração recomendada:
- publicar em 2 modos:
  - modo básico: leitura + busca textual
  - modo avançado: semântica habilitada com recursos maiores
- opcionalmente separar semântica em serviço dedicado

---

## Código que pode ser aproveitado integralmente

- Rotas FastAPI em [app.py](app.py) (com ajustes de estado e startup)
- Geradores de conteúdo e fragments em [helpers/html_content_generator.py](helpers/html_content_generator.py) e [ui_fragments](ui_fragments)
- Templates e CSS/JS atuais em [templates](templates), [css](css), [js](js)
- Busca textual Whoosh em [helpers/search_engine.py](helpers/search_engine.py)
- Lógica de parsing e formatação de parágrafos em [helpers/paper_format.py](helpers/paper_format.py)

---

## Código que pode ser ignorado no deploy web

Itens focados em empacotamento desktop:
- [build_exe.bat](build_exe.bat)
- [build_exe.sh](build_exe.sh)
- [Rodam.spec](Rodam.spec)
- [setup.iss](setup.iss)
- [rodam.desktop](rodam.desktop)
- [create_splash.py](create_splash.py)

Itens para manter apenas em perfil Desktop:
- integração pywebview em [app.py](app.py)
- APIs específicas de clipboard desktop (RodamApi)

---

## Riscos e observações técnicas

- Concorrência: global_config não é seguro para múltiplos usuários/threads/workers.
- Escalabilidade: índice Whoosh local e modelo semântico em memória exigem estratégia de cache e limites.
- Segurança: adicionar proteção básica (rate limit, headers, validação de entrada, logs estruturados).
- Observabilidade: incluir healthcheck e métricas para monitorar uso e latência.

---

## Plano de migração recomendado

Fase 1 (rápida, MVP web interno):
- separar startup web do startup desktop
- desativar recursos pywebview no modo servidor
- rodar com uvicorn em Linux (1 instância)

Fase 2 (multiusuário):
- criar camada de persistência por usuário/sessão
- migrar settings/histórico do arquivo global para banco
- revisar endpoints /api/save_settings, /api/log_paragraph_click, /api/window_loaded

Fase 3 (produção pública):
- containerizar (Docker)
- colocar reverse proxy (Nginx/Caddy)
- HTTPS, limites de requisição, logs e monitoramento
- política para recursos semânticos (on/off por ambiente)

---

## Sugestão de arquitetura de deploy

Opção simples:
- FastAPI + Uvicorn + Nginx em uma VM
- volume persistente para dados

Opção escalável:
- FastAPI containerizado
- banco PostgreSQL
- storage persistente para índices/modelos
- serviço semântico separado (opcional)

---

## Checklist de prontidão web

- Startup FastAPI independente de PyWebView
- Estado por usuário implementado
- Configuração por variáveis de ambiente
- Persistência definida (DB + volume)
- Segurança básica ativada
- Estratégia de semântica definida
- Deploy automatizado e rollback testado

---

Conclusão: publicar o Rodam online é totalmente viável com reaproveitamento alto do código atual. O principal trabalho é adaptar o modelo de estado (de desktop single-user para web multiusuário) e isolar funcionalidades específicas de desktop.

---

## Publicação sem custo e estudo financeiro

## É possível publicar sem custos?

Sim, é possível publicar sem custo inicial para um MVP, especialmente se a busca semântica ficar desativada no ambiente público gratuito.

Opções gratuitas viáveis:
- Render (free): fácil para FastAPI, mas com cold start.
- Railway (crédito gratuito): simples, porém limitado por crédito mensal.
- Fly.io (free limitado): bom com Docker, mas recursos pequenos.
- Oracle Cloud Free Tier: melhor capacidade gratuita para rodar backend continuamente, com maior complexidade operacional.

Observação importante:
- "Sem custo" em nuvem normalmente significa recursos limitados e sem garantia de desempenho constante.
- Para uso público estável, costuma surgir custo mensal baixo a moderado.

## Estratégia recomendada para começar sem custo

Fase A (custo zero):
- Publicar o backend em tier gratuito.
- Habilitar leitura + busca normal (Whoosh).
- Desabilitar busca semântica por padrão no ambiente web.

Fase B (baixo custo):
- Manter app em VPS barata ou PaaS econômico.
- Mover arquivos pesados (modelo/índice semântico) para Object Storage.
- Baixar para cache local no startup, ou manter microserviço semântico separado.

## Estudo financeiro (baixo custo)

Premissas deste estudo:
- Valores aproximados de mercado em USD/mês (podem variar por região e data).
- Câmbio de referência para leitura rápida: 1 USD ~= 5 BRL.
- Faixas conservadoras, não cotações oficiais.

### Cenário 1: MVP público econômico (sem semântica ativa)

Composição:
- App FastAPI em VPS/PaaS de entrada
- Sem banco dedicado (ou SQLite)
- Busca normal ativa

Faixa mensal estimada:
- Hospedagem app: USD 5 a USD 12
- Storage adicional: USD 0 a USD 2
- Tráfego: USD 0 a USD 5
- Total: USD 5 a USD 19 (aprox. BRL 25 a BRL 95)

### Cenário 2: Baixo custo com semântica eventual

Composição:
- App principal econômico
- Arquivos semânticos em Object Storage
- Carga semântica sob demanda (ou janela de uso limitada)

Faixa mensal estimada:
- Hospedagem app: USD 6 a USD 15
- Object Storage (20 a 100 GB): USD 1 a USD 8
- Egress/download de modelo: USD 1 a USD 10
- Total: USD 8 a USD 33 (aprox. BRL 40 a BRL 165)

### Cenário 3: Semântica sempre ativa (produção leve)

Composição:
- App principal + serviço semântico com mais RAM/CPU
- Storage persistente
- Maior consumo de rede

Faixa mensal estimada:
- App/API: USD 8 a USD 20
- Worker/serviço semântico: USD 15 a USD 60
- Object Storage + egress: USD 3 a USD 20
- Total: USD 26 a USD 100 (aprox. BRL 130 a BRL 500)

## Onde colocar arquivos pesados (modelo semântico e índices)

Serviços comuns de baixo custo:
- Cloudflare R2: bom para reduzir custo de egress em certos cenários.
- Backblaze B2: armazenamento barato, egress cobrado por faixa.
- AWS S3 (Standard/IA): robusto, mas pode ficar mais caro em egress.
- Wasabi: preço previsível para storage com políticas próprias de retenção.

Critério de escolha:
- Se o modelo for baixado poucas vezes: priorize simplicidade.
- Se houver muitos downloads: priorize custo de egress.
- Se houver processamento semântico frequente: considerar serviço semântico dedicado com cache local.

## Arquitetura econômica sugerida (prática)

Opção recomendada para baixo custo com evolução segura:
- App web (FastAPI) em instância de USD 5 a USD 10.
- Object Storage para arquivos grandes.
- Cache local do modelo no servidor para evitar download repetido.
- Flag de ambiente para ligar/desligar semântica.

Vantagem:
- Começa barato e cresce gradualmente sem reescrever a aplicação.

## Conclusão financeira

- Sim, é possível publicar sem custo para MVP/demonstração.
- Para operação pública contínua e estável, espere algo entre USD 5 e USD 33/mês nos cenários econômicos mais realistas.
- Semântica sempre ativa tende a elevar o custo para a faixa de USD 26 a USD 100/mês, dependendo de tráfego e memória.
