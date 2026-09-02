import sys
from functools import partial
from typing import Any, Callable, Tuple
from PySide6.QtCore import QEvent, QObject, QPropertyAnimation, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

class _SidebarHoverFilter(QObject):
    def __init__(self, sidebar: QWidget, animation: QPropertyAnimation, target_size: int = 200, trigger_margin: int = 100, position: str = "left"):
        super().__init__(sidebar)
        self.sidebar = sidebar
        self.animation = animation
        self.target_size = target_size
        self.trigger_margin = trigger_margin
        self.position = position.lower()
        self.menu_open = False
        self.animating = False
        self.animation.finished.connect(lambda: setattr(self, "animating", False))

    def _get_current_size(self) -> int:
        """Retorna altura ou largura dinâmica conforme a posição do menu."""
        return self.sidebar.height() if self.position in ("top", "bottom") else self.sidebar.width()

    def _open_menu(self):
        if self.menu_open or self.animating:
            return
        self.animating = True
        self.menu_open = True
        self.animation.stop()
        self.animation.setStartValue(self._get_current_size())
        self.animation.setEndValue(self.target_size)
        self.animation.start()

    def _close_menu(self):
        if not self.menu_open or self.animating:
            return
        self.animating = True
        self.menu_open = False
        self.animation.stop()
        self.animation.setStartValue(self._get_current_size())
        self.animation.setEndValue(0)
        self.animation.start()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() in (
            QEvent.Type.MouseMove,
            QEvent.Type.Enter,
            QEvent.Type.HoverMove,
        ):
            window = self.sidebar.window()
            if window and window.isVisible():
                pos = window.mapFromGlobal(QCursor.pos())
                win_width = window.width()
                win_height = window.height()

                # Lógica para Posicionamento Horizontal (Top / Bottom)
                if self.position == "bottom":
                    if pos.y() >= (win_height - self.trigger_margin):
                        self._open_menu()
                    elif pos.y() < (win_height - self.target_size - 30):
                        self._close_menu()
                elif self.position == "top":
                    if pos.y() <= self.trigger_margin:
                        self._open_menu()
                    elif pos.y() > (self.target_size + 30):
                        self._close_menu()

                # Lógica para Posicionamento Vertical (Left / Right)
                elif self.position == "right":
                    if pos.x() >= (win_width - self.trigger_margin):
                        self._open_menu()
                    elif pos.x() < (win_width - self.target_size - 30):
                        self._close_menu()
                else:  # "left"
                    if pos.x() <= self.trigger_margin:
                        self._open_menu()
                    elif pos.x() > (self.target_size + 30):
                        self._close_menu()

        return super().eventFilter(obj, event)


