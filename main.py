from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from src.utils import *

app = FastAPI()

# Request Models
class Team(BaseModel):
    """
    Represents a team with an ID, name, skills, and required roles.
    Attributes:
        team_id (int): Unique identifier of the team.
        name (str): Name of the team.
        skills (Dict[str, List[str]]): Dictionary where keys are team members and values are lists of their skills.
        required_roles (List[str], optional): List of roles required by the team.
    """
    team_id: int
    name: str
    skills: Dict[str, List[str]]
    required_roles: List[str] = None

class Case(BaseModel):
    """
    Represents a case or project with ID, title, description, and required roles.
    Attributes:
        id (int): Unique identifier of the case.
        title (str): Title of the case.
        description (str): Detailed description of the case.
        required_roles (str): String of required roles for the case.
    """
    id: int
    title: str
    description: str
    required_roles: str

class RecommendTeamToPersonRequest(BaseModel):
    """
    Request model for recommending teams to a person based on their skills.
    Attributes:
        person_skills (List[str]): List of skills of the person.
        teams (List[Team]): List of teams available for recommendation.
        role_filled_threshold (float): Threshold for determining filled roles.
        unfilled_role_weight (float): Weight applied to unfilled roles in similarity calculation.
        confidence_percentile (float): Percentile threshold for filtering recommended teams by similarity.
    """
    person_skills: List[str]
    teams: List[Team]
    role_filled_threshold: float = 0.5  # Renamed threshold for clarity
    unfilled_role_weight: float = 1.5
    confidence_percentile: float = 0.9

class RecommendCaseToTeamRequest(BaseModel):
    """
    Request model for recommending cases to a team based on the team's skills.
    Attributes:
        team (Team): Team for which a case recommendation is being made.
        cases (List[Case]): List of cases available for recommendation.
        alpha (float): Weight applied to embedding similarity.
        beta (float): Weight applied to skill-based similarity.
        confidence_percentile (float): Percentile threshold for filtering recommended cases.
    """
    team: Team
    cases: List[Case]
    alpha: float = 0.5
    beta: float = 0.5
    confidence_percentile: float = 0.9

class RecommendTeamToCaseRequest(BaseModel):
    """
    Request model for recommending teams to a case based on case requirements.
    Attributes:
        case (Case): Case for which a team recommendation is being made.
        teams (List[Team]): List of teams available for recommendation.
        alpha (float): Weight applied to embedding similarity.
        beta (float): Weight applied to skill-based similarity.
        confidence_percentile (float): Percentile threshold for filtering recommended teams.
    """
    case: Case
    teams: List[Team]
    alpha: float = 0.5
    beta: float = 0.5
    confidence_percentile: float = 0.9

# Рекомендация: Человек - Команда
@app.post("/recommend_team_to_person")
async def recommend_team_to_person(request: RecommendTeamToPersonRequest):
    """
    Recommend a list of suitable teams for a person based on their skills.

    This function calculates similarity scores between the person's skills and each team's
    required skills, factoring in filled roles and unfilled role weights. Teams are recommended
    based on a specified percentile threshold for similarity.

    Args:
        request (RecommendTeamToPersonRequest): Contains person skills, list of teams, and filtering criteria.

    Returns:
        Dict: List of recommended teams meeting the percentile confidence threshold.

    Raises:
        HTTPException: If no suitable teams are found above the threshold.
    """
    similarities = []

    for team in request.teams:
        # Определяем заполненные роли в команде
        filled_roles = get_filled_roles(team.skills, team.required_roles, threshold=request.role_filled_threshold)
        unfilled_roles = [role for role in team.required_roles if role not in filled_roles]

        # Если есть незаполненные роли, рассчитываем сходство с их учетом
        if unfilled_roles:
            unfilled_role_skills = get_required_skills(unfilled_roles)
            all_required_skills = get_required_skills(team.required_roles)
            similarity = calculate_weighted_similarity(request.person_skills, unfilled_role_skills, all_required_skills, request.unfilled_role_weight)
        else:
            # Если все роли заполнены, рассчитываем сходство по навыкам команды
            team_skills = [skill for skills in team.skills.values() for skill in skills]
            similarity = calculate_weighted_similarity(request.person_skills, team_skills, team_skills)

        similarities.append({"team_id": team.team_id, "team_name": team.name, "similarity": similarity})

    # Определяем персентильный порог
    df_similarities = pd.DataFrame(similarities)
    threshold_value = df_similarities['similarity'].quantile(request.confidence_percentile)

    # Выбираем команды, которые соответствуют порогу
    recommended_teams = df_similarities[df_similarities['similarity'] >= threshold_value].to_dict(orient="records")

    if recommended_teams:
        return {"recommended_teams": recommended_teams}
    else:
        raise HTTPException(status_code=404, detail="Подходящие команды не найдены")

