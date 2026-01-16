# To DO

Corrigir o erro que aparece na console
Salvar resultados da última busca
Recuperar resultados salvos quando usuário clicar em "Busca" na barra de navegação
Exibir os resultados
Evitar que a modal automática quando há dados de busca
No assuntos ver se a modal é exibida quando não há dados 
Colocar os dados da busca semântica no TUB_FILEs
Gerar checksums dos arquivos
Fazer download deles se diferentes

Implementar as restrições e ordenação  nos assuntos
Fazer testes e merge do repositório de semântica
Verificar a action do github
Implementar o instalado com ícone



Depois iniciar artigos com as sugestões do Gemini:

Entendi perfeitamente. O cenário mudou de uma **aplicação web centralizada** (onde todos acessam o mesmo servidor) para uma **aplicação distribuída** (cada usuário roda o Python na sua própria máquina localmente), mas os arquivos originais vêm de uma fonte central (GitHub).

O problema agora é de **sincronização**: Como o "Python Local" do usuário fala com o "Admin Remoto"?

O SQLite local não serve porque ele fica isolado no computador do usuário. Você precisa de um **intermediário na nuvem**. Aqui estão três abordagens robustas, ordenadas da mais integrada ao GitHub para a mais flexível:

---
---

### Opção 1: Usar o próprio GitHub (Issues) - *Recomendada*

Já que sua fonte de arquivos é o GitHub, o fluxo mais natural é usar a API do GitHub.

* **O Conceito:** O "comentário" do usuário vira uma **Issue** no repositório do GitHub.
* **O Fluxo:**
1. O usuário digita o comentário na aplicação Python local.
2. A aplicação usa a biblioteca `PyGithub` ou `requests` para criar uma *Issue* no repositório. O título da Issue pode ser o nome do arquivo (ex: `[Comentário] manual.md`).
3. **Aprovação:** O Admin recebe a notificação do GitHub. Se ele gostar do comentário, ele edita o arquivo Markdown original no repositório e fecha a Issue.
4. **Atualização:** Quando o usuário rodar a aplicação novamente (e baixar o ZIP), o comentário já estará lá, incorporado oficialmente no texto.


* **Vantagem:** Não precisa de banco de dados extra. Mantém tudo versionado.
* **Desvantagem:** O usuário precisa de um token do GitHub ou você precisa embutir um token de "bot" na aplicação (cuidado com segurança).

```python
# Exemplo simplificado de envio
from github import Github

def enviar_comentario_github(arquivo, usuario, texto, token):
    g = Github(token)
    repo = g.get_repo("seu_usuario/seu_repo")
    body_issue = f"Usuário: {usuario}\n\nComentário:\n{texto}"
    repo.create_issue(title=f"Comentário em {arquivo}", body=body_issue)

```

---

### Opção 2: Google Sheets como Backend (Low-Code)

Você mencionou Google Docs, e essa é uma ótima ideia, mas use o **Google Sheets**. Ele funciona como um banco de dados na nuvem gratuito e fácil de ler.

* **O Conceito:** A aplicação Python envia os dados para uma planilha online.
* **O Fluxo:**
1. Usuário comenta -> Python usa `gspread` (API do Google) -> Adiciona uma linha na planilha "Comentários Pendentes".
2. **Aprovação:** O Admin abre a planilha, lê e muda uma coluna de "Pendente" para "Aprovado".
3. **Exibição:** A aplicação Python do usuário, ao carregar o Markdown, também consulta essa planilha online, filtra apenas as linhas com "Aprovado" e exibe no rodapé.


* **Vantagem:** Muito fácil para o Admin gerenciar (interface de Excel).
* **Desvantagem:** Requer configuração de credenciais da API do Google (arquivo JSON) distribuído junto com o app.

---

### Opção 3: Backend como Serviço (Supabase ou Firebase)

Se você quer algo mais profissional que uma planilha, mas sem configurar servidor, use o **Supabase** (que é um banco de dados Postgres gratuito na nuvem).