class Pyside6_Dgp:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = kwargs.get("position", "left").lower()

    # ... (seus atributos e o add_sidebar continuam aqui) ...

    def set_window_mainwindow(
        self,
        window: QMainWindow,
        title: str = "Aplicação",
        min_size: Tuple[int, int] = (1100, 700),
        mouse_tracking: bool = True,
    ) -> None:
        """Configura os parâmetros básicos da QMainWindow existente."""
        window.setWindowTitle(title)
        window.setMinimumSize(*min_size)
        if mouse_tracking:
            window.setMouseTracking(True)

    def set_window_widget(
        self,
        window: QWidget,
        title: str = "Aplicação",
        style_title: str | None = None,
    ) -> QVBoxLayout:
        layout = QVBoxLayout(window)
        titulo = QLabel(title)
        titulo.setStyleSheet(style_title)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(titulo)
        return layout

    def add_central_mainwindow(
        self,
        window: QMainWindow,
        mouse_tracking: bool = True,
    ) -> Tuple[QWidget, QVBoxLayout]:
        """Layout principal e central de conteúdo separadamente."""
        central = QWidget(window)
        if mouse_tracking:
            central.setMouseTracking(True)

        # content_layout não deve ser pai do central, apenas um layout solto
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 0, 10, 0)

        window.setCentralWidget(central)
        return central, content_layout

    def add_central_widget(
        self,
        window: QWidget,
        mouse_tracking: bool = True,
        style_background: str = "fffff",
    ) -> QVBoxLayout:
        """Configura o layout principal de páginas/sub-telas do tipo QWidget."""
        if mouse_tracking:
            window.setMouseTracking(True)

        content_layout = QVBoxLayout(window)
        content_layout.setContentsMargins(10, 0, 10, 0)

        widget = QWidget()
        widget.setStyleSheet(f"background-color: {style_background};")

        layout_widget = QVBoxLayout(widget)
        layout_widget.setAlignment(Qt.AlignmentFlag.AlignTop)

        content_layout.addWidget(widget)


        return layout_widget

    def add_topbar(
        self,
        parent_layout: QVBoxLayout,
        margins: Tuple[int, int, int, int] = (5, 5, 5, 5),
    ) -> Tuple[QWidget, QHBoxLayout]:
        """Cabeçalho fixo no topo da aplicação e seu layout horizontal."""
        topbar = QWidget()
        layout_topbar = QHBoxLayout(topbar)
        layout_topbar.setContentsMargins(*margins)

        parent_layout.addWidget(topbar)
        return topbar, layout_topbar

    def add_sidebar(self, central: QWidget, dict_pages_info: dict[str, dict[str, Any]], content_layout: QVBoxLayout,
        style_btn: str = "", style_background: str = "", on_finished: Callable[[], None] | None = None,
        enable_hover: bool = True, target_size: int = 200, trigger_margin: int = 100
        ) -> tuple[QStackedWidget, QWidget, QPropertyAnimation, QBoxLayout]:

        if content_layout is None:
            raise ValueError("O layout 'content_layout' não pode ser None.")

        if not isinstance(dict_pages_info, dict):
            raise TypeError("O argumento 'dict_pages_info' deve ser um dicionário.")

        is_horizontal = self.position in ("top", "bottom")

        sidebar = QWidget()
        if style_background:
            sidebar.setStyleSheet(style_background)

        if is_horizontal:
            sidebar.setMinimumHeight(0)
            sidebar.setMaximumHeight(0)
            layout_sidebar = QHBoxLayout(sidebar)
            layout_sidebar.setAlignment(Qt.AlignmentFlag.AlignLeft)
            anim_property = b"maximumHeight"
        else:
            sidebar.setMinimumWidth(0)
            sidebar.setMaximumWidth(0)
            layout_sidebar = QVBoxLayout(sidebar)
            layout_sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
            anim_property = b"maximumWidth"

        # QStackedWidget instanciado uma única vez e mantido vivo pelo parent do content_layout
        parent_widget = content_layout.parentWidget()
        stacked = QStackedWidget(parent_widget) if parent_widget else QStackedWidget()
        stacked.setMouseTracking(True)
        content_layout.addWidget(stacked)

        sidebar_animation = QPropertyAnimation(sidebar, anim_property, parent=sidebar)
        sidebar_animation.setDuration(500)

        if on_finished is not None:
            if not callable(on_finished):
                raise TypeError("O parâmetro 'on_finished' deve ser um chamável (Callable) ou None.")
            sidebar_animation.finished.connect(on_finished)

        # LOOP DE MAPEAMENTO DAS PÁGINAS E BOTÕES
        for key, info in dict_pages_info.items():
            if "page" in info and isinstance(info["page"], QWidget):
                page_widget = info["page"]
            else:
                page_widget = QWidget()
                page_layout = QVBoxLayout(page_widget)
                desc_text = info.get("description", "Página sem descrição")
                page_layout.addWidget(QLabel(desc_text))
                info["page"] = page_widget

            btn_title = info.get("title", key.capitalize())
            btn = QPushButton(btn_title)
            info["btn"] = btn

            if style_btn:
                btn.setStyleSheet(style_btn)

            page_widget.setMouseTracking(True)
            stacked.addWidget(page_widget)
            layout_sidebar.addWidget(btn)

            # Conecta o clique ao slot sem perda de referência no loop
            btn.clicked.connect(partial(stacked.setCurrentWidget, page_widget))

        def toggle():
            if sidebar_animation.state() == QPropertyAnimation.State.Running:
                return
            current_val = sidebar.height() if is_horizontal else sidebar.width()
            end_val = target_size if current_val == 0 else 0
            sidebar_animation.setStartValue(current_val)
            sidebar_animation.setEndValue(end_val)
            sidebar_animation.start()

        sidebar.toggle = toggle  # type: ignore

        if enable_hover:
            app = QApplication.instance()
            if app:
                hover_filter = _SidebarHoverFilter(
                    sidebar=sidebar,
                    animation=sidebar_animation,
                    target_size=target_size,
                    trigger_margin=trigger_margin,
                    position=self.position,
                )
                app.installEventFilter(hover_filter)
                sidebar._hover_filter = hover_filter  # type: ignore


                """Cria e organiza o layout do widget central com base na posição da sidebar."""
        is_horizontal = self.position in ("top", "bottom")

        # Decide o tipo de layout principal
        if is_horizontal:
            main_layout = QVBoxLayout(central)
        else:
            main_layout = QHBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)

        # Insere a sidebar e o conteúdo na ordem correta
        if self.position in ("right", "bottom"):
            main_layout.addLayout(content_layout, stretch=1)
            main_layout.addWidget(sidebar)
        else:  # "left" ou "top"
            main_layout.addWidget(sidebar)
            main_layout.addLayout(content_layout, stretch=1)

        align_map = {
            "left": Qt.AlignmentFlag.AlignLeft,
            "right": Qt.AlignmentFlag.AlignRight,
            "top": Qt.AlignmentFlag.AlignTop,
            "bottom": Qt.AlignmentFlag.AlignBottom,
        }

        if self.position in align_map:
            main_layout.setAlignment(align_map[self.position])


        return stacked, sidebar, sidebar_animation, main_layout

    def add_table(self, df_desp):
        # Trata cópia do DataFrame sem a coluna 'id'
        df = df_desp.drop(columns=["id"], errors="ignore")

        num_rows, num_cols = df.shape
        table = QTableWidget(num_rows, num_cols)
        table.setHorizontalHeaderLabels([str(col) for col in df.columns])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #b0c4de;  /* Azul claro suave (Light Steel Blue) */
                color: #000000;             /* Cor do texto em preto */
            }
        """)
        col_types = []
        for col in df.columns:
            col_nome = str(col).lower()
            if "valor" in col_nome:
                col_types.append("valor")
            elif "quantidade" in col_nome or "qtd" in col_nome:
                col_types.append("qtd")
            elif "data" in col_nome:
                col_types.append("data")
            else:
                col_types.append("outro")

        # Preenchimento da tabela
        for j in range(num_cols):
            tipo_coluna = col_types[j]

            for i in range(num_rows):
                valor = df.iloc[i, j]

                if pd.isna(valor):
                    continue  # Pula células vazias para economizar processamento

                is_numeric = False

                if tipo_coluna == "valor":
                    try:
                        if isinstance(valor, bool):
                            raise ValueError
                        valor_num = float(valor)
                        formatado = (
                            f"{valor_num:,.2f}"
                            .replace(",", "X")
                            .replace(".", ",")
                            .replace("X", ".")
                        )
                        txt = f"R$ {formatado}"
                        is_numeric = True
                    except (ValueError, TypeError):
                        txt = str(valor)

                elif tipo_coluna == "qtd":
                    try:
                        if isinstance(valor, bool):
                            raise ValueError
                        qtd_int = int(float(valor))
                        txt = f"{qtd_int:,}".replace(",", ".")
                        is_numeric = True
                    except (ValueError, TypeError):
                        txt = str(valor)

                elif tipo_coluna == "data":
                    try:
                        dt = pd.to_datetime(valor)
                        txt = dt.strftime("%d/%m/%Y")
                    except Exception:
                        txt = str(valor)

                else:
                    txt = str(valor)

                item = QTableWidgetItem(txt)

                if is_numeric:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )

                table.setItem(i, j, item)

        # Ajustes finais das colunas
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        return table


def styles_() -> dict[str, str]:
    color_primario = "#bcd4e6"
    color_primario_hover = "#7ba4d0"
    color_primario_pressed = "#5c8bc3"
    color_primario_txt = "#1a3a5a"
    color_primario_hover_txt = "#ffffff"
    color_primario_pressed_txt = "#ffffff"

    size_padding = "10px"
    size_border = "12px"
    size_font_normal = "18px"

    # Seletor explícito evita aplicar a cor aos widgets filhos
    style_background = f"QWidget {{ background-color: {color_primario}; }}"

    style_btn = f"""
        QPushButton {{
            background-color: {color_primario};
            color: {color_primario_txt};
            padding: {size_padding};
            border: none;
            text-align: left;
            border-radius: {size_border};
            font-size: {size_font_normal};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {color_primario_hover};
            color: {color_primario_hover_txt};
        }}
        QPushButton:pressed {{
            background-color: {color_primario_pressed};
            color: {color_primario_pressed_txt};
        }}
    """

    return {
        "style_background": style_background,
        "style_btn": style_btn,
    }


if __name__ == "__main__":
    app = QApplication(sys.argv)

    styles = styles_()
    pyside6_dgp = Pyside6_Dgp()
    pyside6_dgp.position = "top"  # Alinhado à esquerda para destacar o fluxo principal

    window = QMainWindow()
    pyside6_dgp.set_window_mainwindow(
        window,
        title="Pyside6_Dgp - Demonstração com Tabela de Dados",
        min_size=(1100, 700),
    )

    central_widget, content_layout = pyside6_dgp.add_central_mainwindow(window)

    # 1. Criação do DataFrame fictício para testes
    df_exemplo = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "data": [
                "2026-01-15",
                "2026-02-10",
                "2026-02-28",
                "2026-03-05",
                "2026-03-12",
            ],
            "descricao": [
                "Licença de Software",
                "Monitor 4K",
                "Teclado Mecânico",
                "Cadeira Ergonômica",
                "Serviço de Nuvem",
            ],
            "quantidade": [2, 1, 5, 2, 12],
            "valor_unitario": [150.50, 2499.90, 350.00, 1200.00, 89.90],
            "valor_total": [301.00, 2499.90, 1750.00, 2400.00, 1078.80],
        }
    )

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
            "description": "<h1>Página Inicial</h1><p>Passe o mouse na lateral ou use o botão para abrir o menu.</p>",
        },
        "tabela": {
            "title": "Tabela de Dados",
            "page": pagina_tabela,  # Passa o QWidget diretamente
        },
        "settings": {
            "title": "Configurações",
            "description": "<h1>Página de Configurações</h1>",
        },
    }

    stacked, sidebar, animation, main_layout = pyside6_dgp.add_sidebar(
        central=central_widget,
        dict_pages_info=dict_pages_info,
        content_layout=content_layout,
        style_btn=styles["style_btn"],
        style_background=styles["style_background"],
        target_size=200,
    )

    # Botão de topo para alternar a sidebar manualmente
    btn_toggle = QPushButton("Alternar Sidebar")
    content_layout.insertWidget(0, btn_toggle)
    btn_toggle.clicked.connect(sidebar.toggle)  # type: ignore

    window.show()
    sys.exit(app.exec())
