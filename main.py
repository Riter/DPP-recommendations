from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from src.utils import *

app = FastAPI()

# Модели для запросов
class Team(BaseModel):
    team_id: int
    name: str
    skills: Dict[str, List[str]]
    required_roles: List[str] = None

class Case(BaseModel):
    id: int
    title: str
    description: str
    required_roles: str
 
class RecommendTeamToPersonRequest(BaseModel):
    person_skills: List[str]
    teams: List[Team]
    threshold: float = 0.5
    unfilled_role_weight: float = 1.5

class RecommendCaseToTeamRequest(BaseModel):
    team: Team
    cases: List[Case]
    alpha: float = 0.5
    beta: float = 0.5

class RecommendTeamToCaseRequest(BaseModel):
    case: Case
    teams: List[Team]
    alpha: float = 0.5
    beta: float = 0.5

# Рекомендация "Человек - команда"
@app.post("/recommend_team_to_person")
async def recommend_team_to_person(request: RecommendTeamToPersonRequest):
    """
    Recommend a team to a person based on the person's skills and the required skills of the teams.

    Args:
    request (RecommendTeamToPersonRequest): A request containing the person's skills, a list of teams, a threshold for the required skills, and a weight for unfilled roles.

    Returns:
    Dict: A dictionary containing the recommended team ID and name.

    Raises:
    HTTPException: If no suitable team is found.
    """
    best_team = None
    best_score = -1

    for team in request.teams:
        filled_roles = get_filled_roles(team.skills, team.required_roles, threshold=request.threshold)
        unfilled_roles = [role for role in team.required_roles if role not in filled_roles]

        if unfilled_roles:
            unfilled_role_skills = get_required_skills(unfilled_roles)
            all_required_skills = get_required_skills(team.required_roles)
            similarity = calculate_weighted_similarity(request.person_skills, unfilled_role_skills, all_required_skills, request.unfilled_role_weight)
        else:
            team_skills = [skill for skills in team.skills.values() for skill in skills]
            similarity = calculate_weighted_similarity(request.person_skills, team_skills, team_skills)
        
        if similarity > best_score:
            best_team = team
            best_score = similarity

    if best_team:
        return {"recommended_team_id": best_team.team_id, "recommended_team_name": best_team.name}
    else:
        raise HTTPException(status_code=404, detail="No suitable team found")

# Рекомендация "Команда - кейс"
@app.post("/recommend_case_to_team")
async def recommend_case_to_team(request: RecommendCaseToTeamRequest):
    """
    Recommend a case to a team based on the team's skills and the required skills of the case.

    Args:
    request (RecommendCaseToTeamRequest): A request containing the team's skills, a list of cases, a parameter alpha for the hybrid similarity, and a parameter beta for the hybrid similarity.

    Returns:
    Dict: A dictionary containing the ID and title of the recommended case.

    Raises:
    HTTPException: If no suitable case is found.
    """
    df_cases = pd.DataFrame([case.dict() for case in request.cases])
    
    # Получаем рекомендации по эмбеддингам и по маппингу
    df_cases = get_case_to_team_recs_by_embedding(request.team.skills, df_cases)
    df_cases = get_case_to_team_recs_by_mapping(request.team.skills, df_cases, role_to_skills_mapping, all_skills)

    # Вычисляем гибридное сходство
    df_cases['hybrid_similarity'] = calculate_hybrid_similarity(
        df_cases['embedding_similarity'],
        df_cases['skills_similarity'],
        request.alpha,
        request.beta
    )

    # Находим кейс с наивысшим гибридным сходством
    recommended_case = df_cases.loc[df_cases['hybrid_similarity'].idxmax()]

    # Преобразуем numpy.int64 в int для возврата
    return {"id": int(recommended_case['id']), "title": recommended_case['title']}


@app.post("/recommend_team_to_case")
async def recommend_team_to_case(request: RecommendTeamToCaseRequest):
    """
    Recommend a team to a case based on the case's requirements and team skills.

    Args:
    request (RecommendTeamToCaseRequest): A request containing the case details, a list of teams, a parameter alpha, and a parameter beta for hybrid similarity.

    Returns:
    Dict: A dictionary containing the team ID, team name, and its similarity score.

    Raises:
    HTTPException: If no suitable team is found.
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
    
    # Получаем команду с наибольшим гибридным сходством
    best_team = df_hybrid.iloc[0]
    return {"team_id": int(best_team['team_id']), "team_name": best_team['team_name'], "hybrid_similarity": best_team['hybrid_similarity']}