* **O Conceito:** O Python conecta num banco remoto via API REST.
* **O Fluxo:**
1. Usuário comenta -> Python envia JSON para o Supabase (Tabela `comentarios`).
2. **Aprovação:** O Admin acessa o painel do Supabase (ou uma paginazinha web simples que você criar) e marca um *boolean* `aprovado = true`.
3. **Exibição:** A aplicação do usuário baixa o ZIP (conteúdo estático) E faz uma consulta rápida no Supabase para buscar comentários dinâmicos aprovados.


* **Vantagem:** Extremamente rápido, seguro, permite múltiplos usuários simultâneos sem conflito.
* **Implementação:**

```python
from supabase import create_client

url = "SUA_URL_SUPABASE"
key = "SUA_CHAVE_PUBLICA_ANONIMA"
supabase = create_client(url, key)

# Enviar
supabase.table("comentarios").insert({"arquivo": "doc1.md", "texto": "Olá", "aprovado": False}).execute()

# Ler (apenas aprovados)
response = supabase.table("comentarios").select("*").eq("arquivo", "doc1.md").eq("aprovado", True).execute()

```

---

### E sobre o E-mail?

Você perguntou sobre e-mail.

* **Enviar é fácil:** Sua aplicação Python pode usar `smtplib` para disparar um e-mail para `admin@empresa.com` com o comentário.
* **O problema é a volta:** O Admin receberá o e-mail, mas como a aprovação dele volta para a aplicação? Ele teria que copiar o texto e colar manualmente no arquivo no GitHub.
* **Conclusão:** Use e-mail apenas como **alerta** ("Ei Admin, tem novo comentário na planilha/Supabase"), não como método de armazenamento.

### Resumo da Recomendação

1. Se você quer que o comentário **altere o arquivo original permanentemente**: Use a **Opção 1 (GitHub Issues)**. O Admin lê a Issue e edita o Markdown.
2. Se você quer que os comentários sejam uma **camada dinâmica sobre o arquivo**: Use a **Opção 3 (Supabase)** ou **Opção 2 (Google Sheets)**.

Qual dessas arquiteturas parece mais adequada ao nível técnico da sua equipe ou usuários?

---


Entendi perfeitamente. O cenário mudou de uma **aplicação web centralizada** (onde todos acessam o mesmo servidor) para uma **aplicação distribuída** (cada usuário roda o Python na sua própria máquina localmente), mas os arquivos originais vêm de uma fonte central (GitHub).

O problema agora é de **sincronização**: Como o "Python Local" do usuário fala com o "Admin Remoto"?

O SQLite local não serve porque ele fica isolado no computador do usuário. Você precisa de um **intermediário na nuvem**. Aqui estão três abordagens robustas, ordenadas da mais integrada ao GitHub para a mais flexível:

---

### Opção 1: Usar o próprio GitHub (Issues) - *Recomendada*

Já que sua fonte de arquivos é o GitHub, o fluxo mais natural é usar a API do GitHub.

* **O Conceito:** O "comentário" do usuário vira uma **Issue** no repositório do GitHub.
* **O Fluxo:**
1. O usuário digita o comentário na aplicação Python local.
2. A aplicação usa a biblioteca `PyGithub` ou `requests` para criar uma *Issue* no repositório. O título da Issue pode ser o nome do arquivo (ex: `[Comentário] manual.md`).
3. **Aprovação:** O Admin recebe a notificação do GitHub. Se ele gostar do comentário, ele edita o arquivo Markdown original no repositório e fecha a Issue.
4. **Atualização:** Quando o usuário rodar a aplicação novamente (e baixar o ZIP), o comentário já estará lá, incorporado oficialmente no texto.


* **Vantagem:** Não precisa de banco de dados extra. Mantém tudo versionado.
* **Desvantagem:** O usuário precisa de um token do GitHub ou você precisa embutir um token de "bot" na aplicação (cuidado com segurança).

```python
# Exemplo simplificado de envio
from github import Github

def enviar_comentario_github(arquivo, usuario, texto, token):
    g = Github(token)
    repo = g.get_repo("seu_usuario/seu_repo")
    body_issue = f"Usuário: {usuario}\n\nComentário:\n{texto}"
    repo.create_issue(title=f"Comentário em {arquivo}", body=body_issue)

```

