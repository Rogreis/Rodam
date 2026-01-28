# 📖 Rodam: Leitor Dinâmico do Livro de Urântia

O **Rodam** é uma aplicação moderna desenvolvida para proporcionar uma experiência de leitura eficiente, bilíngue e enriquecida do *Livro de Urântia*, focada na tradução dinâmica para o **Português do Brasil**.

---

## 🚀 Funcionalidades Principais

### 📄 Leitura Bilíngue e Sincronizada
- Apresenta o texto lado a lado: **Original em Inglês** e **Português do Brasil**.
- Navegação fluida por documentos, seções e parágrafos.
- A tradução é "dinâmica", podendo ser atualizada continuamente pela comunidade quando conectada à internet.

### 🔍 Busca Poderosa
O Rodam oferece dois tipos de busca para atender a todas as suas necessidades de estudo:

1.  **Busca Literal (Padrão)**: 
    - Encontra palavras exatas ou frases no texto.
    - Extremamente rápida e funciona 100% offline.
    - Ideal para quando você sabe exatamente o termo que procura.

2.  **🧠 Busca Semântica (Avançada com IA)**:
    - Entende o *sentido* da sua pergunta, não apenas as palavras.
    - *Exemplo*: Se buscar "como os anjos viajam", o sistema encontrará parágrafos sobre "transporte seráfico" mesmo que a palavra "viagem" não apareça.
    - **⚠️ Atenção:** Este recurso é **opcional**. Para utilizá-lo, o aplicativo precisará baixar um modelo de Inteligência Artificial (aprox. 100MB) para o seu computador na primeira utilização. 
    - Todo o processamento da IA é feito **localmente no seu dispositivo**, garantindo sua privacidade e funcionamento offline após o download inicial.


### 🎨 Personalização e Conforto
- **Modo Escuro (Dark Mode):** Para leitura confortável em ambientes com pouca luz.
- **Destaque de Parágrafos:** Realce visual do parágrafo ativo para facilitar o foco.
- **Funciona Offline:** Após a instalação e sincronização inicial, a maior parte das funcionalidades (incluindo busca e leitura) não requer internet.

---

## 🔒 Privacidade e Filosofia

Este projeto acredita na descentralização e no acesso livre ao conhecimento:
- O software é de **código aberto** e livre para distribuição.
- Não coletamos dados pessoais.
- A tradução em Português é um projeto vivo, aberto a melhorias constantes pela comunidade.

**Aviso Legal:**  
Esta tradução para o Português destina-se exclusivamente ao uso eletrônico (online ou offline) e não se destina a ser impressa ou comercializada em formato físico. O software é fornecido "no estado em que se encontra", sem garantias.

---

## 📥 Instalação

