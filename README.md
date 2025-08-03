# Plano de Estudos CNU 2025 - Streamlit App

## Descrição

Este é um aplicativo Streamlit interativo desenvolvido para organizar e apresentar o plano de estudos do CNU 2025 para o cargo de **Analista de Gestão em Pesquisa e Investigação Biomédica (B4-13-B)**.

O aplicativo foi criado a partir do plano de estudos original em formato Markdown, estruturando todos os recursos de estudo (videoaulas, materiais em PDF e provas anteriores) de forma organizada e interativa.

## Funcionalidades

### 📅 Cronograma Geral
- Visualização completa do cronograma de estudos
- Seleção de data de início personalizada
- Tabela com datas de início e fim de cada semana
- Estatísticas do plano (total de semanas, matérias e duração)

### 📖 Estudo por Semana
- Navegação por semanas de estudo
- Seleção de matérias específicas
- Visualização detalhada de recursos por tipo:
  - 📹 Videoaulas
  - 📄 Materiais em PDF
  - 📝 Provas Anteriores/Questões
- Botões para marcar recursos como concluídos

### 📊 Progresso
- Acompanhamento do progresso geral dos estudos
- Métricas de recursos concluídos vs. total
- Barra de progresso visual
- Gráfico de progresso por semana
- Botão para resetar progresso

### 🔍 Buscar Recursos
- Sistema de busca por palavras-chave
- Busca em todas as descrições de recursos
- Resultados organizados por semana, matéria e tipo
- Links diretos para os recursos encontrados

## Estrutura dos Dados

O aplicativo utiliza um arquivo JSON (`study_plan.json`) que contém todos os dados estruturados do plano de estudos, organizados hierarquicamente:

```
Semana
├── Matéria
    ├── Videoaulas
    ├── Materiais em PDF
    └── Provas Anteriores/Questões
```

Cada recurso contém:
- **description**: Descrição do recurso
- **url**: Link para acessar o recurso

## Tecnologias Utilizadas

- **Streamlit**: Framework principal para a interface web
- **Python**: Linguagem de programação
- **Pandas**: Manipulação de dados
- **JSON**: Armazenamento estruturado dos dados

## Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Instalação
1. Clone ou baixe os arquivos do projeto
2. Instale o Streamlit:
   ```bash
   pip install streamlit
   ```

### Execução
1. Navegue até o diretório do projeto
2. Execute o comando:
   ```bash
   streamlit run app.py
   ```
3. O aplicativo será aberto automaticamente no navegador

## Arquivos do Projeto

- `app.py`: Código principal do aplicativo Streamlit
- `study_plan.json`: Dados estruturados do plano de estudos
- `parse_study_plan.py`: Script para converter o Markdown original em JSON
- `README.md`: Esta documentação

## Recursos do Plano de Estudos

O plano abrange as seguintes áreas de conhecimento:

### Conhecimentos Gerais (Semanas 1-2)
- Língua Portuguesa
- Raciocínio Lógico e Matemático
- Atualidades
- Noções de Informática
- Políticas Públicas
- Ética e Integridade
- Diversidade e Inclusão
- Administração Pública Federal
- Trabalho e Tecnologia

### Conhecimentos Específicos (Semanas 3-4)
- Engenharia de Controle e Automação
- Gestão de Projetos
- Normas Técnicas e Regulamentações
- Saúde e Segurança no Trabalho

### Planejamento e Sustentabilidade (Semanas 5-6)
- Planejamento e Projetos de Obras
- Sustentabilidade e Patrimônio Cultural
- Sistemas Automatizados

### Prova Discursiva
- Redação Técnica
- Estudo de Caso

### Preparação Final (Semanas 7-8)
- Revisão Geral
- Preparação Final

## Estatísticas do Plano

- **Total de recursos**: 255 recursos de estudo
- **Videoaulas**: Links para aulas específicas da banca FGV
- **Materiais em PDF**: Apostilas, livros e materiais de estudo
- **Provas Anteriores**: Questões e simulados da banca FGV

## Funcionalidades Interativas

### Sistema de Progresso
- Marque recursos como concluídos
- Acompanhe seu progresso em tempo real
- Visualize estatísticas por semana
- Reset do progresso quando necessário

### Busca Inteligente
- Encontre rapidamente recursos específicos
- Busca por matéria, tipo de recurso ou palavra-chave
- Resultados organizados e fáceis de navegar

### Cronograma Personalizado
- Defina sua data de início
- Visualize o cronograma completo
- Planeje seus estudos com antecedência

## Suporte e Melhorias

Este aplicativo foi desenvolvido para otimizar a preparação para o CNU 2025. Todas as funcionalidades foram testadas e estão funcionando corretamente.

Para melhorias futuras, considere:
- Adicionar notificações de estudo
- Integração com calendário
- Exportação de relatórios de progresso
- Sistema de notas e anotações

---


