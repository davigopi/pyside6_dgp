TUTORIAL: CRIAR E CENTRALIZAR A BIBLIOTECA E COMANDO CLI (pyside6_dgp)
===============================================================================
## 📋 Sumário
1. [ESTRUTURA DA PASTA DO PROJETO LOCAL](#1-ESTRUTURA-DA-PASTA-DO-PROJETO-LOCAL)
2. [PUBLICAR NO GITHUB](#2-PUBLICAR-NO-GITHUB)
3. [INSTALAR E ATUALIZAÇÕES](#3-INSTALAR-E-ATUALIZAÇÕES)
4. [COMO USAR NOS SEUS PROJETOS](#4-COMO-USAR-NOS-SEUS-PROJETOS)
5. [EXEMPLOS DE CÓDIGO DE COMO UTILIZAR](#5-EXEMPLOS-DE-CÓDIGO-DE-COMO-UTILIZAR)

---------------------------------------------------------
## 1. ESTRUTURA DA PASTA DO PROJETO LOCAL
---------------------------------------------------------
Crie uma pasta com o nome pyside6_dgp e coloque os dois arquivos dentro dela:
```
pyside6_dgp/
    ├── pyside6_dgp.py
    ├── pyproject.toml
    ├── README.md
    ├── LICENSE (Opcional)
    ├── .gitignore
    ├── .editorconfig
    ├── requirements-dev.txt
    └── CHANGELOG.md
```
---------------------------------------------------------
## 2. PUBLICAR NO GITHUB
---------------------------------------------------------
Repositório público ou privado no GitHub com o nome pyside6_dgp.

URL do repositório: https://github.com/davigopi/pyside6_dgp

---------------------------------------------------------
## 3. INSTALAR E ATUALIZAÇÕES
---------------------------------------------------------

Abra o terminal do seu computador, ative o ambiente virtual e, no diretório do repositório pyside6_dgp, execute

### A) INSTALAR A FERRAMENTA NO COMPUTADOR
```bash
pip install git+https://github.com/davigopi/pyside6_dgp.git
```

### B) ATUALIZAR A FERRAMENTA NO FUTURO

Alterado a version em pyproject.toml:
```bash
pip install --upgrade git+https://github.com/davigopi/pyside6_dgp.git
```
Força a atualização:
```bash
pip install --force-reinstall git+https://github.com/davigopi/pyside6_dgp.git
```
```bash
pip install --upgrade --no-cache-dir git+https://github.com/davigopi/pyside6_dgp.git
```

### C) INSTALAR REQUIREMENTS

```bash
pip install -r venv\Lib\site-packages\pyside6_dgp\requirements.txt
```
---------------------------------------------------------
## 4. COMO USAR NOS SEUS PROJETOS
---------------------------------------------------------
- Via importação dentro de scripts Python futuros:
```python
from pyside6_dgp import Pyside6_Dgp
```
```python
import pyside6_dgp
```
- Via terminal (em qualquer pasta de projeto React Native, Python, etc.):
  Basta abrir o terminal na pasta desejada e digitar:
```bash
python -m pyside6_dgp
```
## 5. EXEMPLOS DE CÓDIGO DE COMO UTILIZAR

### A) Exemplo Básico (Sidebar Lateral e Navegação Simples)
```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from pyside6_dgp import Pyside6_Dgp, styles_

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Obtém estilos padrão e inicializa com posição à esquerda
    styles = styles_()
    pyside6_dgp = Pyside6_Dgp(position="left")

    window = QMainWindow()
    pyside6_dgp.set_window(
        window,
        title="Exemplo Básico - PySide6 DGP",
        min_size=(800, 600)
    )

    central_widget, content_layout = pyside6_dgp.add_central_widget(window)

    pages_info = {
        "home": {
            "title": "Início",
            "description": "<h2>Bem-vindo à Aplicação</h2><p>Conteúdo da página inicial.</p>"
        },
        "perfil": {
            "title": "Perfil",
            "description": "<h2>Configurações de Perfil</h2><p>Informações e preferências do usuário.</p>"
        }
    }

    stacked, sidebar, animation, main_layout = pyside6_dgp.add_sidebar(
        central=central_widget,
        dict_pages_info=pages_info,
        content_layout=content_layout,
        style_btn=styles["style_btn"],
        style_background=styles["style_background"],
        target_size=200
    )

    window.show()
    sys.exit(app.exec())
```

### B) Exemplo Avançado (Menu Superior, Tabela Pandas e Customização de Páginas)
```python
import sys
from typing import Any
import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from pyside6_dgp import Pyside6_Dgp, styles_

if __name__ == "__main__":
    app = QApplication(sys.argv)

    styles = styles_()
    pyside6_dgp = Pyside6_Dgp(position="top")

    window = QMainWindow()
    pyside6_dgp.set_window(
        window,
        title="Pyside6_Dgp - Demonstração com Tabela de Dados",
        min_size=(1100, 700)
    )

    central_widget, content_layout = pyside6_dgp.add_central_widget(window)

    # 1. Criação do DataFrame fictício para testes
    df_exemplo = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "data": [
            "2026-01-15",
            "2026-02-10",
            "2026-02-28",
            "2026-03-05",
            "2026-03-12"
        ],
        "descricao": [
            "Licença de Software",
            "Monitor 4K",
            "Teclado Mecânico",
            "Cadeira Ergonômica",
            "Serviço de Nuvem"
        ],
        "quantidade": [2, 1, 5, 2, 12],
        "valor_unitario": [150.50, 2499.90, 350.00, 1200.00, 89.90],
        "valor_total": [301.00, 2499.90, 1750.00, 2400.00, 1078.80]
    })

    # 2. Gerar a tabela PySide6 formatada usando o add_table
    tabela_widget = pyside6_dgp.add_table(df_exemplo)

    # 3. Criar o container/página para a tabela
    pagina_tabela = QWidget()
    layout_tabela = QVBoxLayout(pagina_tabela)

    titulo_tabela = QLabel("<h1>Relatório de Despesas (DataFrame)</h1>")
    layout_tabela.addWidget(titulo_tabela)
    layout_tabela.addWidget(tabela_widget)

    # 4. Estrutura de páginas passando a página customizada na chave "page"
    dict_pages_info: dict[str, dict[str, Any]] = {
        "home": {
            "title": "Home",
            "description": "<h1>Página Inicial</h1><p>Passe o mouse na área superior ou use o botão para abrir o menu.</p>"
        },
        "tabela": {
            "title": "Tabela de Dados",
            "page": pagina_tabela
        },
        "settings": {
            "title": "Configurações",
            "description": "<h1>Página de Configurações</h1>"
        }
    }

    stacked, sidebar, animation, main_layout = pyside6_dgp.add_sidebar(
        central=central_widget,
        dict_pages_info=dict_pages_info,
        content_layout=content_layout,
        style_btn=styles["style_btn"],
        style_background=styles["style_background"],
        target_size=200
    )

    # Botão de topo para alternar a sidebar manualmente
    btn_toggle = QPushButton("Alternar Sidebar")
    content_layout.insertWidget(0, btn_toggle)
    btn_toggle.clicked.connect(sidebar.toggle)

    window.show()
    sys.exit(app.exec())
```

