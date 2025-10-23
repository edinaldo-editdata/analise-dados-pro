import streamlit as st
import pandas as pd
import numpy as np
import io
import pickle
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Análise de Dados Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do session state
if 'datasets' not in st.session_state:
    st.session_state.datasets = {}
if 'projects' not in st.session_state:
    st.session_state.projects = {}
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'auto_save_enabled' not in st.session_state:
    st.session_state.auto_save_enabled = True

# Funções auxiliares
def load_csv_file(file):
    """Carrega arquivo CSV"""
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding='latin1')
    
    # Trata valores vazios como NaN
    df = clean_empty_values(df)
    return df

def load_txt_file(file):
    """Carrega arquivo TXT"""
    content = str(file.read(), "utf-8")
    # Tenta detectar o delimitador
    delimiters = [',', ';', '\t', '|']
    for delimiter in delimiters:
        if delimiter in content:
            df = pd.read_csv(io.StringIO(content), delimiter=delimiter)
            return clean_empty_values(df)
    # Se não encontrar delimitador, cria DataFrame com uma coluna
    lines = content.strip().split('\n')
    df = pd.DataFrame({'data': lines})
    return clean_empty_values(df)

def load_excel_file(file):
    """Carrega arquivo Excel"""
    df = pd.read_excel(file)
    return clean_empty_values(df)

def clean_empty_values(df):
    """Limpa valores vazios e os converte para NaN"""
    # Converte diferentes tipos de valores vazios para NaN
    df = df.replace('', np.nan)  # String vazia
    df = df.replace(' ', np.nan)  # Espaços únicos
    df = df.replace('  ', np.nan)  # Múltiplos espaços
    df = df.replace('   ', np.nan)  # Mais espaços
    df = df.replace('NULL', np.nan)  # NULL strings
    df = df.replace('null', np.nan)  # null minúsculo
    df = df.replace('None', np.nan)  # None strings
    df = df.replace('none', np.nan)  # none minúsculo
    df = df.replace('#N/A', np.nan)  # Erro Excel
    df = df.replace('#REF!', np.nan)  # Erro Excel
    df = df.replace('#VALUE!', np.nan)  # Erro Excel
    df = df.replace('N/A', np.nan)  # Not Available
    df = df.replace('n/a', np.nan)  # Not Available minúsculo
    df = df.replace('-', np.nan)  # Traços usados como placeholders
    
    # Para cada coluna de texto, remove espaços e converte vazias para NaN
    for col in df.columns:
        if df[col].dtype == 'object':
            # Converte para string primeiro (caso haja valores mistos)
            df[col] = df[col].astype(str)
            # Remove espaços em branco no início e fim
            df[col] = df[col].str.strip()
            # Converte strings vazias para NaN
            df[col] = df[col].replace('', np.nan)
            df[col] = df[col].replace('nan', np.nan)
            
            # CORREÇÃO PARA ERRO ARROW: Força todas as colunas object a permanecerem como string
            # Isso evita que o Streamlit tente converter automaticamente para outros tipos
            try:
                # Tenta detectar se é numérico, mas mantém como string se houver valores mistos
                pd.to_numeric(df[col], errors='raise')
            except (ValueError, TypeError):
                # Se não conseguir converter tudo para numérico, mantém como string
                df[col] = df[col].astype('string')
    
    return df

def parse_pasted_data(data):
    """Converte dados colados em DataFrame com suporte a quebras de linha e formatos diversos"""
    try:
        lines = data.strip().split('\n')
        
        # Detecta delimitador comum
        delimiters = [',', ';', '\t', '|']
        delimiter = None
        
        # Verifica se há delimitadores nas primeiras linhas
        for d in delimiters:
            if any(d in line for line in lines[:3]):
                delimiter = d
                break
        
        # Se encontrou delimitador, usa método CSV tradicional
        if delimiter:
            from io import StringIO
            import csv
            
            csv_data = StringIO(data.strip())
            reader = csv.reader(csv_data, delimiter=delimiter)
            rows = list(reader)
            
            if len(rows) > 0:
                headers = rows[0]
                data_rows = rows[1:] if len(rows) > 1 else []
                df = pd.DataFrame(data_rows, columns=headers)
                
                # Limpa dados
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.strip()
                        df[col] = df[col].replace('', np.nan)
                        df[col] = df[col].replace('nan', np.nan)
                
                return df
        
        # Se não há delimitadores, tenta detectar formato de "linhas alternadas"
        # Exemplo: linha 1 = cabeçalho 1, linha 2 = cabeçalho 2, linha 3 = valor 1, linha 4 = valor 2, etc.
        
        # Remove linhas vazias
        lines = [line.strip() for line in lines if line.strip()]
        
        if len(lines) < 2:
            return pd.DataFrame()
        
        # Tenta detectar padrão de repetição
        # Procura por um padrão onde as linhas se repetem em grupos
        possible_patterns = []
        
        # Testa padrões de 2 a 10 colunas
        for num_cols in range(2, min(11, len(lines) + 1)):
            if len(lines) % num_cols == 0:
                # Verifica se é um padrão válido
                num_rows = len(lines) // num_cols
                if num_rows >= 2:  # Pelo menos cabeçalho + 1 linha de dados
                    possible_patterns.append(num_cols)
        
        # Se encontrou padrões possíveis, usa o mais provável
        if possible_patterns:
            # Prefere padrões com menos colunas (mais comum)
            num_cols = min(possible_patterns)
            num_rows = len(lines) // num_cols
            
            # Reconstrói os dados
            headers = []
            data_rows = []
            
            # Primeira "linha" são os cabeçalhos
            for i in range(num_cols):
                headers.append(lines[i])
            
            # Demais "linhas" são os dados
            for row_idx in range(1, num_rows):
                row_data = []
                for col_idx in range(num_cols):
                    line_idx = row_idx * num_cols + col_idx
                    if line_idx < len(lines):
                        row_data.append(lines[line_idx])
                    else:
                        row_data.append('')
                data_rows.append(row_data)
            
            # Cria DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Limpa dados
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace('', np.nan)
                    df[col] = df[col].replace('nan', np.nan)
            
            return df
        
        # Se não conseguiu detectar padrão, tenta como uma única coluna
        df = pd.DataFrame({'Dados': lines})
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar dados colados: {str(e)}")
        # Fallback: cria DataFrame com uma coluna
        lines = data.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        if lines:
            df = pd.DataFrame({'Dados': lines})
            return df
        return pd.DataFrame()

    except Exception as e:
        # Fallback para o método antigo se houver erro
        lines = data.strip().split('\n')
        delimiters = [',', ';', '\t', '|']
        delimiter = ','
        for d in delimiters:
            if d in lines[0]:
                delimiter = d
                break
        
        rows = [line.split(delimiter) for line in lines]
        if len(rows) > 0:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            
            # Converte strings vazias e espaços em branco para NaN
            df = df.replace('', np.nan)
            df = df.replace(' ', np.nan)
            df = df.replace('  ', np.nan)
            
            # Remove espaços em branco das strings e converte vazias para NaN
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace('', np.nan)
                    df[col] = df[col].replace('nan', np.nan)
            
            return df
        return pd.DataFrame()

def save_project(project_name, datasets, description=""):
    """Salva projeto"""
    try:
        project_data = {
            'name': project_name,
            'datasets': datasets,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat()
        }
        
        if not os.path.exists('projects'):
            os.makedirs('projects')
        
        # Salva usando pickle
        with open(f'projects/{project_name}.pkl', 'wb') as f:
            pickle.dump(project_data, f)
        
        st.session_state.projects[project_name] = project_data
        return True
    except Exception as e:
        st.error(f"Erro ao salvar projeto: {str(e)}")
        return False

def load_project(project_name):
    """Carrega projeto"""
    try:
        filepath = f'projects/{project_name}.pkl'
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                project_data = pickle.load(f)
            return project_data
        else:
            st.error(f"Arquivo do projeto não encontrado: {filepath}")
            return None
    except Exception as e:
        st.error(f"Erro ao carregar projeto: {str(e)}")
        return None

def get_available_projects():
    """Retorna lista de projetos disponíveis"""
    if not os.path.exists('projects'):
        return []
    
    projects = []
    for filename in os.listdir('projects'):
        if filename.endswith('.pkl'):
            project_name = filename.replace('.pkl', '')
            projects.append(project_name)
    return projects

def get_numeric_columns(df):
    """Retorna colunas numéricas"""
    return df.select_dtypes(include=[np.number]).columns.tolist()

def get_categorical_columns(df):
    """Retorna colunas categóricas"""
    return df.select_dtypes(include=['object']).columns.tolist()