---

### Opção 2: Google Sheets como Backend (Low-Code)

Você mencionou Google Docs, e essa é uma ótima ideia, mas use o **Google Sheets**. Ele funciona como um banco de dados na nuvem gratuito e fácil de ler.

* **O Conceito:** A aplicação Python envia os dados para uma planilha online.
* **O Fluxo:**
1. Usuário comenta -> Python usa `gspread` (API do Google) -> Adiciona uma linha na planilha "Comentários Pendentes".
2. **Aprovação:** O Admin abre a planilha, lê e muda uma coluna de "Pendente" para "Aprovado".
3. **Exibição:** A aplicação Python do usuário, ao carregar o Markdown, também consulta essa planilha online, filtra apenas as linhas com "Aprovado" e exibe no rodapé.


* **Vantagem:** Muito fácil para o Admin gerenciar (interface de Excel).
* **Desvantagem:** Requer configuração de credenciais da API do Google (arquivo JSON) distribuído junto com o app.

---

### Opção 3: Backend como Serviço (Supabase ou Firebase)

Se você quer algo mais profissional que uma planilha, mas sem configurar servidor, use o **Supabase** (que é um banco de dados Postgres gratuito na nuvem).

* **O Conceito:** O Python conecta num banco remoto via API REST.
* **O Fluxo:**
1. Usuário comenta -> Python envia JSON para o Supabase (Tabela `comentarios`).
2. **Aprovação:** O Admin acessa o painel do Supabase (ou uma paginazinha web simples que você criar) e marca um *boolean* `aprovado = true`.
3. **Exibição:** A aplicação do usuário baixa o ZIP (conteúdo estático) E faz uma consulta rápida no Supabase para buscar comentários dinâmicos aprovados.


* **Vantagem:** Extremamente rápido, seguro, permite múltiplos usuários simultâneos sem conflito.
* **Implementação:**

```python
from supabase import create_client

url = "SUA_URL_SUPABASE"
key = "SUA_CHAVE_PUBLICA_ANONIMA"
supabase = create_client(url, key)

# Enviar
supabase.table("comentarios").insert({"arquivo": "doc1.md", "texto": "Olá", "aprovado": False}).execute()

# Ler (apenas aprovados)
response = supabase.table("comentarios").select("*").eq("arquivo", "doc1.md").eq("aprovado", True).execute()

```

---




### E sobre o E-mail?

Você perguntou sobre e-mail.

* **Enviar é fácil:** Sua aplicação Python pode usar `smtplib` para disparar um e-mail para `admin@empresa.com` com o comentário.
* **O problema é a volta:** O Admin receberá o e-mail, mas como a aprovação dele volta para a aplicação? Ele teria que copiar o texto e colar manualmente no arquivo no GitHub.
* **Conclusão:** Use e-mail apenas como **alerta** ("Ei Admin, tem novo comentário na planilha/Supabase"), não como método de armazenamento.

### Resumo da Recomendação

1. Se você quer que o comentário **altere o arquivo original permanentemente**: Use a **Opção 1 (GitHub Issues)**. O Admin lê a Issue e edita o Markdown.
2. Se você quer que os comentários sejam uma **camada dinâmica sobre o arquivo**: Use a **Opção 3 (Supabase)** ou **Opção 2 (Google Sheets)**.

Qual dessas arquiteturas parece mais adequada ao nível técnico da sua equipe ou usuários?


---
---

Perfeito. Vamos dividir a solução em duas partes práticas: a **Estrutura da Tabela** no Supabase e a **Automação do Bot (Keep-Alive)** usando GitHub Actions (que é a forma mais simples e gratuita de rodar scripts Python agendados).

---

### Parte 1: Estruturando a Tabela no Supabase

Quando você entrar no painel do Supabase, vá na aba **Table Editor** (ícone de tabela à esquerda) e crie uma nova tabela chamada `comentarios`.

Aqui estão as colunas sugeridas e suas configurações:

