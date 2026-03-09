import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import base64  # Para codificar imagens para a API da OpenAI

import os

def load_icon(path, size=(80, 80)):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)

    img = Image.open(full_path)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)

# Certifique-se de ter a chave da API da OpenAI configurada como variável de ambiente
# ou substitua 'os.getenv("OPENAI_API_KEY")' pela sua chave diretamente (NÃO RECOMENDADO PARA PRODUÇÃO)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Configure sua chave como variável de ambiente ou insira aqui

# Importar a biblioteca OpenAI (pip install openai)
try:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    messagebox.showerror("Erro",
                         "A biblioteca 'openai' não está instalada. Por favor, instale com 'pip install openai'.")
    client = None
except Exception as e:
    messagebox.showerror("Erro na OpenAI",
                         f"Não foi possível inicializar a API da OpenAI: {e}\nVerifique sua OPENAI_API_KEY.")
    client = None

"""
Classificador de Animais (Mamífero, Ave, Peixe, Réptil) com IA e GUI

Objetivo didático:
- Coletar respostas (Sim/Não) sobre características biológicas do animal.
- Aplicar regras de decisão para classificar o animal, incluindo casos especiais (ornitorrinco, baleias).
- Exibir resultado + resumo das respostas, deixando o algoritmo transparente.
- Adicionar opção de classificação por imagem usando IA (OpenAI GPT-4o).
"""


# =========================
# 1) MODELO DE DADOS
# =========================
@dataclass(frozen=True)
class Question:
    """
    Estrutura IMUTÁVEL (frozen=True) para organizar as perguntas do quiz.

    Campos:
    - text: pergunta exibida ao usuário
    - key: chave usada para salvar a resposta no dicionário `answers`
    - image: caminho da imagem ilustrativa
    """
    text: str
    key: str
    image: str


# =========================
# 2) MOTOR (LÓGICA)
# =========================
class AnimalClassifierEngine:
    """
    Motor de classificação (lógica do algoritmo).
    """

    RESULT_UNKNOWN = "Não foi possível classificar."
    RESULT_MAMMAL = "MAMÍFERO 🐾"
    RESULT_BIRD = "AVE 🦅"
    RESULT_FISH = "PEIXE 🐟"
    RESULT_REPTILE = "RÉPTIL 🐍"

    def classify(self, answers: Dict[str, str]) -> str:
        """
        Recebe um dicionário com respostas 'sim'/'nao' e aplica regras.

        Regras usadas (didáticas e mais robustas):
        - Mamífero: tem pelos + (amamenta OU respira por pulmões)
        - Ave: tem penas + bota ovos + tem bico
        - Peixe: vive na água + respira por brânquias + tem nadadeiras + tem escamas
        - Réptil: tem escamas + bota ovos em terra + respira por pulmões

        A ordem das verificações é importante para a prioridade.
        """
        ans = answers
        result_text = self.RESULT_UNKNOWN

        # Prioridade 1: Mamíferos (incluindo aquáticos)
        if ans.get("tem_pelos") == "sim":
            if ans.get("amamenta") == "sim" or ans.get("respira_pulmoes") == "sim":
                result_text = self.RESULT_MAMMAL

        # Caso especial: mamíferos aquáticos (golfinho, baleia)
        elif ans.get("eh_aquatico") == "sim":
            if ans.get("respira_branquias") == "nao" and ans.get("respira_pulmoes") == "sim":
                result_text = self.RESULT_MAMMAL

        # Prioridade 2: Aves
        # Penas + ovos + bico formam um conjunto bem representativo de aves.
        elif ans.get("tem_penas") == "sim":
            if ans.get("bota_ovos") == "sim" and ans.get("tem_bico") == "sim":
                result_text = self.RESULT_BIRD

        # Prioridade 3: Peixes
        # Ambiente aquático + brânquias + nadadeiras + escamas são um conjunto típico de peixes.
        elif ans.get("eh_aquatico") == "sim" and ans.get("respira_branquias") == "sim":
            if ans.get("tem_nadadeiras") == "sim" and ans.get("tem_escamas") == "sim":
                result_text = self.RESULT_FISH

        # Prioridade 4: Répteis (se não for nenhum dos anteriores)
        # Escamas + ovos em terra + pulmões são características de répteis.
        elif ans.get("tem_escamas") == "sim" and ans.get("bota_ovos_terra") == "sim" and ans.get(
                "respira_pulmoes") == "sim":
            result_text = self.RESULT_REPTILE

        return result_text


