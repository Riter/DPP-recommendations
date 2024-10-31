import torch
from typing import List, Dict
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from src import role_to_skills_mapping, all_skills


# Функция для получения всех требуемых навыков для команды на основе необходимых ролей
def get_required_skills(roles: List[str]) -> List[str]:
    """
    Get all required skills for a team based on the roles required.

    Args:
    roles (List[str]): A list of roles required for the team.

    Returns:
    List[str]: A list of all required skills for the team.
    """
    required_skills = []
    for role in roles:
        required_skills.extend(role_to_skills_mapping.get(role, []))
    return list(set(required_skills))  # Убираем дубликаты

# Функция для получения общего списка скиллов команды
def get_team_skills(team_skills: Dict) -> List[str]:
    """
    Get all skills of the team members.

    Args:
    team_skills (Dict): A dictionary with team members as keys and their skills as values.

    Returns:
    List[str]: A list of all skills in the team.
    """
    all_current_skills = []
    for member, skills in team_skills.items():
        all_current_skills.extend(skills)
    return list(set(all_current_skills))  # Убираем дубликаты

# Проверка, закрыты ли все необходимые роли в команде
def get_filled_roles(team_skills: Dict, required_roles: List[str], threshold: float = 0.45) -> List[str]:
    """
    Check if all required roles are filled in the team.

    Args:
    team_skills (Dict): A dictionary with team members as keys and their skills as values.
    required_roles (List[str]): A list of roles required for the team.
    threshold (float, optional): Minimum percentage of skills that must be matched to consider a role filled. Defaults to 0.45.

    Returns:
    List[str]: A list of roles that are filled in the team.
    """
    filled_roles = []
    team_skills_flat = get_team_skills(team_skills)
    
    for role in required_roles:
        role_skills = role_to_skills_mapping.get(role, [])
        matched_skills = [skill for skill in role_skills if skill in team_skills_flat]
        
        # Если хотя бы threshold % навыков из необходимых для роли совпадают с навыками команды
        if len(matched_skills) / len(role_skills) >= threshold:
            filled_roles.append(role)
    
    return filled_roles

# Функция для расчета схожести на основе Bag of Skills с весом для незаполненных ролей
def calculate_weighted_similarity(person_skills: List[str], required_skills: List[str], all_skills: List[str], weight: float = 1.0) -> float:
    """
    Calculate a weighted similarity between a person's skills and required skills for a team.

    Args:
    person_skills (List[str]): A list of skills of a person.
    required_skills (List[str]): A list of skills required for a team.
    all_skills (List[str]): A list of all skills in the team.
    weight (float, optional): Weight to be applied to the similarity score. Defaults to 1.0.

    Returns:
    float: Weighted similarity score between the person's skills and required skills.
    """
    person_vector = np.array([1 if skill in person_skills else 0 for skill in all_skills])
    required_vector = np.array([1 if skill in required_skills else 0 for skill in all_skills])
    similarity = cosine_similarity([person_vector], [required_vector])[0][0]
    return similarity * weight


def get_text_embedding(text, model, tokenizer, device):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).cpu().numpy()

def compute_similarity(case_embeddings, team_embedding):
    return cosine_similarity(case_embeddings, team_embedding.reshape(1, -1))

def get_case_to_team_recs_by_embedding(team: Dict, df_cases: pd.DataFrame) -> pd.DataFrame:
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model_path = "intfloat/multilingual-e5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path).to(device)

    team_skills = get_team_skills(team)
    team_text = " ".join(team_skills)
    team_embedding = get_text_embedding(team_text, model, tokenizer, device)

    case_embeddings = []
    for _, row in df_cases.iterrows():
        case_text = row['title'] + " | " + row['description'] + " | Required roles: " + row['required_roles']
        case_embedding = get_text_embedding(case_text, model, tokenizer, device)
        case_embeddings.append(case_embedding)

    case_embeddings = np.vstack(case_embeddings)
    similarities = compute_similarity(case_embeddings, team_embedding)
    df_cases['embedding_similarity'] = similarities

    return df_cases

def skills_to_vector(skills, all_skills):
    return np.array([1 if skill in skills else 0 for skill in all_skills])