| Nome da Coluna | Tipo de Dado  | Configuração Extra (Default/Primary) | Descrição                                                                               |
| -------------- | ------------- | ------------------------------------ | --------------------------------------------------------------------------------------- |
| `id`           | `int8`        | **Primary Key** (marcado)            | Identificador único. O Supabase gerencia sozinho.                                       |
| `created_at`   | `timestamptz` | Default: `now()`                     | Data e hora do comentário. Útil para ordenar.                                           |
| `arquivo`      | `text`        | -                                    | Nome do arquivo MD (ex: `manual.md`).                                                   |
| `usuario`      | `text`        | -                                    | Nome de quem comentou.                                                                  |
| `texto`        | `text`        | -                                    | O conteúdo do comentário.                                                               |
| `aprovado`     | `bool`        | Default: `FALSE`                     | **O segredo:** todo comentário nasce "falso" e só aparece quando você muda para "true". |

**Dica de Segurança (RLS):**
O Supabase cria tabelas com "Row Level Security" ativado por padrão. Para simplificar no início, você pode desativar o RLS ou criar uma "Policy" permitindo leitura/escrita pública (public anon). Como é uma aplicação interna/controlada, desativar o RLS momentaneamente facilita o desenvolvimento.

---

### Parte 2: O Bot "Keep-Alive" (Python + GitHub Actions)

Para evitar que o projeto entre em pausa após 7 dias de inatividade, precisamos de um script que faça uma conexão simples com o banco. Vamos automatizar isso para rodar, por exemplo, a cada 3 dias (para garantir) usando o **GitHub Actions**.

Você já está usando o GitHub para hospedar os arquivos, então é o lugar perfeito.

#### 1. O Script Python (`keep_alive.py`)

Crie este arquivo na raiz do seu repositório ou numa pasta `scripts/`. Ele apenas conecta e lê uma linha qualquer para gerar tráfego.

```python
import os
from supabase import create_client, Client

# Pegamos as credenciais das variáveis de ambiente (Segurança!)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são obrigatórias.")

def ping_supabase():
    supabase: Client = create_client(url, key)
    
    # Faz uma leitura simples. 
    # 'limit(1)' garante que seja leve, apenas para "acordar" o banco.
    try:
        response = supabase.table("comentarios").select("id").limit(1).execute()
        print("Ping realizado com sucesso! O Supabase está ativo.")
    except Exception as e:
        print(f"Erro ao conectar no Supabase: {e}")
        # Opcional: Aqui você poderia adicionar código para te enviar um e-mail de alerta caso falhe

if __name__ == "__main__":
    ping_supabase()

```

#### 2. Configurando as Credenciais (Secrets)

No seu repositório do GitHub:

1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Clique em **New repository secret**.
3. Adicione `SUPABASE_URL` (Sua URL do projeto).
4. Adicione `SUPABASE_KEY` (Sua chave `anon` ou `service_role`).

#### 3. O Agendador (Workflow do GitHub Actions)

Crie um arquivo no seguinte caminho dentro do seu repositório: `.github/workflows/keep_alive.yml`.

Este arquivo diz ao GitHub: "Instale Python, instale a lib do Supabase e rode o script acima a cada X dias".

```yaml
name: Supabase Keep-Alive

on:
  schedule:
    # Cron syntax: minuto hora dia_mes mes dia_semana
    # "0 0 * * 1,4" significa: Rodar às 00:00 toda Segunda (1) e Quinta (4)
    - cron: '0 0 * * 1,4'
  workflow_dispatch: # Permite rodar manualmente clicando num botão (para testar)

jobs:
  ping-database:
    runs-on: ubuntu-latest

    steps:
      - name: Baixar código do repositório
        uses: actions/checkout@v3

      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Instalar dependências
        run: |
          pip install supabase

      - name: Rodar script de Ping
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python keep_alive.py

```

### Resumo do Funcionamento

1. **Segunda e Quinta-feira**, o GitHub Actions vai acordar sozinho.
2. Ele vai baixar seu script `keep_alive.py`.
3. Ele vai injetar suas senhas (Secrets) de forma segura.
4. O script vai fazer um `SELECT` simples no Supabase.
5. O Supabase registra atividade e zera o contador de 7 dias. O projeto nunca será pausado.