def auto_save_if_enabled(dataset_name):
    """Salva automaticamente o projeto se auto-save estiver habilitado e houver projeto ativo"""
    if st.session_state.auto_save_enabled and st.session_state.current_project:
        try:
            if save_project(
                st.session_state.current_project, 
                st.session_state.datasets,
                st.session_state.projects.get(st.session_state.current_project, {}).get('description', '')
            ):
                st.info(f"💾 Dataset '{dataset_name}' salvo automaticamente no projeto '{st.session_state.current_project}'")
                return True
            else:
                st.warning(f"⚠️ Falha no auto-save do dataset '{dataset_name}'")
                return False
        except Exception as e:
            st.error(f"❌ Erro no auto-save: {str(e)}")
            return False
    elif not st.session_state.auto_save_enabled and st.session_state.current_project:
        return "manual_save_needed"
    return None

def show_manual_save_button(dataset_name):
    """Mostra botão de salvamento manual quando necessário"""
    if st.session_state.current_project:
        if st.button(f"💾 Salvar '{dataset_name}' no Projeto", key=f"manual_save_{dataset_name}"):
            if save_project(
                st.session_state.current_project, 
                st.session_state.datasets,
                st.session_state.projects.get(st.session_state.current_project, {}).get('description', '')
            ):
                st.success(f"✅ Dataset '{dataset_name}' salvo no projeto '{st.session_state.current_project}'!")
            else:
                st.error("❌ Erro ao salvar projeto!")
    else:
        st.warning("⚠️ Crie um projeto primeiro para salvar os dados")

# Funções para Filtros Avançados
def analyze_text_column(series):
    """Analisa uma coluna de texto e identifica problemas comuns"""
    import re
    from collections import Counter
    
    problems = []
    suggestions = []
    stats = {}
    
    # Converter para string e remover NaN
    text_values = series.dropna().astype(str)
    
    if len(text_values) == 0:
        return problems, suggestions, stats
    
    # Estatísticas básicas
    stats['total_values'] = len(text_values)
    stats['unique_values'] = len(text_values.unique())
    stats['avg_length'] = text_values.str.len().mean()
    stats['max_length'] = text_values.str.len().max()
    stats['min_length'] = text_values.str.len().min()
    
    # 1. Espaços em branco no início/fim
    leading_trailing_spaces = text_values[text_values != text_values.str.strip()]
    if len(leading_trailing_spaces) > 0:
        problems.append(f"🔸 {len(leading_trailing_spaces)} valores com espaços no início/fim")
        suggestions.append({
            'type': 'trim_spaces',
            'description': 'Remover espaços no início e fim dos textos',
            'count': len(leading_trailing_spaces),
            'examples': leading_trailing_spaces.head(3).tolist()
        })
    
    # 2. Múltiplos espaços consecutivos
    multiple_spaces = text_values[text_values.str.contains(r'\s{2,}', regex=True, na=False)]
    if len(multiple_spaces) > 0:
        problems.append(f"🔸 {len(multiple_spaces)} valores com múltiplos espaços consecutivos")
        suggestions.append({
            'type': 'fix_multiple_spaces',
            'description': 'Substituir múltiplos espaços por um único espaço',
            'count': len(multiple_spaces),
            'examples': multiple_spaces.head(3).tolist()
        })
    
    # 3. Inconsistências de capitalização
    capitalization_variants = {}
    for value in text_values.unique():
        lower_value = value.lower()
        if lower_value not in capitalization_variants:
            capitalization_variants[lower_value] = []
        capitalization_variants[lower_value].append(value)
    
    inconsistent_caps = {k: v for k, v in capitalization_variants.items() if len(v) > 1}
    if inconsistent_caps:
        total_inconsistent = sum(len(variants) for variants in inconsistent_caps.values())
        problems.append(f"🔸 {len(inconsistent_caps)} grupos com inconsistências de capitalização")
        suggestions.append({
            'type': 'fix_capitalization',
            'description': 'Padronizar capitalização (primeira letra maiúscula)',
            'count': total_inconsistent,
            'examples': list(inconsistent_caps.values())[:3]
        })
    
    # 4. Palavras duplicadas consecutivas
    duplicate_words = text_values[text_values.str.contains(r'\b(\w+)\s+\1\b', regex=True, na=False, case=False)]
    if len(duplicate_words) > 0:
        problems.append(f"🔸 {len(duplicate_words)} valores com palavras duplicadas consecutivas")
        suggestions.append({
            'type': 'remove_duplicate_words',
            'description': 'Remover palavras duplicadas consecutivas',
            'count': len(duplicate_words),
            'examples': duplicate_words.head(3).tolist()
        })
    
    # 5. Caracteres especiais suspeitos
    special_chars = text_values[text_values.str.contains(r'[^\w\s\-.,!?()\[\]{}"\':;]', regex=True, na=False)]
    if len(special_chars) > 0:
        problems.append(f"🔸 {len(special_chars)} valores com caracteres especiais suspeitos")
        suggestions.append({
            'type': 'clean_special_chars',
            'description': 'Remover ou substituir caracteres especiais',
            'count': len(special_chars),
            'examples': special_chars.head(3).tolist()
        })
    
    # 6. Valores muito curtos ou muito longos (outliers)
    length_stats = text_values.str.len()
    q1, q3 = length_stats.quantile([0.25, 0.75])
    iqr = q3 - q1
    outlier_threshold_low = max(1, q1 - 1.5 * iqr)
    outlier_threshold_high = q3 + 1.5 * iqr
    
    length_outliers = text_values[(length_stats < outlier_threshold_low) | (length_stats > outlier_threshold_high)]
    if len(length_outliers) > 0:
        problems.append(f"🔸 {len(length_outliers)} valores com comprimento atípico")
        suggestions.append({
            'type': 'review_length_outliers',
            'description': 'Revisar valores com comprimento muito diferente da média',
            'count': len(length_outliers),
            'examples': length_outliers.head(3).tolist()
        })
    
    # 7. Possíveis abreviações inconsistentes
    abbreviations = text_values[text_values.str.contains(r'\b\w{1,3}\.', regex=True, na=False)]
    if len(abbreviations) > 0:
        problems.append(f"🔸 {len(abbreviations)} valores com possíveis abreviações")
        suggestions.append({
            'type': 'standardize_abbreviations',
            'description': 'Padronizar abreviações',
            'count': len(abbreviations),
            'examples': abbreviations.head(3).tolist()
        })
    
    return problems, suggestions, stats

def apply_text_corrections(series, correction_type):
    """Aplica correções específicas em uma série de texto"""
    import re
    
    corrected = series.copy()
    
    if correction_type == 'trim_spaces':
        corrected = corrected.str.strip()
    
    elif correction_type == 'fix_multiple_spaces':
        corrected = corrected.str.replace(r'\s+', ' ', regex=True)
    
    elif correction_type == 'fix_capitalization':
        corrected = corrected.str.title()
    
    elif correction_type == 'remove_duplicate_words':
        def remove_consecutive_duplicates(text):
            if pd.isna(text):
                return text
            words = str(text).split()
            result = []
            prev_word = None
            for word in words:
                if word.lower() != (prev_word or '').lower():
                    result.append(word)
                prev_word = word
            return ' '.join(result)
        
        corrected = corrected.apply(remove_consecutive_duplicates)
    
    elif correction_type == 'clean_special_chars':
        corrected = corrected.str.replace(r'[^\w\s\-.,!?()\[\]{}"\':;]', '', regex=True)
    
    elif correction_type == 'standardize_abbreviations':
        # Padronizar algumas abreviações comuns
        abbreviation_map = {
            r'\bdr\.': 'Dr.',
            r'\bsr\.': 'Sr.',
            r'\bsra\.': 'Sra.',
            r'\bltda\.': 'Ltda.',
            r'\bs\.a\.': 'S.A.',
        }
        for pattern, replacement in abbreviation_map.items():
            corrected = corrected.str.replace(pattern, replacement, regex=True, case=False)
    
    return corrected

def apply_text_filter(df, column, operation, value):
    """Aplica filtros de texto"""
    if operation == "Contém":
        return df[df[column].astype(str).str.contains(value, case=False, na=False)]
    elif operation == "Não contém":
        return df[~df[column].astype(str).str.contains(value, case=False, na=False)]
    elif operation == "Igual":
        return df[df[column].astype(str).str.lower() == value.lower()]
    elif operation == "Diferente":
        return df[df[column].astype(str).str.lower() != value.lower()]
    elif operation == "Começa com":
        return df[df[column].astype(str).str.startswith(value, na=False)]
    elif operation == "Termina com":
        return df[df[column].astype(str).str.endswith(value, na=False)]
    elif operation == "Regex":
        try:
            return df[df[column].astype(str).str.match(value, na=False)]
        except:
            st.error("Padrão regex inválido")
            return df
    return df