Disponível para **Windows**, **Linux** e **macOS**. Baixe a versão mais recente na aba de [Releases](https://github.com/Rogreis/Rodam/releases) deste repositório.

## 📥 Como Baixar

As versões compiladas (executáveis) para Windows, Linux e macOS estão disponíveis na aba de **Releases** deste repositório.

1. Vá até a página de [**Releases**](../../releases).
2. Encontre a versão mais recente (marcada como *Latest*).
3. Na seção **Assets**, baixe o arquivo correspondente ao seu sistema operacional:
    * **Windows:** `.exe` ou `.zip`
    * **Linux:** Arquivo binário (geralmente sem extensão) ou `.tar.gz`
    * **macOS:** `.app`, `.dmg` ou `.zip`

---

## 🚀 Guia de Instalação e Execução

Como esta aplicação não possui um instalador assinado digitalmente (certificado pago), os sistemas operacionais podem emitir alertas de segurança. Siga os passos abaixo para o seu sistema:

### 🪟 Windows

1. Baixe o executável (`.exe`).
2. Clique duas vezes para abrir.
3. **Tela "O Windows protegeu o seu PC" (SmartScreen):**
   * Se aparecer uma janela azul dizendo que o Windows protegeu o PC, clique em **"Mais informações"**.
   * Em seguida, clique no botão **"Executar mesmo assim"**.
   * *Isso acontece porque o aplicativo é novo e ainda não é conhecido pela Microsoft.*

### 🐧 Linux

Por segurança, o Linux não permite executar arquivos baixados da internet imediatamente. Você precisa dar permissão.

1. **Extraia** o arquivo (se estiver compactado).
2. **Opção A (Interface Gráfica):**
   * Clique com o botão direito no arquivo > **Propriedades**.
   * Vá na aba **Permissões** e marque **"Permitir execução do arquivo como um programa"**.
3. **Opção B (Terminal - Recomendado):**
   Abra o terminal na pasta onde baixou o arquivo e rode:
   ```bash
   chmod +x nome_do_arquivo
   ./nome_do_arquivo


---

## 🚀 Guia de Instalação e Execução

Como esta aplicação não possui um instalador assinado digitalmente (certificado pago), os sistemas operacionais podem emitir alertas de segurança. Siga os passos abaixo para o seu sistema:

### 🪟 Windows

1. Baixe o executável (`.exe`).
2. Clique duas vezes para abrir.
3. **Tela "O Windows protegeu o seu PC" (SmartScreen):**
   * Se aparecer uma janela azul dizendo que o Windows protegeu o PC, clique em **"Mais informações"**.
   * Em seguida, clique no botão **"Executar mesmo assim"**.
   * *Isso acontece porque o aplicativo é novo e ainda não é conhecido pela Microsoft.*

### 🐧 Linux

Por segurança, o Linux não permite executar arquivos baixados da internet imediatamente. Você precisa dar permissão.

1. **Extraia** o arquivo (se estiver compactado).
2. **Opção A (Interface Gráfica):**
   * Clique com o botão direito no arquivo > **Propriedades**.
   * Vá na aba **Permissões** e marque **"Permitir execução do arquivo como um programa"**.
3. **Opção B (Terminal - Recomendado):**
   Abra o terminal na pasta onde baixou o arquivo e rode:
   ```bash
   chmod +x nome_do_arquivo
   ./nome_do_arquivo


### 🍎 macOS

O macOS possui o **Gatekeeper**, que bloqueia aplicativos de desenvolvedores não identificados pela Apple.

**Passo 1: Abrir pela primeira vez**

1. Não clique duas vezes. Em vez disso, clique com o **Botão Direito** (ou `Control` + Clique) no ícone do App.
2. Selecione **Abrir** no menu.
3. Uma janela aparecerá perguntando se tem certeza. Clique em **Abrir** novamente.
* *O sistema lembrará dessa escolha e nas próximas vezes você poderá abrir com dois cliques normais.*



**Passo 2: Erro "Arquivo danificado" (Corrompido)**
Se o Mac disser que *"O arquivo está danificado e deve ser movido para o lixo"*, não se preocupe, o arquivo está intacto. É apenas uma medida de quarentena do sistema.

1. Abra o Terminal.
2. Digite o comando abaixo (substitua pelo caminho real do seu app):
```bash
xattr -cr /Caminho/Para/SeuApp.app
```


*Dica: Digite `xattr -cr` (com um espaço no final) e arraste o ícone do App para dentro da janela do terminal para preencher o caminho automaticamente.*

---

## 🛠️ Rodando via código fonte (Para Desenvolvedores)

Se você preferir rodar a aplicação diretamente pelo Python:

```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)

# Entre na pasta
cd seu-repositorio

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python main.py

```

---


## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

## 🐙 Como instalar o Git

Para clonar o repositório e colaborar, você precisará do Git instalado.

### 🪟 Windows
1. Baixe o instalador oficial em [git-scm.com/download/win](https://git-scm.com/download/win).
2. Execute o instalador e siga as instruções (assumir as opções padrão geralmente é seguro).
3. Após instalar, abra o **Prompt de Comando** ou **PowerShell** e digite `git --version` para confirmar.

### 🐧 Linux (Ubuntu/Debian)
No terminal, execute:
```bash
sudo apt update
sudo apt install git
```
Para outras distribuições, consulte o gerenciador de pacotes padrão (yum, dnf, pacman, etc).

### 🍎 macOS
A maneira mais fácil é instalar via **Homebrew** ou através das ferramentas de linha de comando do Xcode.

**Opção 1: Via instalador oficial**
Baixe em [git-scm.com/download/mac](https://git-scm.com/download/mac).

**Opção 2: Via Terminal (se já tiver Homebrew)**
```bash
brew install git
```

**Opção 3: Ferramentas Apple**
Ao tentar rodar `git` no terminal pela primeira vez, o macOS pode oferecer para instalar as ferramentas de desenvolvedor. Aceite e aguarde a instalação.