Essa solução é **gratuita**, **segura** (senhas não ficam no código) e resolve o problema de infraestrutura sem você precisar contratar um servidor para rodar o bot. O que acha?


---
---

Essa é uma ideia criativa — aproveitar hardware que já está ligado 24/7 em sua casa para economizar recursos. No entanto, sendo bem direto: **é tecnicamente muito difícil e pouco prático** fazer isso nos equipamentos fornecidos pela Vodafone (ou qualquer operadora de telecomunicações), e vou explicar o porquê e quais são as suas alternativas reais.

### 1. O Router da Vodafone (Smart Router)

**Veredito: Praticamente Impossível / Não Recomendado**

* **Sistema Fechado:** Os routers das operadoras usam um firmware (sistema operacional) extremamente bloqueado. Embora por baixo usem Linux, você não tem acesso ao terminal (SSH) nem permissão para instalar pacotes como o Python.
* **Risco:** Tentar "desbloquear" o router (instalar um firmware customizado como OpenWrt) viola o contrato com a Vodafone, perde a garantia e, se der errado, você fica sem internet em casa.
* **Hardware Fraco:** Eles são desenhados estritamente para gerir tráfego de rede, com pouca memória sobrando para rodar aplicações externas.

### 2. A Box da TV (Vodafone TV Box - Android)

**Veredito: Possível (com "gambiarras"), mas Instável**

As boxes mais recentes da Vodafone (VTV 4K Pro, etc.) rodam sobre Android TV. Isso abre uma pequena porta, mas tem grandes obstáculos:

* **Como faria:** Teria que instalar um aplicativo chamado **Termux** (um emulador de terminal para Android). Dentro do Termux, você instalaria o Python e rodaria o script.
* **O Problema (Background Killing):** O Android TV é agressivo. Se você estiver assistindo à RTP ou Netflix, o sistema vai matar qualquer processo em segundo plano (como seu bot) para liberar memória para o vídeo. Seu bot pararia de funcionar sem aviso.
* **Dificuldade de Instalação:** Muitas vezes a loja de apps da Box é limitada. Você teria que habilitar "Modo Desenvolvedor", baixar o APK do Termux num pen drive ou via rede (sideloading) para instalar.
* **Reset:** Se a Vodafone atualizar o firmware da Box remotamente (o que fazem com frequência à noite), seu ambiente Python pode ser apagado.

---

### Qual a melhor solução "Caseira"?

Se você faz questão de rodar isso em casa (para não depender do GitHub Actions ou apenas pelo desafio técnico), aqui estão as melhores opções de hardware "Always-on":

#### A. Raspberry Pi (A Melhor Opção)

Se você tiver um Raspberry Pi (mesmo um modelo antigo como o Zero ou o 3) ou um computador velho com Linux:

1. Ele consome quase nada de energia.
2. É um Linux completo e aberto.
3. Você configura um "Cron Job" (agendador) e ele roda o script Python perfeitamente para sempre.

#### B. Um Telemóvel Android Antigo

Se tiver um smartphone Android velho na gaveta:

1. Instale o app **Termux** (gratuito na Play Store ou F-Droid).
2. Instale o Python: `pkg install python`.
3. Rode seu script.
4. Deixe-o ligado no carregador e conectado ao Wi-Fi.
5. *Nota:* Ainda sofre do risco do Android fechar o app, mas existem formas de travar o Termux na memória ("Wake Lock").

---

### Minha Recomendação Sincera

Considerando o trabalho x benefício: **Mantenha a ideia do GitHub Actions (Nuvem).**

Por que?

1. **Não falha:** O servidor do GitHub é infinitamente mais estável que uma Box de TV ou um telemóvel velho.
2. **Custo Zero:** É grátis e você não gasta nem a eletricidade da sua casa.
3. **Manutenção Zero:** Se a luz cair na sua casa em Portugal, o bot continua rodando na nuvem e seu banco de dados no Supabase não é pausado.