def apply_numeric_filter(df, column, operation, value):
    """Aplica filtros numéricos"""
    try:
        numeric_value = float(value)
        if operation == "Igual":
            return df[df[column] == numeric_value]
        elif operation == "Diferente":
            return df[df[column] != numeric_value]
        elif operation == "Maior que":
            return df[df[column] > numeric_value]
        elif operation == "Menor que":
            return df[df[column] < numeric_value]
        elif operation == "Maior ou igual":
            return df[df[column] >= numeric_value]
        elif operation == "Menor ou igual":
            return df[df[column] <= numeric_value]
    except ValueError:
        st.error("Valor numérico inválido")
    return df

def apply_null_filter(df, column, operation):
    """Aplica filtros para valores nulos"""
    if operation == "É nulo":
        return df[df[column].isnull()]
    elif operation == "Não é nulo":
        return df[df[column].notnull()]
    return df

def get_filter_preview(df, filters, logic_operator="E"):
    """Gera preview das linhas que serão removidas"""
    if not filters:
        return df, pd.DataFrame()
    
    # Inicializa máscara combinada
    combined_mask = None
    
    # Aplica cada filtro
    active_filters = [f for f in filters if f['active']]
    
    if not active_filters:
        return df, pd.DataFrame()
    
    for f in active_filters:
        col = f['column']
        op = f['operation']
        val = f['value']
        invert = f.get('invert', False)
        
        if f['type'] == 'Texto':
            if op == "Contém":
                mask = df[col].astype(str).str.contains(val, case=False, na=False)
            elif op == "Não contém":
                mask = ~df[col].astype(str).str.contains(val, case=False, na=False)
            elif op == "Igual":
                mask = df[col].astype(str).str.lower() == val.lower()
            elif op == "Diferente":
                mask = df[col].astype(str).str.lower() != val.lower()
            elif op == "Começa com":
                mask = df[col].astype(str).str.lower().str.startswith(val.lower())
            elif op == "Termina com":
                mask = df[col].astype(str).str.lower().str.endswith(val.lower())
            elif op == "Regex":
                try:
                    mask = df[col].astype(str).str.contains(val, regex=True, na=False)
                except:
                    st.error(f"Regex inválido: {val}")
                    continue
        
        elif f['type'] == 'Numérico':
            try:
                val_num = float(val)
                if op == "Igual":
                    mask = df[col] == val_num
                elif op == "Diferente":
                    mask = df[col] != val_num
                elif op == "Maior que":
                    mask = df[col] > val_num
                elif op == "Menor que":
                    mask = df[col] < val_num
                elif op == "Maior ou igual":
                    mask = df[col] >= val_num
                elif op == "Menor ou igual":
                    mask = df[col] <= val_num
            except ValueError:
                st.error(f"Valor numérico inválido: {val}")
                continue
        
        elif f['type'] == 'Nulo':
            if op == "É nulo":
                mask = df[col].isnull()
            elif op == "Não é nulo":
                mask = df[col].notnull()
        
        # Aplicar inversão se necessário
        if invert:
            mask = ~mask
        
        # Combinar com filtros anteriores
        if combined_mask is None:
            combined_mask = mask
        else:
            if logic_operator == "E":
                combined_mask = combined_mask & mask
            else:  # OU
                combined_mask = combined_mask | mask
    
    # Se não houver máscara válida, retorna o DataFrame original
    if combined_mask is None:
        return df, pd.DataFrame()
    
    # Aplica a máscara combinada
    result_df = df[combined_mask]
    lines_to_remove = df[~combined_mask]
    
    return result_df, lines_to_remove

def backup_dataset(dataset_name):
    """Cria backup do dataset antes da operação"""
    if 'dataset_backups' not in st.session_state:
        st.session_state.dataset_backups = {}
    
    if dataset_name in st.session_state.datasets:
        st.session_state.dataset_backups[dataset_name] = st.session_state.datasets[dataset_name].copy()
        return True
    return False

def restore_dataset(dataset_name):
    """Restaura dataset do backup"""
    if ('dataset_backups' in st.session_state and 
        dataset_name in st.session_state.dataset_backups):
        st.session_state.datasets[dataset_name] = st.session_state.dataset_backups[dataset_name].copy()
        return True
    return False

# Funções para Filtros Avançados
def apply_text_filter(df, column, operation, value):
    """Aplica filtros de texto"""
    if operation == "Contém":
        return df[df[column].astype(str).str.contains(value, case=False, na=False)]
    elif operation == "Não contém":
        return df[~df[column].astype(str).str.contains(value, case=False, na=False)]
    elif operation == "Igual":
        return df[df[column].astype(str).str.lower() == value.lower()]
    elif operation == "Diferente":
        return df[df[column].astype(str).str.lower() != value.lower()]
    elif operation == "Começa com":
        return df[df[column].astype(str).str.startswith(value, na=False)]
    elif operation == "Termina com":
        return df[df[column].astype(str).str.endswith(value, na=False)]
    elif operation == "Regex":
        try:
            return df[df[column].astype(str).str.match(value, na=False)]
        except:
            st.error("Padrão regex inválido")
            return df
    return df

def apply_numeric_filter(df, column, operation, value):
    """Aplica filtros numéricos"""
    try:
        numeric_value = float(value)
        if operation == "Igual":
            return df[df[column] == numeric_value]
        elif operation == "Diferente":
            return df[df[column] != numeric_value]
        elif operation == "Maior que":
            return df[df[column] > numeric_value]
        elif operation == "Menor que":
            return df[df[column] < numeric_value]
        elif operation == "Maior ou igual":
            return df[df[column] >= numeric_value]
        elif operation == "Menor ou igual":
            return df[df[column] <= numeric_value]
    except ValueError:
        st.error("Valor numérico inválido")
    return df

def apply_null_filter(df, column, operation):
    """Aplica filtros para valores nulos"""
    if operation == "É nulo":
        return df[df[column].isnull()]
    elif operation == "Não é nulo":
        return df[df[column].notnull()]
    return df

def get_filter_preview(df, filters, logic_operator="E"):
    """Gera preview das linhas que serão removidas"""
    if not filters:
        return df, pd.DataFrame()
    
    # Aplica todos os filtros
    filtered_dfs = []
    for filter_config in filters:
        if not filter_config['active']:
            continue
            
        column = filter_config['column']
        operation = filter_config['operation']
        value = filter_config['value']
        filter_type = filter_config['type']
        
        if filter_type == "Texto":
            filtered_df = apply_text_filter(df, column, operation, value)
        elif filter_type == "Numérico":
            filtered_df = apply_numeric_filter(df, column, operation, value)
        elif filter_type == "Nulo":
            filtered_df = apply_null_filter(df, column, operation)
        else:
            filtered_df = df
            
        filtered_dfs.append(filtered_df)
    
    if not filtered_dfs:
        return df, pd.DataFrame()
    
    # Combina os filtros com operador lógico
    if logic_operator == "E":
        # Intersecção - linhas que atendem TODOS os filtros
        result_df = filtered_dfs[0]
        for filtered_df in filtered_dfs[1:]:
            result_df = result_df[result_df.index.isin(filtered_df.index)]
    else:  # "OU"
        # União - linhas que atendem QUALQUER filtro
        all_indices = set()
        for filtered_df in filtered_dfs:
            all_indices.update(filtered_df.index)
        result_df = df.loc[list(all_indices)]
    
    # Linhas que serão removidas (invertido)
    lines_to_remove = df[~df.index.isin(result_df.index)]
    
    return result_df, lines_to_remove

def backup_dataset(dataset_name):
    """Cria backup do dataset antes da operação"""
    if 'dataset_backups' not in st.session_state:
        st.session_state.dataset_backups = {}
    
    if dataset_name in st.session_state.datasets:
        st.session_state.dataset_backups[dataset_name] = st.session_state.datasets[dataset_name].copy()
        return True
    return False

def restore_dataset(dataset_name):
    """Restaura dataset do backup"""
    if ('dataset_backups' in st.session_state and 
        dataset_name in st.session_state.dataset_backups):
        st.session_state.datasets[dataset_name] = st.session_state.dataset_backups[dataset_name].copy()
        return True
    return False

# Interface principal
st.title("📊 Análise de Dados Pro")
st.markdown("---")

# Sidebar
st.sidebar.title("🛠️ Ferramentas")

# Configurações
st.sidebar.subheader("⚙️ Configurações")

