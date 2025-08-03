import json
import os
from datetime import datetime, timedelta
import base64

import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Plano de Estudos CNU 2025 - Analista de Gestão em Pesquisa e Investigação Biomédica",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Arquivo do plano de estudos
STUDY_PLAN_FILE = "study_plan.json"

# Carregamento dos dados do plano de estudos
@st.cache_data
def load_study_plan():
    try:
        with open(STUDY_PLAN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Arquivo {STUDY_PLAN_FILE} não encontrado!")
        return {}

# Funções para gerenciar dados do usuário usando session_state
def initialize_user_data():
    """Inicializa os dados do usuário no session_state se não existirem"""
    if "user_progress" not in st.session_state:
        st.session_state.user_progress = {
            "start_date": datetime.now().date().isoformat(),
            "completed_resources": [],
            "settings": {
                "notifications": True,
                "theme": "light"
            },
            "last_access": datetime.now().isoformat(),
            "study_sessions": [],
            "initialization_date": datetime.now().isoformat()
        }

def update_last_access():
    """Atualiza o último acesso"""
    if "user_progress" in st.session_state:
        st.session_state.user_progress["last_access"] = datetime.now().isoformat()

def export_progress_data():
    """Exporta os dados de progresso para download"""
    if "user_progress" in st.session_state:
        progress_data = st.session_state.user_progress.copy()
        progress_data["export_date"] = datetime.now().isoformat()
        return json.dumps(progress_data, ensure_ascii=False, indent=2)
    return "{}"

def import_progress_data(imported_data):
    """Importa dados de progresso de um backup"""
    try:
        data = json.loads(imported_data)
        # Validar estrutura básica
        required_keys = ["start_date", "completed_resources", "study_sessions"]
        if all(key in data for key in required_keys):
            st.session_state.user_progress = data
            st.session_state.user_progress["last_access"] = datetime.now().isoformat()
            return True
        else:
            return False
    except json.JSONDecodeError:
        return False

def add_completed_resource(resource_key):
    """Adiciona um recurso como concluído"""
    initialize_user_data()
    if resource_key not in st.session_state.user_progress["completed_resources"]:
        st.session_state.user_progress["completed_resources"].append(resource_key)
        update_last_access()

def remove_completed_resource(resource_key):
    """Remove um recurso dos concluídos"""
    initialize_user_data()
    if resource_key in st.session_state.user_progress["completed_resources"]:
        st.session_state.user_progress["completed_resources"].remove(resource_key)
        update_last_access()

def update_start_date(new_date):
    """Atualiza a data de início"""
    initialize_user_data()
    st.session_state.user_progress["start_date"] = new_date.isoformat()
    update_last_access()

def add_study_session(duration_minutes, subjects_studied):
    """Adiciona uma sessão de estudo"""
    initialize_user_data()
    session = {
        "date": datetime.now().isoformat(),
        "duration_minutes": duration_minutes,
        "subjects": subjects_studied
    }
    st.session_state.user_progress["study_sessions"].append(session)
    update_last_access()

def is_resource_completed(resource_key):
    """Verifica se um recurso está concluído"""
    initialize_user_data()
    return resource_key in st.session_state.user_progress["completed_resources"]

# Função para criar cronograma de estudos
def create_study_schedule(start_date, end_date_fixed, weeks_data):
    schedule = []

    # Calcular o número total de dias disponíveis para estudo
    total_days_available = (end_date_fixed - start_date).days + 1

    # Calcular o número de Etapas de estudo com base nos dados fornecidos
    num_study_weeks = len([week_name for week_name, subjects in weeks_data.items() if subjects])

    # Calcular a duração média de cada Etapa
    if num_study_weeks > 0:
        avg_days_per_week = total_days_available / num_study_weeks
    else:
        return schedule # Retorna vazio se não houver Etapas de estudo

    current_date = start_date

    for week_name, subjects in weeks_data.items():
        if not subjects:  # Pula Etapas vazias
            continue

        week_start = current_date

        # Calcula a data de término da Etapa com base na duração média
        week_end = week_start + timedelta(days=int(avg_days_per_week) - 1)

        # Ajusta a última Etapa para terminar exatamente na data fixa
        if week_name == list(weeks_data.keys())[-1]: # Verifica se é a última Etapa não vazia
            week_end = end_date_fixed

        schedule.append({
            "Etapa": week_name,
            "Data Início": week_start.strftime("%d/%m/%Y"),
            "Data Fim": week_end.strftime("%d/%m/%Y"),
            "Matérias": list(subjects.keys())
        })

        current_date = week_end + timedelta(days=1)

    return schedule

# Função para exibir recursos de uma matéria
def display_subject_resources(subject_data, week_name, subject_name):
    for resource_type, resources in subject_data.items():
        if resources:
            st.subheader(f"📋 {resource_type}")

            for i, resource in enumerate(resources, 1):
                # Criar chave única para o recurso
                resource_key = f"{week_name}_{subject_name}_{resource_type}_{i}_{resource['description'][:20]}"
                
                # Verificar se já foi concluído
                is_completed = is_resource_completed(resource_key)
                
                with st.expander(f"{'✅' if is_completed else '📄'} {i}. {resource['description'][:80]}..."):
                    st.write(f"**Descrição:** {resource['description']}")
                    st.write(f"**Link:** [Acessar recurso]({resource['url']})")

                    # Botão para marcar/desmarcar como concluído
                    col1, col2 = st.columns([3, 1])
                    
                    with col2:
                        if is_completed:
                            if st.button("❌ Desmarcar", key=f"uncheck_{resource_key}"):
                                remove_completed_resource(resource_key)
                                st.success("Recurso desmarcado!")
                                st.rerun()
                        else:
                            if st.button("✅ Concluído", key=f"check_{resource_key}"):
                                add_completed_resource(resource_key)
                                st.success("Recurso marcado como concluído!")
                                st.rerun()
                    
                    with col1:
                        if is_completed:
                            st.success("✅ Concluído")

def days_float_to_days_hours(days_float):
    days = int(days_float)
    hours = int(round((days_float - days) * 24))
    return f"{days}d e {hours}h"


def main():
    # Inicializar dados do usuário
    initialize_user_data()
    update_last_access()

    # Título principal
    st.title("Plano de Estudos CNU 2025 - Engenharias e Arquitetura")
    st.subheader("Analista de Gestão em Pesquisa e Investigação Biomédica (B4-13-B)")

    # Indicador de progresso salvo
    completed_count = len(st.session_state.user_progress["completed_resources"])
    st.sidebar.success(f"💾 {completed_count} recursos concluídos salvos")
    
    # Mostrar último acesso
    if "last_access" in st.session_state.user_progress:
        last_access = datetime.fromisoformat(st.session_state.user_progress["last_access"])
        st.sidebar.info(f"Última atualização: {last_access.strftime('%d/%m/%Y %H:%M')}")

    # Carregamento dos dados do plano de estudos
    try:
        study_data = load_study_plan()
        if not study_data:
            st.error("Nenhum dado de estudo encontrado.")
            return
    except Exception as e:
        st.error(f"Erro ao carregar plano de estudos: {str(e)}")
        return

    # Sidebar para navegação
    st.sidebar.title("Navegação")

    # Opções de visualização
    view_option = st.sidebar.selectbox(
        "Escolha a visualização:",
        ["📅 Cronograma Geral", "📖 Estudo por Etapa", "📊 Progresso", "🔍 Buscar Recursos", "⚙️ Dados e Backup"]
    )

    if view_option == "📅 Cronograma Geral":
        st.header("Cronograma de Estudos")

        # Seletor de data de início (carrega data salva)
        saved_start_date = datetime.fromisoformat(st.session_state.user_progress["start_date"]).date()
        
        start_date = st.date_input(
            "Data de início dos estudos:",
            value=saved_start_date,
            help="Selecione quando você pretende começar os estudos"
        )

        # Verificar se a data mudou e salvar
        if start_date != saved_start_date:
            update_start_date(start_date)
            st.success("✅ Data de início salva automaticamente!")

        # Data de término fixa
        end_date_fixed = datetime(2025, 10, 4).date() # 04/10/2025
        st.write(f"**Data de término dos estudos para a prova:** {end_date_fixed.strftime('%d/%m/%Y')}")

        # Criar cronograma
        schedule = create_study_schedule(start_date, end_date_fixed, study_data)

        # Exibir cronograma em tabela
        if schedule:
            df_schedule = pd.DataFrame(schedule)
            df_schedule["Matérias"] = df_schedule["Matérias"].apply(lambda x: ", ".join(x))
            st.dataframe(df_schedule, use_container_width=True)

            exit_text = days_float_to_days_hours(avg_days_per_week)
            
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Etapas", len(schedule))
            with col2:
                st.metric("Período por Etapas", exit_text)
            with col3:
                total_subjects = sum(len(week_data["Matérias"]) for week_data in schedule if week_data["Matérias"])
                st.metric("Total de Matérias", total_subjects)
            with col4:
                end_date = datetime.strptime(schedule[-1]["Data Fim"], "%d/%m/%Y").date()
                duration = (end_date - start_date).days
                st.metric("Duração (dias)", duration)

    elif view_option == "📖 Estudo por Etapa":
        st.header("Estudo Detalhado por Etapa")

        # Filtrar Etapas que têm conteúdo
        weeks_with_content = {k: v for k, v in study_data.items() if v}

        # Seletor de Etapa
        selected_week = st.selectbox("Selecione a Etapa:", list(weeks_with_content.keys()))

        if selected_week and selected_week in weeks_with_content:
            week_data = weeks_with_content[selected_week]
            st.subheader(f"📚 {selected_week}")

            # Seletor de matéria
            subjects = list(week_data.keys())
            selected_subject = st.selectbox("Selecione a matéria:", subjects)

            if selected_subject:
                st.subheader(f"📖 {selected_subject}")
                subject_data = week_data[selected_subject]

                # Exibir recursos da matéria
                display_subject_resources(subject_data, selected_week, selected_subject)

                # Seção para registrar sessão de estudo
                st.markdown("---")
                st.subheader("📝 Registrar Sessão de Estudo")
                
                col1, col2 = st.columns(2)
                with col1:
                    study_duration = st.number_input("Duração do estudo (minutos):", min_value=1, max_value=480, value=60)
                with col2:
                    if st.button("💾 Registrar Sessão"):
                        add_study_session(study_duration, [selected_subject])
                        st.success(f"✅ Sessão de {study_duration} minutos registrada para {selected_subject}!")

    elif view_option == "📊 Progresso":
        st.header("Acompanhamento de Progresso")

        # Calcular estatísticas de progresso
        total_resources = 0
        completed_resources = len(st.session_state.user_progress["completed_resources"])

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
                progress_percentage = (completed_resources / total_resources) * 100
                st.metric("Progresso", f"{progress_percentage:.1f}%")
            else:
                st.metric("Progresso", "0%")

        # Barra de progresso
        if total_resources > 0:
            progress = completed_resources / total_resources
            st.progress(progress)

            # Estatísticas de sessões de estudo
            study_sessions = st.session_state.user_progress.get("study_sessions", [])
            if study_sessions:
                st.subheader("📈 Estatísticas de Estudo")
                
                total_study_time = sum(session["duration_minutes"] for session in study_sessions)
                total_sessions = len(study_sessions)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Sessões", total_sessions)
                with col2:
                    st.metric("Tempo Total", f"{total_study_time//60}h {total_study_time%60}m")
                with col3:
                    if total_sessions > 0:
                        avg_session = total_study_time / total_sessions
                        st.metric("Média por Sessão", f"{int(avg_session)} min")

                # Mostrar últimas sessões
                st.subheader("🕒 Últimas Sessões de Estudo")
                recent_sessions = study_sessions[-5:] if len(study_sessions) > 5 else study_sessions
                
                for session in reversed(recent_sessions):
                    session_date = datetime.fromisoformat(session["date"]).strftime("%d/%m/%Y %H:%M")
                    subjects_str = ", ".join(session["subjects"])
                    st.write(f"📅 {session_date} - ⏱️ {session['duration_minutes']}min - 📚 {subjects_str}")

            # Gráfico de progresso por Etapa
            st.subheader("📊 Progresso por Etapa")

            week_progress = {}
            completed_set = set(st.session_state.user_progress["completed_resources"])
            
            for week_name, week_data in study_data.items():
                if not week_data:
                    continue

                week_total = 0
                week_completed = 0

                for subject_name, subject_data in week_data.items():
                    for resource_type, resources in subject_data.items():
                        week_total += len(resources)
                        # Contar recursos concluídos desta Etapa
                        for i, resource in enumerate(resources, 1):
                            resource_key = f"{week_name}_{subject_name}_{resource_type}_{i}_{resource['description'][:20]}"
                            if resource_key in completed_set:
                                week_completed += 1

                if week_total > 0:
                    week_progress[week_name] = (week_completed / week_total) * 100

            if week_progress:
                df_progress = pd.DataFrame(list(week_progress.items()), columns=["Etapa", "Progresso (%)"])
                st.bar_chart(df_progress.set_index("Etapa"))

    elif view_option == "🔍 Buscar Recursos":
        st.header("Buscar Recursos")

        # Campo de busca
        search_term = st.text_input("Digite o termo de busca:", placeholder="Ex: português, questões, PDF...")

        if search_term:
            search_results = []

            for week_name, week_data in study_data.items():
                for subject_name, subject_data in week_data.items():
                    for resource_type, resources in subject_data.items():
                        for i, resource in enumerate(resources, 1):
                            if search_term.lower() in resource['description'].lower():
                                resource_key = f"{week_name}_{subject_name}_{resource_type}_{i}_{resource['description'][:20]}"
                                is_completed = is_resource_completed(resource_key)
                                
                                search_results.append({
                                    "Etapa": week_name,
                                    "Matéria": subject_name,
                                    "Tipo": resource_type,
                                    "Descrição": resource['description'],
                                    "URL": resource['url'],
                                    "Concluído": "✅" if is_completed else "❌",
                                    "Key": resource_key
                                })

            if search_results:
                st.success(f"Encontrados {len(search_results)} recursos:")

                for i, result in enumerate(search_results, 1):
                    is_completed = result["Concluído"] == "✅"
                    with st.expander(f"{result['Concluído']} {i}. {result['Descrição'][:80]}..."):
                        st.write(f"**Etapa:** {result['Etapa']}")
                        st.write(f"**Matéria:** {result['Matéria']}")
                        st.write(f"**Tipo:** {result['Tipo']}")
                        st.write(f"**Descrição:** {result['Descrição']}")
                        st.write(f"**Link:** [Acessar recurso]({result['URL']})")
                        
                        # Botão para marcar/desmarcar
                        if is_completed:
                            if st.button("❌ Desmarcar", key=f"search_uncheck_{i}"):
                                remove_completed_resource(result["Key"])
                                st.success("Recurso desmarcado!")
                                st.rerun()
                        else:
                            if st.button("✅ Marcar como concluído", key=f"search_check_{i}"):
                                add_completed_resource(result["Key"])
                                st.success("Recurso marcado como concluído!")
                                st.rerun()
            else:
                st.warning("Nenhum recurso encontrado com o termo pesquisado.")

    elif view_option == "⚙️ Dados e Backup":
        st.header("Backup e Configurações")
        
        # Informações da sessão
        st.subheader("📊 Informações da Sessão Atual")
        
        init_date = datetime.fromisoformat(st.session_state.user_progress["initialization_date"])
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Sessão iniciada:** {init_date.strftime('%d/%m/%Y %H:%M')}")
            st.info(f"**Recursos concluídos:** {len(st.session_state.user_progress['completed_resources'])}")
        
        with col2:
            total_sessions = len(st.session_state.user_progress.get('study_sessions', []))
            st.info(f"**Sessões de estudo:** {total_sessions}")
            if st.session_state.user_progress.get('study_sessions'):
                total_time = sum(s['duration_minutes'] for s in st.session_state.user_progress['study_sessions'])
                st.info(f"**Tempo total:** {total_time//60}h {total_time%60}m")

        # Backup e Restauração
        st.subheader("💾 Backup e Restauração")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Fazer Backup:**")
            backup_data = export_progress_data()
            
            st.download_button(
                label="📤 Baixar Backup Completo",
                data=backup_data,
                file_name=f"cnu_progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Baixe este arquivo para fazer backup do seu progresso"
            )
            
            # Mostrar preview dos dados
            if st.checkbox("🔍 Visualizar dados do backup"):
                st.code(backup_data, language="json")
        
        with col2:
            st.write("**Restaurar Backup:**")
            uploaded_file = st.file_uploader(
                "Selecione um arquivo de backup",
                type=['json'],
                help="Carregue um arquivo de backup para restaurar seu progresso"
            )
            
            if uploaded_file is not None:
                try:
                    backup_content = uploaded_file.read().decode('utf-8')
                    
                    if st.button("🔄 Restaurar Backup"):
                        if import_progress_data(backup_content):
                            st.success("✅ Backup restaurado com sucesso!")
                            st.balloons()
                            # Pequeno delay para mostrar a mensagem antes do rerun
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao restaurar backup. Verifique se o arquivo está correto.")
                except Exception as e:
                    st.error(f"❌ Erro ao ler arquivo: {str(e)}")

        # Reset de dados
        st.subheader("⚠️ Reset de Dados")
        
        with st.expander("🔴 Área de Reset (Cuidado!)"):
            st.warning("**Atenção:** Esta ação não pode ser desfeita!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Resetar apenas progresso"):
                    st.session_state.user_progress["completed_resources"] = []
                    update_last_access()
                    st.success("Progresso resetado!")
                    st.rerun()
            
            with col2:
                if st.button("💥 Reset completo"):
                    # Criar dados padrão
                    st.session_state.user_progress = {
                        "start_date": datetime.now().date().isoformat(),
                        "completed_resources": [],
                        "settings": {"notifications": True, "theme": "light"},
                        "last_access": datetime.now().isoformat(),
                        "study_sessions": [],
                        "initialization_date": datetime.now().isoformat()
                    }
                    st.success("Reset completo realizado!")
                    st.rerun()

        # Estatísticas detalhadas
        st.subheader("📈 Estatísticas Detalhadas")
        
        if st.session_state.user_progress.get('study_sessions'):
            sessions_df = pd.DataFrame(st.session_state.user_progress['study_sessions'])
            sessions_df['date'] = pd.to_datetime(sessions_df['date']).dt.strftime('%d/%m/%Y')
            sessions_df['subjects'] = sessions_df['subjects'].apply(lambda x: ', '.join(x))
            
            st.write("**Histórico de Sessões de Estudo:**")
            st.dataframe(sessions_df, use_container_width=True)

    # Footer com informações importantes
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666;'>
            Plano de Estudos CNU 2025 - Banca FGV<br>
            <a href="mailto:alanderson.paula@gmail.com?subject=Projeto Streamlit CNU 2025">alanderson.paula@gmail.com</a> | © 2025
            <br><small>💾 Progresso salvo na sessão - {len(st.session_state.user_progress["completed_resources"])} recursos concluídos</small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
