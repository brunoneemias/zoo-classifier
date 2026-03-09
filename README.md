# 🧬 Animal Classifier AI

Sistema de **classificação de animais** baseado em características biológicas e análise de imagem com **Inteligência Artificial**, desenvolvido em **Python** com interface gráfica usando **CustomTkinter**.

O sistema permite identificar se um animal é **Mamífero, Ave, Peixe ou Réptil** através de duas abordagens:

- 🧠 **Quiz Biológico** – classificação por características físicas do animal
- 🤖 **Classificação por IA** – análise de imagem utilizando a API da OpenAI

---

## 🚀 Funcionalidades

✔ Classificação de animais por características biológicas  
✔ Interface gráfica moderna com **CustomTkinter**  
✔ Classificação por **imagem usando IA**  
✔ Sistema de perguntas dinâmico (fluxo inteligente)  
✔ Tratamento de **casos especiais** como golfinhos e baleias  
✔ Exibição de imagens educativas durante o quiz  

---

## 🖥️ Interface do Sistema

### Menu Inicial

Sistema permite escolher entre classificação por quiz ou por IA.

```
[ Quiz Biológico ]  [ Classificação por IA ]
```

### Quiz Biológico

O usuário responde perguntas como:

- O animal possui pelos?
- O animal possui penas?
- O animal respira por brânquias?
- O animal possui escamas?

Com base nas respostas o sistema classifica automaticamente o animal.

### Classificação por IA

O usuário pode:

1. Selecionar uma imagem de animal
2. Enviar para análise
3. O sistema utiliza **IA para identificar a classe do animal**

---

## 🧠 Lógica de Classificação

O algoritmo utiliza características biológicas clássicas da zoologia:

| Classe | Características |
|--------|----------------|
| 🐾 Mamíferos | pelos, amamentação, respiração pulmonar |
| 🦅 Aves | penas, ovos, bico |
| 🐟 Peixes | brânquias, escamas, nadadeiras |
| 🐍 Répteis | escamas, ovos em terra, pulmões |

Também trata **casos especiais**, como:

- 🐬 Golfinhos
- 🐳 Baleias

Que são **mamíferos aquáticos**.

---

## 🛠️ Tecnologias Utilizadas

- **Python**
- **CustomTkinter**
- **Pillow (PIL)**
- **OpenAI API**
- **Base64** (processamento de imagem)

---

## 📦 Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/animal-classifier-ai.git
```

Entre na pasta:

```bash
cd animal-classifier-ai
```

Instale as dependências:

```bash
pip install customtkinter pillow openai
```

---

## 🔑 Configuração da API da OpenAI

Configure sua chave como variável de ambiente:

**Windows**
```bash
setx OPENAI_API_KEY "sua_chave_aqui"
```

**Linux / Mac**
```bash
export OPENAI_API_KEY="sua_chave_aqui"
```

---

## ▶️ Executar o Sistema

```bash
python animal_classification_system.py
```

---

## 📂 Estrutura do Projeto

```
animal-classifier-ai/
│
├── animal_classification_system.py
├── fluxograma.html
├── README.md
├── .gitignore
│
└── imagens/
    │
    ├── menu/
    │   ├── icon_app.png
    │   ├── icon_quiz.png
    │   └── icon_ai.png
    │
    └── quiz/
        ├── pelos.png
        ├── pena.png
        ├── escamas.jpeg
        ├── branquias.png
        ├── nadadeiras.jpg
        ├── ovos.png
        ├── ovos_terra.jpg
        ├── resultado_mamifero.jpg
        ├── resultado_ave.jpg
        ├── resultado_peixe.jpg
        └── resultado_reptil.jpg
```

---

## 🎓 Objetivo Educacional

Este projeto foi desenvolvido como atividade da disciplina:

> **Engenharia de Sistemas de Segurança e Aplicações de Inteligência Artificial**

**Curso:** Defesa Cibernética – FATEC

---

## 👨‍💻 Autor

**Bruno Alves**  
Estudante de Defesa Cibernética

Interesse em:
- 🔐 Cybersecurity
- 🤖 Artificial Intelligence
- ⚙️ DevOps
- 🌐 Network Security

---

## ⭐ Melhorias Futuras

- [ ] Adicionar mais classes de animais
- [ ] Treinar modelo de visão computacional próprio
- [ ] Exportar resultados em relatório
- [ ] Melhorar sistema de explicação da IA

---

## 📜 Licença

Este projeto é de uso educacional.