# Auto-save
st.session_state.auto_save_enabled = st.sidebar.checkbox(
    "🔄 Auto-save (salvar automaticamente ao importar dados)", 
    value=st.session_state.auto_save_enabled,
    help="Quando habilitado, os datasets serão salvos automaticamente no projeto ativo após serem importados"
)

if st.session_state.auto_save_enabled and not st.session_state.current_project:
    st.sidebar.warning("⚠️ Auto-save habilitado mas nenhum projeto ativo. Crie um projeto primeiro.")

st.sidebar.markdown("---")

# Seção de projetos
st.sidebar.subheader("📁 Projetos")

# Mostrar projeto atual
if st.session_state.current_project:
    st.sidebar.success(f"✅ Projeto Ativo: {st.session_state.current_project}")
    if st.sidebar.button("💾 Salvar Projeto Atual", key="save_current"):
        if save_project(
            st.session_state.current_project, 
            st.session_state.datasets,
            st.session_state.projects.get(st.session_state.current_project, {}).get('description', '')
        ):
            st.sidebar.success("Projeto salvo com sucesso!")
        else:
            st.sidebar.error("Erro ao salvar projeto!")
else:
    st.sidebar.info("Nenhum projeto ativo")

project_action = st.sidebar.selectbox(
    "Gerenciar Projetos",
    ["Selecionar Ação", "➕ Criar Novo", "📂 Carregar Existente", "📋 Listar Projetos"]
)

if project_action == "➕ Criar Novo":
    with st.sidebar.expander("Criar Novo Projeto", expanded=True):
        new_project_name = st.text_input("Nome do Projeto", key="new_project_name")
        project_description = st.text_area("Descrição (opcional)", key="project_desc")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Criar", key="create_project_btn"):
                if new_project_name.strip():
                    # Verifica se já existe
                    if new_project_name in get_available_projects():
                        st.error("❌ Projeto já existe!")
                    else:
                        st.session_state.current_project = new_project_name
                        project_data = {
                            'name': new_project_name,
                            'description': project_description,
                            'datasets': st.session_state.datasets.copy(),
                            'created_at': datetime.now().isoformat()
                        }
                        st.session_state.projects[new_project_name] = project_data
                        
                        # Salva automaticamente
                        if save_project(new_project_name, st.session_state.datasets, project_description):
                            st.success(f"✅ Projeto '{new_project_name}' criado e salvo!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao salvar projeto!")
                else:
                    st.error("❌ Digite um nome para o projeto!")
        
        with col2:
            if st.button("🚮 Limpar", key="clear_project_form"):
                st.rerun()

elif project_action == "📂 Carregar Existente":
    with st.sidebar.expander("Carregar Projeto", expanded=True):
        available_projects = get_available_projects()
        
        if available_projects:
            selected_project = st.selectbox(
                "Projetos Disponíveis", 
                ["Selecione..."] + available_projects,
                key="load_project_select"
            )
            
            if selected_project != "Selecione...":
                # Mostra informações do projeto
                try:
                    project_info = load_project(selected_project)
                    if project_info:
                        st.info(f"📅 Criado: {project_info.get('created_at', 'N/A')[:10]}")
                        st.info(f"📊 Datasets: {len(project_info.get('datasets', {}))}")
                        if project_info.get('description'):
                            st.info(f"📝 Descrição: {project_info['description']}")
                except:
                    st.warning("⚠️ Erro ao ler informações do projeto")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📂 Carregar", key="load_project_btn"):
                        project_data = load_project(selected_project)
                        if project_data:
                            st.session_state.current_project = selected_project
                            st.session_state.datasets = project_data.get('datasets', {})
                            st.session_state.projects[selected_project] = project_data
                            st.success(f"✅ Projeto '{selected_project}' carregado!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao carregar projeto!")
                
                with col2:
                    if st.button("🗑️ Deletar", key="delete_project_btn"):
                        try:
                            os.remove(f'projects/{selected_project}.pkl')
                            if selected_project in st.session_state.projects:
                                del st.session_state.projects[selected_project]
                            if st.session_state.current_project == selected_project:
                                st.session_state.current_project = None
                            st.success(f"✅ Projeto '{selected_project}' deletado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao deletar: {str(e)}")
        else:
            st.info("📭 Nenhum projeto salvo encontrado")
            st.info("💡 Crie um novo projeto primeiro!")

elif project_action == "📋 Listar Projetos":
    with st.sidebar.expander("Todos os Projetos", expanded=True):
        available_projects = get_available_projects()
        
        if available_projects:
            st.write(f"**📊 Total: {len(available_projects)} projetos**")
            
            for project in available_projects:
                with st.container():
                    st.write(f"**📁 {project}**")
                    try:
                        project_info = load_project(project)
                        if project_info:
                            datasets_count = len(project_info.get('datasets', {}))
                            created_date = project_info.get('created_at', 'N/A')[:10]
                            st.caption(f"📅 {created_date} | 📊 {datasets_count} datasets")
                        else:
                            st.caption("⚠️ Erro ao ler projeto")
                    except:
                        st.caption("⚠️ Projeto corrompido")
                    st.markdown("---")
        else:
            st.info("📭 Nenhum projeto encontrado")

# Abas principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Import de Dados", 
    "🧹 Data Cleaning", 
    "🔍 Filtrar Dados",
    "🔗 Relacionamentos", 
    "📈 Análises"
])