def roles_to_skills_vector(roles, role_to_skills_mapping, all_skills):
    all_case_skills = set()
    for role in roles:
        role_skills = role_to_skills_mapping.get(role, [])
        all_case_skills.update(role_skills)
    return skills_to_vector(all_case_skills, all_skills)

def team_to_skills_vector(team, all_skills):
    all_team_skills = set()
    for member, skills in team.items():
        all_team_skills.update(skills)
    return skills_to_vector(all_team_skills, all_skills)

def get_case_to_team_recs_by_mapping(team: Dict, df_cases: pd.DataFrame, role_to_skills_mapping: Dict, all_skills: list) -> pd.DataFrame:
    team_skills_vector = team_to_skills_vector(team, all_skills)
    similarities = []
    
    for _, row in df_cases.iterrows():
        case_roles = row['required_roles'].split(", ")
        case_skills_vector = roles_to_skills_vector(case_roles, role_to_skills_mapping, all_skills)
        similarity = cosine_similarity([case_skills_vector], [team_skills_vector])[0][0]
        similarities.append(similarity)

    df_cases['skills_similarity'] = similarities
    return df_cases

def calculate_hybrid_similarity(embedding_similarity, skill_similarity, alpha=0.5, beta=0.5):
    return alpha * embedding_similarity + beta * skill_similarity

def get_team_to_case_recs_by_embedding(case: Dict, teams: Dict, model, tokenizer, device) -> pd.DataFrame:
    case_text = case['title'] + " | " + case['description'] + " | Required roles: " + case['required_roles']
    case_embedding = get_text_embedding(case_text, model, tokenizer, device)
    
    team_embeddings = []
    for team_id, team_data in teams.items():
        team_name = team_data.get('name', f'Team {team_id}')  # Получаем team_name или создаем дефолтное имя
        team_skills = get_team_skills(team_data['skills'])
        team_text = " ".join(team_skills)
        team_embedding = get_text_embedding(team_text, model, tokenizer, device)
        similarity = compute_similarity(case_embedding, team_embedding)
        team_embeddings.append({
            'team_id': int(team_id),  # Приводим к int
            'team_name': team_name,
            'embedding_similarity': float(similarity[0][0])  # Приводим к float
        })
    
    return pd.DataFrame(team_embeddings)

def get_team_to_case_recs_by_mapping(case: Dict, teams: Dict, role_to_skills_mapping: Dict, all_skills: list) -> pd.DataFrame:
    case_roles = case['required_roles'].split(", ")
    case_skills_vector = roles_to_skills_vector(case_roles, role_to_skills_mapping, all_skills)
    
    similarities = []
    for team_id, team_data in teams.items():
        team_name = team_data.get('name', f'Team {team_id}')
        team_skills_vector = team_to_skills_vector(team_data['skills'], all_skills)
        similarity = cosine_similarity([case_skills_vector], [team_skills_vector])[0][0]
        similarities.append({
            'team_id': int(team_id),  # Приводим к int
            'team_name': team_name,
            'skills_similarity': float(similarity)  # Приводим к float
        })
    
    return pd.DataFrame(similarities)

def get_team_to_case_recs(case: Dict, teams: Dict, role_to_skills_mapping: Dict, all_skills: list, alpha=0.5, beta=0.5) -> pd.DataFrame:
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model_path = "intfloat/multilingual-e5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path).to(device)
    
    # Получаем рекомендации по эмбеддингам
    df_embedding = get_team_to_case_recs_by_embedding(case, teams, model, tokenizer, device)
    
    # Получаем рекомендации по маппингу
    df_mapping = get_team_to_case_recs_by_mapping(case, teams, role_to_skills_mapping, all_skills)
    
    # Объединяем результаты и вычисляем гибридное сходство
    df_hybrid = pd.merge(df_embedding, df_mapping, on=['team_id', 'team_name'])
    df_hybrid['hybrid_similarity'] = calculate_hybrid_similarity(
        df_hybrid['embedding_similarity'],
        df_hybrid['skills_similarity'],
        alpha,
        beta
    ).astype(float)  # Приводим к float
    
    return df_hybrid.sort_values(by='hybrid_similarity', ascending=False)