# Рекомендация: Команда - Кейс
@app.post("/recommend_case_to_team")
async def recommend_case_to_team(request: RecommendCaseToTeamRequest):
    """
    Recommend a list of suitable cases for a team based on the team's skills.

    This function calculates hybrid similarity scores between the team's skills and each case's
    required roles using embedding and skill-based similarities. Cases are recommended based on
    a specified percentile threshold for hybrid similarity.

    Args:
        request (RecommendCaseToTeamRequest): Contains team skills, list of cases, and filtering criteria.

    Returns:
        Dict: List of recommended cases meeting the percentile confidence threshold.

    Raises:
        HTTPException: If no suitable cases are found above the threshold.
    """
    df_cases = pd.DataFrame([case.dict() for case in request.cases])

    # Расчет сходства для эмбеддингов и навыков
    df_cases = get_case_to_team_recs_by_embedding(request.team.skills, df_cases)
    df_cases = get_case_to_team_recs_by_mapping(request.team.skills, df_cases, role_to_skills_mapping, all_skills)

    # Гибридное сходство
    df_cases['hybrid_similarity'] = calculate_hybrid_similarity(
        df_cases['embedding_similarity'],
        df_cases['skills_similarity'],
        request.alpha,
        request.beta
    )

    # Порог персентиля
    threshold_value = df_cases['hybrid_similarity'].quantile(request.confidence_percentile)
    recommended_cases = df_cases[df_cases['hybrid_similarity'] >= threshold_value][['id', 'title', 'hybrid_similarity']].to_dict(orient="records")

    if recommended_cases:
        return {"recommended_cases": recommended_cases}
    else:
        raise HTTPException(status_code=404, detail="Подходящие кейсы не найдены")

# Рекомендация: Кейс - Команда
@app.post("/recommend_team_to_case")
async def recommend_team_to_case(request: RecommendTeamToCaseRequest):
    """
    Recommend a list of suitable teams for a case based on the case's requirements.

    This function calculates hybrid similarity scores between each team's skills and the case's
    requirements, using embedding and skill-based similarities. Teams are recommended based on
    a specified percentile threshold for hybrid similarity.

    Args:
        request (RecommendTeamToCaseRequest): Contains case requirements, list of teams, and filtering criteria.

    Returns:
        Dict: List of recommended teams meeting the percentile confidence threshold.

    Raises:
        HTTPException: If no suitable teams are found above the threshold.
    """
    teams_dict = {team.team_id: team.dict() for team in request.teams}
    df_hybrid = get_team_to_case_recs(
        request.case.dict(),
        teams_dict,
        role_to_skills_mapping,
        all_skills,
        request.alpha,
        request.beta
    )

    # Порог персентиля
    threshold_value = df_hybrid['hybrid_similarity'].quantile(request.confidence_percentile)
    recommended_teams = df_hybrid[df_hybrid['hybrid_similarity'] >= threshold_value][['team_id', 'team_name', 'hybrid_similarity']].to_dict(orient="records")

    if recommended_teams:
        return {"recommended_teams": recommended_teams}
    else:
        raise HTTPException(status_code=404, detail="No suitable team found")