# =========================
# 3) GUI (INTERFACE) - TELAS
# =========================

class StartScreen(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        # carregar ícones do menu
        self.icon_app = load_icon("imagens/menu/icon_app.png", (90,90))
        self.icon_quiz = load_icon("imagens/menu/icon_quiz.png", (50,50))
        self.icon_ai = load_icon("imagens/menu/icon_ai.png", (50,50))
        self.pack(fill="both", expand=True)

        # Container central
        self.container = ctk.CTkFrame(self, corner_radius=22, fg_color=("#f8f9fa", "#2b2b2b"))
        self.container.pack(padx=40, pady=40, fill="both", expand=True)

        self.label_icon = ctk.CTkLabel(
            self.container,
            text="",
            image=self.icon_app
        )
        self.label_icon.pack(pady=(35, 10))

        self.label_title = ctk.CTkLabel(
            self.container,
            text="Classificador de Animais",
            font=ctk.CTkFont(size=34, weight="bold"),
        )
        self.label_title.pack(pady=(0, 10))

        self.label_subtitle = ctk.CTkLabel(
            self.container,
            text="Escolha como deseja identificar o animal",
            font=ctk.CTkFont(size=18),
            text_color=("gray40", "gray70")
        )
        self.label_subtitle.pack(pady=(0, 30))

        # Card Quiz
        self.card_quiz = ctk.CTkFrame(self.container, corner_radius=18, fg_color=("#ffffff", "#333333"))
        self.card_quiz.pack(padx=30, pady=20, fill="x")

        self.quiz_icon_label = ctk.CTkLabel(
            self.card_quiz,
            text="",
            image=self.icon_quiz
        )
        self.quiz_icon_label.pack(pady=(15, 5))

        self.label_quiz_title = ctk.CTkLabel(
            self.card_quiz,
            text="Quiz Biológico",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_quiz_title.pack(pady=(5, 8))

        self.label_quiz_desc = ctk.CTkLabel(
            self.card_quiz,
            text="Responda perguntas sobre características do animal e descubra sua classe biológica.",
            font=ctk.CTkFont(size=15),
            wraplength=520,
            text_color=("gray40", "gray70")
        )
        self.label_quiz_desc.pack(pady=(0, 15), padx=20)

        self.btn_quiz = ctk.CTkButton(
            self.card_quiz,
            text="Iniciar Quiz",
            compound="left",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=220,
            height=50,
            corner_radius=14,
            fg_color="#2563eb",
            hover_color="#1e40af",
            command=self.app.show_quiz_screen
        )
        self.btn_quiz.pack(pady=(0, 20))

        # Card IA
        self.card_ia = ctk.CTkFrame(self.container, corner_radius=18, fg_color=("#ffffff", "#333333"))
        self.card_ia.pack(padx=30, pady=10, fill="x")

        self.ai_icon_label = ctk.CTkLabel(
            self.card_ia,
            text="",
            image=self.icon_ai
        )
        self.ai_icon_label.pack(pady=(15, 5))

        self.label_ia_title = ctk.CTkLabel(
            self.card_ia,
            text="Classificação por Foto com IA",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_ia_title.pack(pady=(5, 8))

        self.label_ia_desc = ctk.CTkLabel(
            self.card_ia,
            text="Selecione uma imagem do animal para que a inteligência artificial analise e classifique.",
            font=ctk.CTkFont(size=15),
            wraplength=520,
            text_color=("gray40", "gray70")
        )
        self.label_ia_desc.pack(pady=(0, 15), padx=20)

        self.btn_ia = ctk.CTkButton(
            self.card_ia,
            text="Iniciar Classificação por Imagem",
            compound="left",
            command=self.app.show_ia_screen,
            font=ctk.CTkFont(size=18, weight="bold"),
            width=220,
            height=50,
            corner_radius=14,
            fg_color="#16a34a",
            hover_color="#166534",
        )
        self.btn_ia.pack(pady=(0, 20))

class QuizScreen(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.engine = AnimalClassifierEngine()

        # Estado do aplicativo
        self.current_question_key: Optional[str] = None
        self.answers: Dict[str, str] = {}
        self.question_history: List[str] = []
        self.current_image = None

        # Dados: perguntas e imagens
        self.all_questions: Dict[str, Question] = {
            "tem_pelos": Question(
                "O animal possui pelos ou cabelos?",
                "tem_pelos",
                "imagens/quiz/pelos.png"
            ),

            "amamenta": Question(
                "O animal amamenta seus filhotes com leite?",
                "amamenta",
                "imagens/quiz/amamenta.png"
            ),

            "respira_pulmoes": Question(
                "O animal respira por pulmões?",
                "respira_pulmoes",
                "imagens/quiz/pulmoes.png"
            ),

            "tem_penas": Question(
                "O animal possui penas?",
                "tem_penas",
                "imagens/quiz/pena.png"
            ),

            "bota_ovos": Question(
                "O animal bota ovos?",
                "bota_ovos",
                "imagens/quiz/ovos.png"
            ),

            "tem_bico": Question(
                "O animal possui bico (sem dentes)?",
                "tem_bico",
                "imagens/quiz/bico.png"
            ),

            "eh_aquatico": Question(
                "O animal vive predominantemente em ambiente aquático?",
                "eh_aquatico",
                "imagens/quiz/aquatico.png"
            ),

            "respira_branquias": Question(
                "O animal respira por brânquias?",
                "respira_branquias",
                "imagens/quiz/branquias.png"
            ),

            "tem_escamas": Question(
                "O animal possui escamas?",
                "tem_escamas",
                "imagens/quiz/escamas.jpeg"
            ),

            "bota_ovos_terra": Question(
                "O animal bota ovos em terra?",
                "bota_ovos_terra",
                "imagens/quiz/ovos_terra.jpg"
            ),

            "tem_nadadeiras": Question(
                "O animal possui nadadeiras?",
                "tem_nadadeiras",
                "imagens/quiz/nadadeiras.jpg"
            ),
        }
        # Imagens de resultado
        self.result_images: Dict[str, str] = {
            AnimalClassifierEngine.RESULT_MAMMAL: "imagens/quiz/resultado_mamifero.jpg",
            AnimalClassifierEngine.RESULT_BIRD: "imagens/quiz/resultado_ave.jpg",
            AnimalClassifierEngine.RESULT_FISH: "imagens/quiz/resultado_peixe.jpg",
            AnimalClassifierEngine.RESULT_REPTILE: "imagens/quiz/resultado_reptil.jpg",
            AnimalClassifierEngine.RESULT_UNKNOWN: "imagens/quiz/resultado_desconhecido.png",
        }

        self.total_questions = len(self.all_questions)
        self._build_ui()

    def _build_ui(self) -> None:
        self.label_progress_text = ctk.CTkLabel(
            self,
            text="Pergunta 1 de 1",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("gray40", "gray70")
        )
        self.label_progress_text.pack(pady=(5, 0))

        self.question_card_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("white", "#333333"))
        self.question_card_frame.pack(pady=20, padx=30, fill="both", expand=True)

        self.image_display = ctk.CTkLabel(self.question_card_frame, text="", width=450, height=250)
        self.image_display.pack(pady=15)

        self.label_question = ctk.CTkLabel(
            self.question_card_frame,
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
            wraplength=500,
            justify="center",
        )

        self.label_question.pack(pady=15)

        # botões
        self.frame_buttons = ctk.CTkFrame(self.question_card_frame, fg_color="transparent")
        self.frame_buttons.pack(pady=10)

        self.btn_voltar = ctk.CTkButton(
            self.frame_buttons,
            text="Voltar",
            command=self.go_back,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=150,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.btn_voltar.pack(side=ctk.LEFT, padx=10)

        self.btn_sim = ctk.CTkButton(
            self.frame_buttons,
            text="Sim",
            command=lambda: self.process_answer("sim"),
            fg_color="#28a745",
            hover_color="#218838",
            width=150,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.btn_sim.pack(side=ctk.LEFT, padx=10)

        self.btn_nao = ctk.CTkButton(
            self.frame_buttons,
            text="Não",
            command=lambda: self.process_answer("nao"),
            fg_color="#dc3545",
            hover_color="#c82333",
            width=150,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.btn_nao.pack(side=ctk.LEFT, padx=10)

        self.label_result = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#007bff",
            wraplength=560,
            justify="left"
        )
        self.label_result.pack(pady=20)

        self.btn_restart = ctk.CTkButton(
            self,
            text="Reiniciar Classificação",
            command=self.start_quiz,
            fg_color="gray",
            width=150,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),

        )

        self.btn_back_to_menu = ctk.CTkButton(
            self,
            text="Voltar ao Menu Principal",
            command=self.app.show_start_screen,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=150,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.btn_back_to_menu.pack(pady=10)

    def _reset_image_label(self) -> None:
        self.image_display.destroy()
        self.image_display = ctk.CTkLabel(self.question_card_frame, text="", width=450, height=250)
        self.image_display.pack(pady=15, before=self.label_question)

    def _load_image(self, path: str) -> Optional[ctk.CTkImage]:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, path)

        if not os.path.exists(full_path):
            print(f"Imagem não encontrada: {full_path}")
            return None

        try:
            img = Image.open(full_path)
            img = img.resize((450, 250), Image.LANCZOS)

            return ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(450, 250)
            )
        except Exception as e:
            print(f"Erro ao carregar imagem {full_path}: {e}")
            return None

    def _set_question_view(self, question: Question) -> None:
        self.label_question.configure(text=question.text)

        # recria o label para evitar erro de pyimage inexistente
        self._reset_image_label()
        self.current_image = None

        img = self._load_image(question.image)
        if img is not None:
            self.current_image = img
            self.image_display.configure(image=self.current_image, text="")
        else:
            self.image_display.configure(image=None, text="[Imagem não encontrada]")

    def _update_progress(self) -> None:
        respondidas = len(self.question_history)

        if self.current_question_key is None:
            atual = self.total_questions
        else:
            atual = min(respondidas + 1, self.total_questions)

        self.label_progress_text.configure(text=f"Pergunta {atual} de {self.total_questions}")
        self.app.progress_bar.set(respondidas / self.total_questions if self.total_questions > 0 else 0)

    def _update_back_button(self) -> None:
        self.btn_voltar.configure(state="disabled" if not self.question_history else "normal")

    def start_quiz(self) -> None:
        self.answers = {}
        self.question_history = []
        self.label_result.configure(text="")
        self.btn_restart.pack_forget()
        self.app.progress_bar.set(0)

        self.current_question_key = "tem_pelos"
        self.current_image = None

        self._reset_image_label()
        self.image_display.configure(image=None, text="")
        self.label_progress_text.configure(text=f"Pergunta 1 de {self.total_questions}")

        self.show_current_question()

    def show_current_question(self) -> None:
        if self.current_question_key is None:
            self.finish_and_show_result()
            return

        question = self.all_questions[self.current_question_key]
        self.frame_buttons.pack(pady=10)
        self._update_back_button()
        self._set_question_view(question)
        self._update_progress()

    def process_answer(self, answer: str) -> None:
        if self.current_question_key:
            self.answers[self.current_question_key] = answer
            self.question_history.append(self.current_question_key)

        self.current_question_key = self._get_next_question_key()
        self.show_current_question()

    def go_back(self) -> None:
        if self.question_history:
            last_question_key = self.question_history.pop()

            if last_question_key in self.answers:
                del self.answers[last_question_key]

            # recalcula a pergunta atual corretamente
            self.current_question_key = "tem_pelos"
            respostas_temp = dict(self.answers)
            self.answers = {}

            for key in self.question_history:
                if key in respostas_temp:
                    self.answers[key] = respostas_temp[key]

            self.current_question_key = self._get_next_question_key()
            self.show_current_question()

    def _get_next_question_key(self) -> Optional[str]:
        ans = self.answers

        if ans.get("tem_pelos") is None:
            return "tem_pelos"

        if ans.get("tem_pelos") == "sim":
            if ans.get("amamenta") is None:
                return "amamenta"
            if ans.get("amamenta") == "nao":
                if ans.get("respira_pulmoes") is None:
                    return "respira_pulmoes"
                if ans.get("respira_pulmoes") == "sim":
                    return None
            elif ans.get("amamenta") == "sim":
                return None

        elif ans.get("tem_pelos") == "nao":
            if ans.get("tem_penas") is None:
                return "tem_penas"

            if ans.get("tem_penas") == "sim":
                if ans.get("bota_ovos") is None:
                    return "bota_ovos"
                if ans.get("bota_ovos") == "sim":
                    if ans.get("tem_bico") is None:
                        return "tem_bico"
                    if ans.get("tem_bico") == "sim":
                        return None

            elif ans.get("tem_penas") == "nao":
                if ans.get("eh_aquatico") is None:
                    return "eh_aquatico"

                if ans.get("eh_aquatico") == "sim":
                    if ans.get("respira_branquias") is None:
                        return "respira_branquias"
                    if ans.get("respira_branquias") == "sim":
                        if ans.get("tem_nadadeiras") is None:
                            return "tem_nadadeiras"
                        if ans.get("tem_nadadeiras") == "sim":
                            if ans.get("tem_escamas") is None:
                                return "tem_escamas"
                            if ans.get("tem_escamas") == "sim":
                                return None
                    elif ans.get("respira_branquias") == "nao":
                        if ans.get("respira_pulmoes") is None:
                            return "respira_pulmoes"
                        if ans.get("respira_pulmoes") == "sim":
                            if ans.get("tem_escamas") is None:
                                return "tem_escamas"
                            if ans.get("tem_escamas") == "sim":
                                if ans.get("bota_ovos_terra") is None:
                                    return "bota_ovos_terra"
                                if ans.get("bota_ovos_terra") == "sim":
                                    return None

                elif ans.get("eh_aquatico") == "nao":
                    if ans.get("tem_escamas") is None:
                        return "tem_escamas"
                    if ans.get("tem_escamas") == "sim":
                        if ans.get("bota_ovos_terra") is None:
                            return "bota_ovos_terra"
                        if ans.get("bota_ovos_terra") == "sim":
                            if ans.get("respira_pulmoes") is None:
                                return "respira_pulmoes"
                            if ans.get("respira_pulmoes") == "sim":
                                return None

        return None

    def _format_answers_summary(self) -> str:
        nomes_caracteristicas = {
            "tem_pelos": "Possui pelos",
            "amamenta": "Amamenta os filhotes",
            "respira_pulmoes": "Respira por pulmões",
            "tem_penas": "Possui penas",
            "bota_ovos": "Bota ovos",
            "tem_bico": "Possui bico",
            "eh_aquatico": "Vive em ambiente aquático",
            "respira_branquias": "Respira por brânquias",
            "tem_escamas": "Possui escamas",
            "bota_ovos_terra": "Bota ovos em terra",
            "tem_nadadeiras": "Possui nadadeiras",
        }

        linhas = []
        for chave, valor in self.answers.items():
            nome = nomes_caracteristicas.get(chave, chave)

            if valor == "sim":
                linhas.append(f"✓ {nome}")
            elif valor == "nao":
                linhas.append(f"✗ {nome}")

        if not linhas:
            return "Nenhuma característica foi registrada."

        return "\n".join(linhas)

    def finish_and_show_result(self) -> None:
        result_text = self.engine.classify(self.answers)
        resumo_respostas = self._format_answers_summary()

        self.label_question.configure(text="Classificação Concluída!")
        self.frame_buttons.pack_forget()
        self.label_result.configure(
            text=f"Resultado: {result_text}\n\nCaracterísticas observadas:\n{resumo_respostas}"
        )
        self.btn_restart.pack(pady=20)
        self.app.progress_bar.set(1)
        self.label_progress_text.configure(text="Classificação concluída")

        self._reset_image_label()
        self.current_image = None

        final_image_path = self.result_images.get(
            result_text,
            self.result_images[self.engine.RESULT_UNKNOWN]
        )
        final_photo = self._load_image(final_image_path)

        if final_photo is not None:
            self.current_image = final_photo
            self.image_display.configure(image=self.current_image, text="")
        else:
            self.image_display.configure(image=None, text="[Imagem de resultado não encontrada]")



class IAScreen(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.engine = AnimalClassifierEngine()
        self.image_path = None

        self.label_title = ctk.CTkLabel(
            self,
            text="Classificação por IA (Foto)",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.label_title.pack(pady=20)

        self.image_display = ctk.CTkLabel(
            self,
            text="Selecione uma imagem",
            width=450,
            height=250,
            fg_color=("white", "#333333")
        )
        self.image_display.pack(pady=15)

        self.btn_select_image = ctk.CTkButton(
            self,
            text="Selecionar Imagem",
            command=self.select_image,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#007bff",
            hover_color="#0056b3",
        )
        self.btn_select_image.pack(pady=10)

        self.btn_classify_ia = ctk.CTkButton(
            self,
            text="Classificar com IA",
            command=self.classify_with_ia,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"
        )
        self.btn_classify_ia.pack(pady=10)

        # Card de resultado
        self.result_frame = ctk.CTkFrame(self, corner_radius=15)
        self.result_frame.pack(pady=20, padx=20, fill="x")

        self.label_result_title = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00aaff"
        )
        self.label_result_title.pack(pady=(15, 10))

        self.label_result_class = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#00c853"
        )
        self.label_result_class.pack(pady=(0, 10))

        self.result_box = ctk.CTkTextbox(
            self.result_frame,
            width=500,
            height=120,
            font=ctk.CTkFont(size=18),
            corner_radius=10
        )
        self.result_box.pack(pady=(0, 15), padx=20)
        self.result_box.configure(state="disabled")

        self.btn_back_to_menu = ctk.CTkButton(
            self,
            text="Voltar ao Menu Principal",
            command=self.app.show_start_screen,
            fg_color="#6c757d",
            hover_color="#5a6268",
        )
        self.btn_back_to_menu.pack(pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecione uma imagem de animal",
            filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )

        if file_path:
            self.image_path = file_path
            img = self._load_image(self.image_path, size=(450, 250))

            if img:
                self.image_display.configure(image=img, text="")
                self.btn_classify_ia.configure(state="normal")
            else:
                self.image_display.configure(image=None, text="[Erro ao carregar imagem]")
                self.btn_classify_ia.configure(state="disabled")

            self.clear_result()

    def _load_image(self, path: str, size: tuple) -> Optional[ctk.CTkImage]:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize(size, Image.LANCZOS)
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            except Exception as e:
                print(f"Erro ao carregar imagem {path}: {e}")
        return None

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def clear_result(self):
        self.label_result_title.configure(text="")
        self.label_result_class.configure(text="")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.configure(state="disabled")

    def show_result(self, classe: str, justificativa: str, confianca: str):
        self.label_result_title.configure(text="Resultado da análise")
        self.label_result_class.configure(text=classe)

        texto_final = (
            f"Justificativa:\n{justificativa}\n\n"
            f"Confiança: {confianca}"
        )

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", texto_final)
        self.result_box.configure(state="disabled")

    def parse_ia_response(self, ia_response: str):
        classe = "Não identificado"
        justificativa = "Não informada."
        confianca = "Não informada"

        for linha in ia_response.splitlines():
            linha = linha.strip()
            if linha.startswith("Classe:"):
                classe = linha.replace("Classe:", "").strip()
            elif linha.startswith("Justificativa:"):
                justificativa = linha.replace("Justificativa:", "").strip()
            elif linha.startswith("Confiança:"):
                confianca = linha.replace("Confiança:", "").strip()

        return classe, justificativa, confianca

    def classify_with_ia(self):
        if not client:
            messagebox.showerror("Erro", "A API da OpenAI não foi inicializada. Verifique sua chave de API.")
            return

        if not self.image_path:
            messagebox.showwarning("Aviso", "Por favor, selecione uma imagem primeiro.")
            return

        self.label_result_title.configure(text="Analisando imagem...")
        self.label_result_class.configure(text="")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", "Aguarde enquanto a IA analisa a imagem.")
        self.result_box.configure(state="disabled")
        self.update_idletasks()

        try:
            base64_image = self.encode_image(self.image_path)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analise a imagem e responda em português, exatamente neste formato:

Classe: [Mamífero, Ave, Peixe, Réptil ou Não foi possível classificar]
Justificativa: [uma frase curta]
Confiança: [Baixa, Média ou Alta]

Responda com apenas 3 linhas."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=100,
            )

            ia_response = response.choices[0].message.content.strip()
            classe, justificativa, confianca = self.parse_ia_response(ia_response)
            self.show_result(classe, justificativa, confianca)

        except Exception as e:
            messagebox.showerror("Erro na IA", f"Ocorreu um erro ao classificar a imagem com IA: {e}")
            self.label_result_title.configure(text="Erro na classificação")
            self.label_result_class.configure(text="")
            self.result_box.configure(state="normal")
            self.result_box.delete("1.0", "end")
            self.result_box.insert("1.0", "Não foi possível concluir a análise da imagem.")
            self.result_box.configure(state="disabled")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Classificador de Animais")
        self.geometry("760x840")
        self.minsize(760, 840)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Cabeçalho global
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=80, fg_color=("#e9ecef", "#1f1f1f"))
        self.header_frame.pack(fill="x")

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Classificador Biológico de Animais",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.header_title.pack(pady=(18, 6))


        # Barra de progresso global
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", width=420)
        self.progress_bar.set(0)

        self.start_screen = StartScreen(self, self)
        self.quiz_screen = QuizScreen(self, self)
        self.ia_screen = IAScreen(self, self)

        self.show_start_screen()

    def show_start_screen(self):
        self.quiz_screen.pack_forget()
        self.ia_screen.pack_forget()
        self.start_screen.pack(fill="both", expand=True)
        self.progress_bar.pack_forget()

    def show_quiz_screen(self):
        self.start_screen.pack_forget()
        self.ia_screen.pack_forget()
        self.quiz_screen.pack(fill="both", expand=True)
        self.quiz_screen.start_quiz()
        self.progress_bar.pack(pady=10)

    def show_ia_screen(self):
        self.start_screen.pack_forget()
        self.quiz_screen.pack_forget()
        self.ia_screen.pack(fill="both", expand=True)
        self.ia_screen.image_display.configure(image=None, text="Selecione uma imagem")
        self.ia_screen.btn_classify_ia.configure(state="disabled")
        self.ia_screen.image_path = None
        self.ia_screen.clear_result()
        self.progress_bar.pack_forget()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()