Se o objetivo é apenas "manter o Supabase vivo", o script no GitHub Actions que desenhamos anteriormente é a solução de engenharia mais robusta e profissional. Tentar colocar na Box da Vodafone vai te dar dor de cabeça configurar e frustração quando parar de funcionar do nada.

---
---

Ótima escolha. Usar o GitHub Actions é a solução mais profissional e "limpa" para isso.

Aqui está o pacote completo para você configurar o seu bot "Keep-Alive". Você precisará criar **dois arquivos** no seu repositório e fazer uma configuração rápida nas definições do GitHub.

### 1. O Script Python (`keep_alive.py`)

Crie um arquivo chamado `keep_alive.py` na raiz do seu projeto.

Este script conecta ao Supabase e faz uma leitura mínima (apenas 1 linha) na tabela de comentários. Isso é suficiente para o Supabase entender que o banco está em uso e resetar o contador de inatividade.

```python
import os
import sys
from supabase import create_client, Client

def main():
    # 1. Captura as credenciais das Variáveis de Ambiente (Segurança)
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("ERRO: As variáveis SUPABASE_URL e SUPABASE_KEY não foram encontradas.")
        sys.exit(1)

    # 2. Conecta ao Supabase
    try:
        supabase: Client = create_client(url, key)
        
        # 3. Executa uma consulta leve (Ping)
        # Seleciona apenas o ID de 1 comentário para economizar dados.
        # Mesmo que a tabela esteja vazia, a tentativa de conexão conta como atividade.
        response = supabase.table("comentarios").select("id").limit(1).execute()
        
        print("✅ SUCESSO: Conexão realizada e ping enviado ao Supabase.")
        print(f"Dados retornados: {response.data}")

    except Exception as e:
        print(f"❌ ERRO ao conectar no Supabase: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

```

---

### 2. O Agendador do GitHub (`.github/workflows/keep_alive.yml`)

Para que o GitHub rode esse script automaticamente, você precisa criar uma estrutura de pastas específica.

1. Crie uma pasta chamada `.github` (com o ponto na frente).
2. Dentro dela, crie uma pasta chamada `workflows`.
3. Dentro de workflows, crie um arquivo chamado `keep_alive.yml`.

Copie o conteúdo abaixo para este arquivo:

```yaml
name: Supabase Keep-Alive Bot

on:
  schedule:
    # Roda às 06:00 (UTC) toda Segunda e Quinta-feira.
    # Isso garante que nunca passe de 3-4 dias sem atividade.
    - cron: '0 6 * * 1,4'
  
  # Permite que você rode manualmente clicando num botão na aba "Actions" (para testar)
  workflow_dispatch:

jobs:
  ping-database:
    runs-on: ubuntu-latest

    steps:
      - name: Baixar código do repositório
        uses: actions/checkout@v3

      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Instalar dependências
        run: |
          pip install supabase

      - name: Rodar script de Ping
        env:
          # Aqui ele puxa as senhas que vamos configurar no passo 3
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python keep_alive.py

```

---

### 3. Configuração de Segurança (Secrets)

Para que o script funcione, o GitHub precisa saber a URL e a Senha do seu Supabase, mas **você nunca deve escrever isso diretamente no código**.

Faça o seguinte:

1. Vá no seu repositório no GitHub.
2. Clique na aba **Settings** (Configurações).
3. No menu lateral esquerdo, procure por **Secrets and variables** e clique em **Actions**.
4. Clique no botão verde **New repository secret**.
5. Crie dois segredos:
* **Nome:** `SUPABASE_URL`
* **Valor:** (Cole a URL do seu projeto Supabase, ex: `https://xyz.supabase.co`)


* **Nome:** `SUPABASE_KEY`
* **Valor:** (Cole a chave pública/anon do Supabase)





### Como testar agora mesmo?

Depois de fazer o "commit" e "push" desses arquivos para o GitHub:

1. Vá na aba **Actions** do seu repositório.
2. Você verá "Supabase Keep-Alive Bot" na lista à esquerda.
3. Clique nele e, do lado direito, haverá um botão **Run workflow**.
4. Clique para rodar. Se aparecer um "check" verde ✅ após alguns segundos, seu bot está vivo e configurado!