# TAB 1: Import de Dados
with tab1:
    st.header("Importar Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload de Arquivos")
        uploaded_files = st.file_uploader(
            "Escolha os arquivos",
            type=['csv', 'txt', 'xlsx'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for file in uploaded_files:
                dataset_name = st.text_input(f"Nome para {file.name}", value=file.name.split('.')[0])
                
                if st.button(f"Processar {file.name}"):
                    try:
                        if file.name.endswith('.csv'):
                            df = load_csv_file(file)
                        elif file.name.endswith('.txt'):
                            df = load_txt_file(file)
                        elif file.name.endswith('.xlsx'):
                            df = load_excel_file(file)
                        
                        st.session_state.datasets[dataset_name] = df
                        st.success(f"Dataset '{dataset_name}' carregado com sucesso!")
                        st.dataframe(df.head())
                        
                        # Auto-save se habilitado
                        auto_save_result = auto_save_if_enabled(dataset_name)
                        if auto_save_result is False:
                            st.info("💡 Você pode salvar manualmente clicando em 'Salvar Projeto Atual' na sidebar")
                        elif auto_save_result == "manual_save_needed":
                            st.info("💡 Auto-save desabilitado. Use o botão abaixo para salvar:")
                            show_manual_save_button(dataset_name)
                        
                    except Exception as e:
                        st.error(f"Erro ao processar arquivo: {str(e)}")
    
    with col2:
        st.subheader("Colar Dados")
        pasted_data = st.text_area("Cole seus dados aqui (CSV, TSV, etc.)", height=200)
        dataset_name_paste = st.text_input("Nome do dataset")
        
        if st.button("Processar Dados Colados"):
            if pasted_data and dataset_name_paste:
                try:
                    df = parse_pasted_data(pasted_data)
                    st.session_state.datasets[dataset_name_paste] = df
                    st.success(f"Dataset '{dataset_name_paste}' criado!")
                    st.dataframe(df.head())
                    
                    # Auto-save se habilitado
                    auto_save_result = auto_save_if_enabled(dataset_name_paste)
                    if auto_save_result is False:
                        st.info("💡 Você pode salvar manualmente clicando em 'Salvar Projeto Atual' na sidebar")
                    elif auto_save_result == "manual_save_needed":
                        st.info("💡 Auto-save desabilitado. Use o botão abaixo para salvar:")
                        show_manual_save_button(dataset_name_paste)
                    
                except Exception as e:
                    st.error(f"Erro ao processar dados: {str(e)}")

# TAB 2: Data Cleaning
with tab2:
    st.header("Limpeza e Transformação de Dados")
    
    if not st.session_state.datasets:
        st.warning("Importe dados primeiro na aba 'Import de Dados'")
    else:
        dataset_names = list(st.session_state.datasets.keys())
        selected_dataset = st.selectbox("Selecione o dataset", dataset_names)
        
        if selected_dataset:
            df = st.session_state.datasets[selected_dataset].copy()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Informações do Dataset")
                st.write(f"Linhas: {df.shape[0]}")
                st.write(f"Colunas: {df.shape[1]}")
                
                # Informações detalhadas sobre nulos
                null_info = pd.DataFrame({
                    'Coluna': df.columns,
                    'Tipo': df.dtypes,
                    'Nulos': df.isnull().sum(),
                    '% Nulos': (df.isnull().sum() / len(df) * 100).round(2)
                })
                st.write("**Informações por Coluna:**")
                st.dataframe(null_info)
                
                # Mostrar alguns valores únicos para identificar possíveis valores vazios não detectados
                st.write("**Valores Únicos Suspeitos:**")
                for col in df.columns:
                    if df[col].dtype == 'object':
                        unique_vals = df[col].unique()
                        # Filtra valores que podem ser vazios ou suspeitos
                        suspicious = [str(v) for v in unique_vals if str(v).strip() in ['', ' ', 'nan', 'None', 'NULL', '-'] or len(str(v).strip()) <= 1]
                        if suspicious:
                            st.write(f"*{col}*: {suspicious}")
            
            with col2:
                st.subheader("Operações")
                
                # Nova seção: Análise Inteligente de Colunas
                st.markdown("---")
                st.write("**🔍 Análise Inteligente de Colunas**")
                
                # Seletor de coluna para análise
                text_columns = [col for col in df.columns if df[col].dtype == 'object']
                if text_columns:
                    analysis_column = st.selectbox(
                        "Selecione uma coluna de texto para análise:",
                        text_columns,
                        key="analysis_column"
                    )
                    
                    if st.button("🔍 Analisar Coluna", key="analyze_column"):
                        with st.spinner("Analisando coluna..."):
                            problems, suggestions, stats = analyze_text_column(df[analysis_column])
                            
                            # Armazenar resultados no session state
                            st.session_state.analysis_results = {
                                'column': analysis_column,
                                'problems': problems,
                                'suggestions': suggestions,
                                'stats': stats
                            }
                    
                    # Mostrar resultados da análise
                    if hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
                        results = st.session_state.analysis_results
                        
                        if results['column'] == analysis_column:
                            st.markdown("---")
                            st.write(f"**📊 Resultados da Análise - Coluna '{analysis_column}'**")
                            
                            # Estatísticas
                            col_stats1, col_stats2 = st.columns(2)
                            with col_stats1:
                                st.metric("Total de Valores", results['stats'].get('total_values', 0))
                                st.metric("Valores Únicos", results['stats'].get('unique_values', 0))
                            with col_stats2:
                                st.metric("Comprimento Médio", f"{results['stats'].get('avg_length', 0):.1f}")
                                st.metric("Comprimento Máximo", results['stats'].get('max_length', 0))
                            
                            # Problemas encontrados
                            if results['problems']:
                                st.write("**⚠️ Problemas Detectados:**")
                                for problem in results['problems']:
                                    st.write(problem)
                                
                                st.write("**🛠️ Correções Sugeridas:**")
                                
                                # Interface para aplicar correções
                                for i, suggestion in enumerate(results['suggestions']):
                                    with st.expander(f"✨ {suggestion['description']} ({suggestion['count']} valores)"):
                                        st.write("**Exemplos:**")
                                        for example in suggestion['examples'][:3]:
                                            if isinstance(example, list):
                                                st.write(f"• Variações: {', '.join(map(str, example))}")
                                            else:
                                                st.write(f"• `{example}`")
                                        
                                        col_preview, col_apply = st.columns([2, 1])
                                        
                                        with col_preview:
                                            if st.button(f"👁️ Preview", key=f"preview_{i}"):
                                                # Mostrar preview da correção
                                                corrected_series = apply_text_corrections(
                                                    df[analysis_column], 
                                                    suggestion['type']
                                                )
                                                
                                                # Mostrar apenas valores que mudaram
                                                changed_mask = df[analysis_column] != corrected_series
                                                if changed_mask.any():
                                                    preview_df = pd.DataFrame({
                                                        'Original': df[analysis_column][changed_mask],
                                                        'Corrigido': corrected_series[changed_mask]
                                                    }).head(10)
                                                    st.dataframe(preview_df)
                                                else:
                                                    st.info("Nenhuma alteração seria feita.")
                                        
                                        with col_apply:
                                            if st.button(f"✅ Aplicar", key=f"apply_{i}"):
                                                # Aplicar correção
                                                corrected_series = apply_text_corrections(
                                                    df[analysis_column], 
                                                    suggestion['type']
                                                )
                                                
                                                # Backup antes da alteração
                                                backup_dataset(selected_dataset)
                                                
                                                # Aplicar correção
                                                st.session_state.datasets[selected_dataset][analysis_column] = corrected_series
                                                
                                                # Auto-save se habilitado
                                                auto_save_if_enabled(selected_dataset)
                                                
                                                st.success(f"✅ Correção '{suggestion['description']}' aplicada!")
                                                
                                                # Limpar resultados para nova análise
                                                del st.session_state.analysis_results
                                                st.rerun()
                                
                                # Botão para aplicar todas as correções
                                st.markdown("---")
                                if st.button("🚀 Aplicar Todas as Correções", key="apply_all_corrections"):
                                    # Backup antes das alterações
                                    backup_dataset(selected_dataset)
                                    
                                    corrected_series = df[analysis_column].copy()
                                    corrections_applied = []
                                    
                                    # Aplicar todas as correções em sequência
                                    for suggestion in results['suggestions']:
                                        corrected_series = apply_text_corrections(
                                            corrected_series, 
                                            suggestion['type']
                                        )
                                        corrections_applied.append(suggestion['description'])
                                    
                                    # Aplicar ao dataset
                                    st.session_state.datasets[selected_dataset][analysis_column] = corrected_series
                                    
                                    # Auto-save se habilitado
                                    auto_save_if_enabled(selected_dataset)
                                    
                                    st.success(f"✅ {len(corrections_applied)} correções aplicadas!")
                                    st.write("**Correções aplicadas:**")
                                    for correction in corrections_applied:
                                        st.write(f"• {correction}")
                                    
                                    # Limpar resultados
                                    del st.session_state.analysis_results
                                    st.rerun()
                            else:
                                st.success("✅ Nenhum problema detectado nesta coluna!")
                else:
                    st.info("📝 Nenhuma coluna de texto encontrada para análise.")
                
                st.markdown("---")
                
                # Botão para re-limpar dados
                if st.button("🧹 Re-limpar Dados (Converter vazios em NaN)"):
                    df = clean_empty_values(df)
                    st.session_state.datasets[selected_dataset] = df
                    st.success("Dados re-limpos! Valores vazios convertidos para NaN.")
                    st.rerun()
                
                st.markdown("---")
                
                # Remover colunas
                st.write("**Remover Colunas**")
                cols_to_remove = st.multiselect("Selecione colunas para remover", df.columns)
                if st.button("Remover Colunas Selecionadas"):
                    df = df.drop(columns=cols_to_remove)
                    st.session_state.datasets[selected_dataset] = df
                    st.success("Colunas removidas!")
                    st.rerun()
                
                st.markdown("---")
                
                # Tratar valores nulos
                st.write("**Tratamento de Nulos**")
                null_action = st.selectbox("Ação para valores nulos", 
                                         ["Selecionar", "Remover linhas", "Preencher com média", "Preencher com mediana", "Preencher com valor", "Preencher com valor mais frequente"])
                
                if null_action != "Selecionar":
                    # Mostrar apenas colunas que têm valores nulos
                    cols_with_nulls = [col for col in df.columns if df[col].isnull().sum() > 0]
                    if cols_with_nulls:
                        target_col = st.selectbox("Coluna alvo (apenas com nulos)", cols_with_nulls)
                        
                        # Mostrar quantos nulos existem na coluna selecionada
                        null_count = df[target_col].isnull().sum()
                        st.info(f"Coluna '{target_col}' tem {null_count} valores nulos ({(null_count/len(df)*100):.1f}%)")
                        
                        if null_action == "Preencher com valor":
                            fill_value = st.text_input("Valor para preencher")
                        
                        if st.button("Aplicar Tratamento"):
                            if null_action == "Remover linhas":
                                initial_rows = len(df)
                                df = df.dropna(subset=[target_col])
                                removed_rows = initial_rows - len(df)
                                st.success(f"Removidas {removed_rows} linhas com valores nulos!")
                            elif null_action == "Preencher com média":
                                if pd.api.types.is_numeric_dtype(df[target_col]):
                                    mean_val = df[target_col].mean()
                                    df[target_col].fillna(mean_val, inplace=True)
                                    st.success(f"Valores nulos preenchidos com a média: {mean_val:.2f}")
                                else:
                                    st.error("Coluna não é numérica. Use outro método.")
                            elif null_action == "Preencher com mediana":
                                if pd.api.types.is_numeric_dtype(df[target_col]):
                                    median_val = df[target_col].median()
                                    df[target_col].fillna(median_val, inplace=True)
                                    st.success(f"Valores nulos preenchidos com a mediana: {median_val:.2f}")
                                else:
                                    st.error("Coluna não é numérica. Use outro método.")
                            elif null_action == "Preencher com valor":
                                if fill_value:
                                    df[target_col].fillna(fill_value, inplace=True)
                                    st.success(f"Valores nulos preenchidos com: '{fill_value}'")
                                else:
                                    st.error("Digite um valor para preencher")
                            elif null_action == "Preencher com valor mais frequente":
                                mode_val = df[target_col].mode()
                                if not mode_val.empty:
                                    mode_val = mode_val.iloc[0]
                                    df[target_col].fillna(mode_val, inplace=True)
                                    st.success(f"Valores nulos preenchidos com o valor mais frequente: '{mode_val}'")
                                else:
                                    st.error("Não foi possível determinar o valor mais frequente")
                            
                            st.session_state.datasets[selected_dataset] = df
                            st.rerun()
                    else:
                        st.info("Nenhuma coluna com valores nulos encontrada!")
            
            # Criar colunas calculadas
            st.subheader("Criar Colunas Calculadas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_col_name = st.text_input("Nome da nova coluna")
            
            with col2:
                calc_type = st.selectbox("Tipo de cálculo", 
                                       ["Soma", "Subtração", "Multiplicação", "Divisão", "Concatenação", "Personalizado"])
            
            with col3:
                if calc_type in ["Soma", "Subtração", "Multiplicação", "Divisão"]:
                    numeric_cols = get_numeric_columns(df)
                    col1_calc = st.selectbox("Primeira coluna", numeric_cols, key="col1_calc")
                    col2_calc = st.selectbox("Segunda coluna", numeric_cols, key="col2_calc")
                elif calc_type == "Concatenação":
                    cat_cols = get_categorical_columns(df)
                    col1_calc = st.selectbox("Primeira coluna", cat_cols, key="col1_calc")
                    col2_calc = st.selectbox("Segunda coluna", cat_cols, key="col2_calc")
                    separator = st.text_input("Separador", value=" ")
                elif calc_type == "Personalizado":
                    custom_formula = st.text_area("Fórmula Python (use df['coluna'])", 
                                                height=100,
                                                value="df['coluna1'] * 2 + df['coluna2']")
            
            if st.button("Criar Coluna"):
                try:
                    if calc_type == "Soma":
                        df[new_col_name] = df[col1_calc] + df[col2_calc]
                    elif calc_type == "Subtração":
                        df[new_col_name] = df[col1_calc] - df[col2_calc]
                    elif calc_type == "Multiplicação":
                        df[new_col_name] = df[col1_calc] * df[col2_calc]
                    elif calc_type == "Divisão":
                        df[new_col_name] = df[col1_calc] / df[col2_calc]
                    elif calc_type == "Concatenação":
                        df[new_col_name] = df[col1_calc].astype(str) + separator + df[col2_calc].astype(str)
                    elif calc_type == "Personalizado":
                        df[new_col_name] = eval(custom_formula)
                    
                    st.session_state.datasets[selected_dataset] = df
                    st.success(f"Coluna '{new_col_name}' criada!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Erro ao criar coluna: {str(e)}")
            
            # Visualizar dados atualizados
            st.subheader("Dados Atualizados")
            st.dataframe(df)

# TAB 3: Filtrar Dados
with tab3:
    st.header("🔍 Filtrar e Remover Dados")
    
    if not st.session_state.datasets:
        st.warning("Importe dados primeiro na aba 'Import de Dados'")
    else:
        dataset_names = list(st.session_state.datasets.keys())
        selected_dataset = st.selectbox("Selecione o dataset para filtrar", dataset_names, key="filter_dataset")
        
        if selected_dataset:
            df = st.session_state.datasets[selected_dataset].copy()
            
            # Inicializar filtros no session_state
            if 'active_filters' not in st.session_state:
                st.session_state.active_filters = []
            
            st.subheader("⚙️ Configurar Filtros")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Interface para adicionar filtros
                with st.expander("➕ Adicionar Novo Filtro", expanded=True):
                    new_col1, new_col2, new_col3 = st.columns(3)
                    
                    with new_col1:
                        filter_column = st.selectbox(
                            "Coluna", 
                            df.columns.tolist(), 
                            key="new_filter_column"
                        )
                    
                    with new_col2:
                        # Detectar tipo da coluna
                        if pd.api.types.is_numeric_dtype(df[filter_column]):
                            filter_type = st.selectbox(
                                "Tipo de Filtro", 
                                ["Numérico", "Texto", "Nulo"], 
                                key="new_filter_type"
                            )
                        else:
                            filter_type = st.selectbox(
                                "Tipo de Filtro", 
                                ["Texto", "Nulo"], 
                                key="new_filter_type"
                            )
                    
                    with new_col3:
                        # Checkbox para inverter condição (NOT)
                        invert_condition = st.checkbox(
                            "🔄 NOT (Inverter condição)", 
                            key="new_filter_not",
                            help="Marca esta opção para inverter a condição do filtro"
                        )
                        
                        if filter_type == "Texto":
                            operations = ["Contém", "Não contém", "Igual", "Diferente", "Começa com", "Termina com", "Regex"]
                        elif filter_type == "Numérico":
                            operations = ["Igual", "Diferente", "Maior que", "Menor que", "Maior ou igual", "Menor ou igual"]
                        else:  # Nulo
                            operations = ["É nulo", "Não é nulo"]
                        
                        filter_operation = st.selectbox(
                            "Operação", 
                            operations, 
                            key="new_filter_operation"
                        )
                        
                        # Mostrar preview da condição
                        if invert_condition:
                            st.caption(f"🔄 NOT {filter_operation}")
                    
                    # Campo de valor (se necessário)
                    if filter_type != "Nulo":
                        if filter_type == "Numérico":
                            filter_value = st.number_input(
                                "Valor", 
                                value=0.0, 
                                key="new_filter_value"
                            )
                        else:
                            filter_value = st.text_input(
                                "Valor", 
                                key="new_filter_value"
                            )
                    else:
                        filter_value = ""
                    
                    if st.button("➕ Adicionar Filtro"):
                        new_filter = {
                            'id': len(st.session_state.active_filters),
                            'column': filter_column,
                            'type': filter_type,
                            'operation': filter_operation,
                            'value': str(filter_value),
                            'active': True,
                            'invert': invert_condition  # Nova propriedade
                        }
                        st.session_state.active_filters.append(new_filter)
                        st.rerun()
                
                # Mostrar filtros ativos
                if st.session_state.active_filters:
                    st.subheader("🔧 Filtros Ativos")
                    
                    # Operador lógico
                    logic_operator = st.radio(
                        "Combinar filtros com:", 
                        ["E", "OU"], 
                        horizontal=True,
                        help="E: Remove linhas que atendem TODOS os filtros\nOU: Remove linhas que atendem QUALQUER filtro"
                    )
                    
                    # Lista de filtros
                    for i, filter_config in enumerate(st.session_state.active_filters):
                        with st.container():
                            filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
                            
                            with filter_col1:
                                filter_desc = f"{filter_config['column']} {filter_config['operation']}"
                                if filter_config['value']:
                                    filter_desc += f" '{filter_config['value']}'"
                                
                                st.session_state.active_filters[i]['active'] = st.checkbox(
                                    filter_desc, 
                                    value=filter_config['active'],
                                    key=f"filter_active_{i}"
                                )
                            
                            with filter_col2:
                                if st.button("🗑️", key=f"delete_filter_{i}", help="Remover filtro"):
                                    st.session_state.active_filters.pop(i)
                                    st.rerun()
                            
                            with filter_col3:
                                # Mostrar preview do filtro individual
                                if st.button("👁️", key=f"preview_filter_{i}", help="Preview deste filtro"):
                                    single_filter_result, _ = get_filter_preview(df, [filter_config])
                                    st.info(f"Este filtro manteria {len(single_filter_result)} linhas")
                    
                    st.markdown("---")
            
            with col2:
                st.subheader("📊 Informações")
                st.metric("Total de Linhas", len(df))
                
                if st.session_state.active_filters:
                    # Calcular preview
                    active_filters = [f for f in st.session_state.active_filters if f['active']]
                    if active_filters:
                        remaining_df, to_remove_df = get_filter_preview(df, active_filters, logic_operator)
                        
                        st.metric("Linhas que Permanecerão", len(remaining_df))
                        st.metric("Linhas a Remover", len(to_remove_df))
                        
                        if len(to_remove_df) > 0:
                            removal_percentage = (len(to_remove_df) / len(df)) * 100
                            st.metric("% a Remover", f"{removal_percentage:.1f}%")
                            
                            # Preview das linhas a remover
                            if st.checkbox("👁️ Mostrar Preview das Linhas a Remover"):
                                st.subheader("🔍 Preview - Linhas que serão Removidas")
                                st.dataframe(to_remove_df.head(10))
                                if len(to_remove_df) > 10:
                                    st.info(f"Mostrando 10 de {len(to_remove_df)} linhas que serão removidas")
                            
                            # Botões de ação
                            st.markdown("---")
                            
                            col_backup, col_remove = st.columns(2)
                            
                            with col_backup:
                                if st.button("💾 Criar Backup", help="Criar backup antes de remover"):
                                    if backup_dataset(selected_dataset):
                                        st.success("✅ Backup criado!")
                                    else:
                                        st.error("❌ Erro ao criar backup")
                            
                            with col_remove:
                                if st.button("🗑️ Remover Linhas", type="primary"):
                                    # Criar backup automático
                                    backup_dataset(selected_dataset)
                                    
                                    # Aplicar filtros e remover linhas
                                    st.session_state.datasets[selected_dataset] = remaining_df
                                    
                                    # Auto-save se habilitado
                                    auto_save_result = auto_save_if_enabled(selected_dataset)
                                    
                                    st.success(f"✅ {len(to_remove_df)} linhas removidas com sucesso!")
                                    
                                    # Limpar filtros após aplicação
                                    st.session_state.active_filters = []
                                    st.rerun()
                            
                            # Botão de desfazer
                            if ('dataset_backups' in st.session_state and 
                                selected_dataset in st.session_state.dataset_backups):
                                if st.button("↩️ Desfazer Última Operação"):
                                    if restore_dataset(selected_dataset):
                                        st.success("✅ Operação desfeita!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao desfazer operação")
                        else:
                            st.info("ℹ️ Nenhuma linha será removida com os filtros atuais")
                    else:
                        st.info("ℹ️ Ative pelo menos um filtro para ver o preview")
                
                # Limpeza rápida
                st.markdown("---")
                st.subheader("🧹 Limpeza Rápida")
                
                if st.button("🗑️ Remover Linhas Duplicadas"):
                    backup_dataset(selected_dataset)
                    original_len = len(df)
                    df_no_duplicates = df.drop_duplicates()
                    st.session_state.datasets[selected_dataset] = df_no_duplicates
                    removed = original_len - len(df_no_duplicates)
                    st.success(f"✅ {removed} linhas duplicadas removidas!")
                    auto_save_if_enabled(selected_dataset)
                    st.rerun()
                
                if st.button("🗑️ Remover Linhas Completamente Vazias"):
                    backup_dataset(selected_dataset)
                    original_len = len(df)
                    df_no_empty = df.dropna(how='all')
                    st.session_state.datasets[selected_dataset] = df_no_empty
                    removed = original_len - len(df_no_empty)
                    st.success(f"✅ {removed} linhas vazias removidas!")
                    auto_save_if_enabled(selected_dataset)
                    st.rerun()

# TAB 4: Relacionamentos
with tab4:
    st.header("🔗 Relacionamentos entre Tabelas")

    if len(st.session_state.datasets) < 2:
        st.warning("⚠️ Você precisa de pelo menos 2 datasets para criar relacionamentos")
        st.info("💡 Importe mais dados na aba 'Import de Dados' primeiro")
    else:
        st.subheader("Configurar Relacionamento")
        
        dataset_names = list(st.session_state.datasets.keys())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Tabela Principal (Esquerda)**")
            left_dataset = st.selectbox("Selecione a tabela principal", dataset_names, key="left_ds")
            
            if left_dataset:
                left_df = st.session_state.datasets[left_dataset]
                left_columns = list(left_df.columns)
                left_key = st.selectbox("Campo chave da tabela principal", left_columns, key="left_key")
                
                # Preview da tabela principal
                st.markdown(f"**Preview de {left_dataset}:**")
                st.dataframe(left_df.head(3), use_container_width=True)
        
        with col2:
            st.markdown("**📋 Tabela Secundária (Direita)**")
            right_dataset_options = [ds for ds in dataset_names if ds != left_dataset]
            right_dataset = st.selectbox("Selecione a tabela secundária", right_dataset_options, key="right_ds")
            
            if right_dataset:
                right_df = st.session_state.datasets[right_dataset]
                right_columns = list(right_df.columns)
                right_key = st.selectbox("Campo chave da tabela secundária", right_columns, key="right_key")
                
                # Preview da tabela secundária
                st.markdown(f"**Preview de {right_dataset}:**")
                st.dataframe(right_df.head(3), use_container_width=True)
        
        # Configurações do relacionamento
        st.markdown("---")
        st.subheader("⚙️ Configurações do Relacionamento")
        
        col3, col4 = st.columns(2)
        
        with col3:
            join_type = st.selectbox(
                "Tipo de Relacionamento",
                ["Inner Join", "Left Join", "Right Join", "Outer Join"],
                help="Inner: apenas registros que existem em ambas as tabelas\n"
                     "Left: todos os registros da tabela principal\n"
                     "Right: todos os registros da tabela secundária\n"
                     "Outer: todos os registros de ambas as tabelas"
            )
        
        with col4:
            result_name = st.text_input(
                "Nome do resultado",
                value=f"{left_dataset}_relacionado_{right_dataset}" if 'left_dataset' in locals() and 'right_dataset' in locals() else "",
                help="Nome para salvar a tabela resultante do relacionamento"
            )
        
        # Botão para executar o relacionamento
        if st.button("🔗 Executar Relacionamento", type="primary"):
            if left_dataset and right_dataset and left_key and right_key and result_name:
                try:
                    # Mapear tipos de join
                    join_mapping = {
                        "Inner Join": "inner",
                        "Left Join": "left", 
                        "Right Join": "right",
                        "Outer Join": "outer"
                    }
                    
                    # Executar o relacionamento
                    left_df = st.session_state.datasets[left_dataset]
                    right_df = st.session_state.datasets[right_dataset]
                    
                    # Verificar se as chaves existem
                    if left_key not in left_df.columns:
                        st.error(f"❌ Campo '{left_key}' não encontrado em {left_dataset}")
                    elif right_key not in right_df.columns:
                        st.error(f"❌ Campo '{right_key}' não encontrado em {right_dataset}")
                    else:
                        # Realizar o merge
                        result_df = pd.merge(
                            left_df, 
                            right_df, 
                            left_on=left_key, 
                            right_on=right_key, 
                            how=join_mapping[join_type],
                            suffixes=('_principal', '_secundaria')
                        )
                        
                        # Salvar resultado
                        st.session_state.datasets[result_name] = result_df
                        
                        # Mostrar resultado
                        st.success(f"✅ Relacionamento criado com sucesso!")
                        st.info(f"📊 Resultado: {len(result_df)} registros na tabela '{result_name}'")
                        
                        # Auto-save se habilitado
                        auto_save_if_enabled(result_name)
                        
                        # Preview do resultado
                        st.subheader(f"📋 Preview do Resultado: {result_name}")
                        st.dataframe(result_df.head(10), use_container_width=True)
                        
                        # Estatísticas do relacionamento
                        col5, col6, col7 = st.columns(3)
                        with col5:
                            st.metric("Registros Resultantes", len(result_df))
                        with col6:
                            st.metric("Colunas Totais", len(result_df.columns))
                        with col7:
                            matches = len(result_df.dropna())
                            st.metric("Correspondências", matches)
                        
                except Exception as e:
                    st.error(f"❌ Erro ao executar relacionamento: {str(e)}")
            else:
                st.error("❌ Preencha todos os campos obrigatórios")
        
        # Seção de ajuda
        with st.expander("❓ Ajuda - Como usar Relacionamentos"):
            st.markdown("""
            ### 🎯 Como Relacionar Tabelas
            
            1. **Selecione duas tabelas** que você deseja relacionar
            2. **Escolha os campos chave** que serão usados para fazer a correspondência
            3. **Defina o tipo de relacionamento:**
               - **Inner Join**: Apenas registros que existem em ambas as tabelas
               - **Left Join**: Todos os registros da tabela principal + correspondências da secundária
               - **Right Join**: Todos os registros da tabela secundária + correspondências da principal
               - **Outer Join**: Todos os registros de ambas as tabelas
            4. **Nomeie o resultado** e clique em "Executar Relacionamento"
            
            ### 💡 Dicas Importantes
            
            - Os **campos chave devem ter valores compatíveis** (mesmo tipo de dados)
            - **Valores duplicados** nas chaves podem gerar múltiplas correspondências
            - **Colunas com nomes iguais** receberão sufixos '_principal' e '_secundaria'
            - O **resultado é salvo automaticamente** como um novo dataset
            
            ### 🔍 Exemplo Prático
            
            **Tabela Clientes:** ID, Nome, Email  
            **Tabela Pedidos:** PedidoID, ClienteID, Valor  
            **Relacionamento:** Clientes.ID = Pedidos.ClienteID  
            **Resultado:** Dados completos de clientes com seus pedidos
            """)

# TAB 5: Gerenciar Dados
with tab5:
    st.header("Gerenciar Dados e Projetos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Datasets Carregados")
        
        # Informações de debug
        total_datasets = len(st.session_state.datasets)
        if total_datasets > 0:
            st.info(f"📈 **{total_datasets} dataset(s) carregado(s)**")
        
        if st.session_state.datasets:
            # Ordenar datasets por nome para consistência
            sorted_datasets = sorted(st.session_state.datasets.items())
            
            for i, (name, df) in enumerate(sorted_datasets):
                with st.expander(f"📊 {name} ({df.shape[0]} linhas, {df.shape[1]} colunas)", expanded=False):
                    # Informações do dataset
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**📏 Dimensões:** {df.shape[0]} × {df.shape[1]}")
                        st.write(f"**💾 Memória:** {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                    
                    with col_info2:
                        st.write(f"**📋 Colunas:** {', '.join(df.columns[:3])}{'...' if len(df.columns) > 3 else ''}")
                        st.write(f"**🔢 Tipos:** {len(df.select_dtypes(include=['number']).columns)} numérica(s), {len(df.select_dtypes(include=['object']).columns)} texto")
                    
                    # Prévia dos dados
                    st.write("**👀 Prévia dos dados:**")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Botões de ação
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button(f"👁️ Ver Completo", key=f"view_full_{i}_{name}"):
                            st.session_state[f'show_table_{name}'] = True
                            st.rerun()
                    
                    with col_b:
                        if st.button(f"✏️ Renomear", key=f"rename_{i}_{name}"):
                            st.session_state[f'renaming_{name}'] = True
                            st.rerun()
                    
                    with col_c:
                        if st.button(f"🗑️ Excluir", key=f"delete_{i}_{name}"):
                            # Confirmação antes de excluir
                            if f'confirm_delete_{name}' not in st.session_state:
                                st.session_state[f'confirm_delete_{name}'] = True
                                st.warning(f"⚠️ Tem certeza que deseja excluir '{name}'? Clique novamente para confirmar.")
                                st.rerun()
                            else:
                                del st.session_state.datasets[name]
                                if f'confirm_delete_{name}' in st.session_state:
                                    del st.session_state[f'confirm_delete_{name}']
                                st.success(f"✅ Dataset '{name}' excluído!")
                                st.rerun()
                    
                    # Exibir tabela completa se solicitado
                    if st.session_state.get(f'show_table_{name}', False):
                        st.markdown("---")
                        st.subheader(f"📊 Dataset Completo: {name}")
                        
                        if st.button(f"🔽 Ocultar", key=f"hide_{i}_{name}"):
                            st.session_state[f'show_table_{name}'] = False
                            st.rerun()
                        
                        st.dataframe(df, use_container_width=True, height=400)
                    
                    # Interface de renomeação
                    if st.session_state.get(f'renaming_{name}', False):
                        st.markdown("---")
                        new_name = st.text_input(
                            "✏️ Novo nome do dataset:", 
                            value=name, 
                            key=f"new_name_{i}_{name}"
                        )
                        
                        col_rename1, col_rename2 = st.columns(2)
                        with col_rename1:
                            if st.button("✅ Confirmar", key=f"confirm_rename_{i}_{name}"):
                                if new_name and new_name != name:
                                    if new_name not in st.session_state.datasets:
                                        # Renomear o dataset
                                        st.session_state.datasets[new_name] = st.session_state.datasets.pop(name)
                                        
                                        # Limpar estados relacionados
                                        st.session_state[f'renaming_{name}'] = False
                                        
                                        # Auto-save se habilitado
                                        auto_save_if_enabled(new_name)
                                        
                                        st.success(f"✅ Dataset renomeado de '{name}' para '{new_name}'!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Já existe um dataset com o nome '{new_name}'!")
                                elif new_name == name:
                                    st.session_state[f'renaming_{name}'] = False
                                    st.rerun()
                                else:
                                    st.error("❌ Nome não pode estar vazio!")
                        
                        with col_rename2:
                            if st.button("❌ Cancelar", key=f"cancel_rename_{i}_{name}"):
                                st.session_state[f'renaming_{name}'] = False
                                st.rerun()
        else:
            st.info("📭 Nenhum dataset carregado")
            st.markdown("""
            ### 🚀 Como começar:
            1. **📥 Importe dados** na aba "Import de Dados"
            2. **🧹 Limpe os dados** se necessário
            3. **🔍 Filtre** conforme sua necessidade
            4. **🔗 Relacione** tabelas se precisar
            5. **📈 Analise** seus dados
            
            💡 **Dica**: Esta aba mostrará todos os seus datasets depois da importação!
            """)
    
    with col2:
        st.subheader("Gerenciar Projetos")
        
        # Status do projeto atual
        if st.session_state.current_project:
            st.info(f"📁 Projeto Ativo: **{st.session_state.current_project}**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("💾 Salvar Projeto", key="save_project_main"):
                    if save_project(
                        st.session_state.current_project, 
                        st.session_state.datasets,
                        st.session_state.projects.get(st.session_state.current_project, {}).get('description', '')
                    ):
                        st.success(f"✅ Projeto '{st.session_state.current_project}' salvo!")
                    else:
                        st.error("❌ Erro ao salvar projeto!")
            
            with col_b:
                if st.button("🔄 Novo Projeto", key="new_project_main"):
                    st.session_state.current_project = None
                    st.rerun()
        else:
            st.warning("⚠️ Nenhum projeto ativo")
            st.info("💡 Crie um projeto na barra lateral para organizar seus dados")
        
        st.markdown("---")
        
        # Lista de projetos salvos
        st.write("**📂 Projetos Salvos:**")
        available_projects = get_available_projects()
        
        if available_projects:
            for i, project in enumerate(available_projects):
                with st.expander(f"📁 {project}"):
                    try:
                        project_info = load_project(project)
                        if project_info:
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.write(f"**📅 Criado:** {project_info.get('created_at', 'N/A')[:19].replace('T', ' ')}")
                                st.write(f"**📊 Datasets:** {len(project_info.get('datasets', {}))}")
                            
                            with col_info2:
                                if project_info.get('description'):
                                    st.write(f"**📝 Descrição:** {project_info['description']}")
                                
                                # Botões de ação
                                col_btn1, col_btn2 = st.columns(2)
                                with col_btn1:
                                    if st.button(f"📂 Carregar", key=f"load_{i}"):
                                        project_data = load_project(project)
                                        if project_data:
                                            st.session_state.current_project = project
                                            st.session_state.datasets = project_data.get('datasets', {})
                                            st.session_state.projects[project] = project_data
                                            st.success(f"✅ Projeto '{project}' carregado!")
                                            st.rerun()
                                
                                with col_btn2:
                                    if st.button(f"🗑️ Deletar", key=f"delete_{i}"):
                                        try:
                                            os.remove(f'projects/{project}.pkl')
                                            if project in st.session_state.projects:
                                                del st.session_state.projects[project]
                                            if st.session_state.current_project == project:
                                                st.session_state.current_project = None
                                            st.success(f"✅ Projeto '{project}' deletado!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Erro ao deletar: {str(e)}")
                        else:
                            st.error("❌ Erro ao carregar informações do projeto")
                    except Exception as e:
                        st.error(f"❌ Projeto corrompido: {str(e)}")
        else:
            st.info("📭 Nenhum projeto salvo encontrado")
        
        # Download dos dados
        st.markdown("---")
        st.subheader("📥 Download de Dados")
        if st.session_state.datasets:
            dataset_to_download = st.selectbox("Dataset para download", list(st.session_state.datasets.keys()))
            download_format = st.selectbox("Formato", ["CSV", "Excel"])
            
            if st.button("📥 Preparar Download"):
                df = st.session_state.datasets[dataset_to_download]
                
                if download_format == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"{dataset_to_download}.csv",
                        mime="text/csv"
                    )
                elif download_format == "Excel":
                    buffer = io.BytesIO()
                    df.to_excel(buffer, index=False)
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=buffer.getvalue(),
                        file_name=f"{dataset_to_download}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.info("📊 Nenhum dataset carregado para download")

# Footer
st.markdown("---")
st.markdown("**Análise de Dados Pro** - Ferramenta completa para manipulação e análise de dados")
st.markdown("Desenvolvido por [EditData Soluções Inteligentes](mailto:contato@editdata.com.br)")