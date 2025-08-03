import json
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Plano de Estudos CNU 2025 - Analista de Gestão em Pesquisa e Investigação Biomédica",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregamento dos dados


@st.cache_data
def load_study_plan():
    with open("study_plan.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Função para criar cronograma de estudos


def create_study_schedule(start_date, end_date_fixed, weeks_data):
    schedule = []

    # Calcular o número total de dias disponíveis para estudo
    total_days_available = (end_date_fixed - start_date).days + 1

    # Calcular o número de semanas de estudo com base nos dados fornecidos
    num_study_weeks = len([week_name for week_name, subjects in weeks_data.items() if subjects])

    # Calcular a duração média de cada semana
    if num_study_weeks > 0:
        avg_days_per_week = total_days_available / num_study_weeks
    else:
        return schedule # Retorna vazio se não houver semanas de estudo

    current_date = start_date

    for week_name, subjects in weeks_data.items():
        if not subjects:  # Pula semanas vazias
            continue

        week_start = current_date

        # Calcula a data de término da semana com base na duração média
        week_end = week_start + timedelta(days=int(avg_days_per_week) - 1)

        # Ajusta a última semana para terminar exatamente na data fixa
        if week_name == list(weeks_data.keys())[-1]: # Verifica se é a última semana não vazia
            week_end = end_date_fixed

        schedule.append({
            "Semana": week_name,
            "Data Início": week_start.strftime("%d/%m/%Y"),
            "Data Fim": week_end.strftime("%d/%m/%Y"),
            "Matérias": list(subjects.keys())
        })

        current_date = week_end + timedelta(days=1)

    return schedule

# Função para exibir recursos de uma matéria


def display_subject_resources(subject_data):
    for resource_type, resources in subject_data.items():
        if resources:
            st.subheader(f"📋 {resource_type}")

            for i, resource in enumerate(resources, 1):
                with st.expander(f"{i}. {resource['description'][:80]}..."):
                    st.write(f"**Descrição:** {resource['description']}")
                    st.write(f"**Link:** [Acessar recurso]({resource['url']})")

                    # Botão para marcar como concluído
                    key = f"{resource_type}_{i}_{resource['description'][:20]}"
                    if st.button("✅ Marcar como concluído", key=key):
                        if "completed_resources" not in st.session_state:
                            st.session_state.completed_resources = set()
                        st.session_state.completed_resources.add(key)
                        st.success("Recurso marcado como concluído!")

                    # Mostrar se já foi concluído
                    if "completed_resources" in st.session_state and key in st.session_state.completed_resources:
                        st.success("✅ Concluído")


def main():
    # Título principal
    st.title("Plano de Estudos CNU 2025")
    st.subheader(
        "Analista de Gestão em Pesquisa e Investigação Biomédica (B4-13-B)")

    # Carregamento dos dados
    try:
        study_data = load_study_plan()
    except FileNotFoundError:
        st.error("Arquivo de dados não encontrado. Certifique-se de que o arquivo \"study_plan.json\" está no diretório correto.")
        return

    # Sidebar para navegação
    st.sidebar.title("Navegação")

    # Opções de visualização
    view_option = st.sidebar.selectbox(
        "Escolha a visualização:",
        ["📅 Cronograma Geral", "📖 Estudo por Semana",
            "📊 Progresso", "🔍 Buscar Recursos"]
    )

    if view_option == "📅 Cronograma Geral":
        st.header("Cronograma de Estudos")

        # Seletor de data de início
        start_date = st.date_input(
            "Data de início dos estudos:",
            value=datetime.now().date(),
            help="Selecione quando você pretende começar os estudos"
        )

        # Data de término fixa
        end_date_fixed = datetime(2025, 10, 4).date() # 04/10/2025
        st.write(f"**Data de término dos estudos para a prova:** {end_date_fixed.strftime('%d/%m/%Y')}")

        # Criar cronograma
        schedule = create_study_schedule(start_date, end_date_fixed, study_data)

        # Exibir cronograma em tabela
        if schedule:
            df_schedule = pd.DataFrame(schedule)
            df_schedule["Matérias"] = df_schedule["Matérias"].apply(
                lambda x: ", ".join(x))
            st.dataframe(df_schedule, use_container_width=True)

            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Semanas", len(schedule))
            with col2:
                # Corrigido: Somar o comprimento das listas de matérias diretamente
                total_subjects = sum(
                    len(week_data["Matérias"]) for week_data in schedule if week_data["Matérias"])
                st.metric("Total de Matérias", total_subjects)
            with col3:
                # end_date = datetime.strptime(
                #     schedule[-1]["Data Fim"], "%d/%m/%Y")
                # duration = (end_date - start_date).timedelta(days=0)
                # st.metric("Duração (dias)", duration)
                end_date = datetime.strptime(schedule[-1]["Data Fim"], "%d/%m/%Y").date()
                duration = (end_date - start_date).days
                st.metric("Duração (dias)", duration)

    elif view_option == "📖 Estudo por Semana":
        st.header("Estudo Detalhado por Semana")

        # Filtrar semanas que têm conteúdo
        weeks_with_content = {k: v for k, v in study_data.items() if v}

        # Seletor de semana
        selected_week = st.selectbox(
            "Selecione a semana:",
            list(weeks_with_content.keys())
        )

        if selected_week and selected_week in weeks_with_content:
            week_data = weeks_with_content[selected_week]

            st.subheader(f"📚 {selected_week}")

            # Seletor de matéria
            subjects = list(week_data.keys())
            selected_subject = st.selectbox(
                "Selecione a matéria:",
                subjects
            )

            if selected_subject:
                st.subheader(f"📖 {selected_subject}")
                subject_data = week_data[selected_subject]

                # Exibir recursos da matéria
                display_subject_resources(subject_data)

    elif view_option == "📊 Progresso":
        st.header("Acompanhamento de Progresso")

        # Inicializar session state se necessário
        if "completed_resources" not in st.session_state:
            st.session_state.completed_resources = set()

        # Calcular estatísticas de progresso
        total_resources = 0
        completed_resources = len(st.session_state.completed_resources)

        for week_name, week_data in study_data.items():
            for subject_name, subject_data in week_data.items():
                for resource_type, resources in subject_data.items():
                    total_resources += len(resources)

        # Exibir métricas de progresso
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Recursos Concluídos", completed_resources)

        with col2:
            st.metric("Total de Recursos", total_resources)

        with col3:
            if total_resources > 0:
                progress_percentage = (
                    completed_resources / total_resources) * 100
                st.metric("Progresso", f"{progress_percentage:.1f}%")
            else:
                st.metric("Progresso", "0%")

        # Barra de progresso
        if total_resources > 0:
            progress = completed_resources / total_resources
            st.progress(progress)

            # Gráfico de progresso por semana
            st.subheader("📈 Progresso por Semana")

            week_progress = {}
            for week_name, week_data in study_data.items():
                if not week_data:
                    continue

                week_total = 0
                week_completed = 0

                for subject_name, subject_data in week_data.items():
                    for resource_type, resources in subject_data.items():
                        week_total += len(resources)
                        # Contar recursos concluídos desta semana
                        for i, resource in enumerate(resources, 1):
                            key = f"{resource_type}_{i}_{resource['description'][:20]}"
                            if key in st.session_state.completed_resources:
                                week_completed += 1

                if week_total > 0:
                    week_progress[week_name] = (
                        week_completed / week_total) * 100

            if week_progress:
                df_progress = pd.DataFrame(list(week_progress.items()), columns=[
                                           "Semana", "Progresso (%)"])
                st.bar_chart(df_progress.set_index("Semana"))

        # Botão para resetar progresso
        if st.button("🔄 Resetar Progresso"):
            st.session_state.completed_resources = set()
            st.success("Progresso resetado!")
            st.rerun()

    elif view_option == "🔍 Buscar Recursos":
        st.header("Buscar Recursos")

        # Campo de busca
        search_term = st.text_input(
            "Digite o termo de busca:", placeholder="Ex: português, questões, PDF...")

        if search_term:
            search_results = []

            for week_name, week_data in study_data.items():
                for subject_name, subject_data in week_data.items():
                    for resource_type, resources in subject_data.items():
                        for resource in resources:
                            if search_term.lower() in resource['description'].lower():
                                search_results.append({
                                    "Semana": week_name,
                                    "Matéria": subject_name,
                                    "Tipo": resource_type,
                                    "Descrição": resource['description'],
                                    "URL": resource['url']
                                })

            if search_results:
                st.success(f"Encontrados {len(search_results)} recursos:")

                for i, result in enumerate(search_results, 1):
                    with st.expander(f"{i}. {result['Descrição'][:80]}..."):
                        st.write(f"**Semana:** {result['Semana']}")
                        st.write(f"**Matéria:** {result['Matéria']}")
                        st.write(f"**Tipo:** {result['Tipo']}")
                        st.write(f"**Descrição:** {result['Descrição']}")
                        st.write(
                            f"**Link:** [Acessar recurso]({result['URL']})")
            else:
                st.warning("Nenhum recurso encontrado com o termo pesquisado.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style=\'text-align: center; color: #666;\'>
            Plano de Estudos CNU 2025 - Banca FGV<br>
            <a href="mailto:alanderson.paula@gmail.com?subject=Projeto Streamlit CNU 2025">alanderson.paula@gmail.com</a> | © 2025

        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
