# DPP-recommendations

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1YDyAEc9irfTy44NkFl2RfLLuHX--PGcw?usp=sharing)

## Описание проекта

DPP-recommendations — это система рекомендаций для платформы командообразования, которая помогает подбирать кейсы для команд, команды для кейсов и людей в команды на основе их навыков и предпочтений. Основная задача проекта — автоматизация процесса формирования команд, назначение на них подходящих кейсов, а также поиск наиболее подходящих команд для участников.

## Setup
Для установки проекта выполните следующие шаги:

1. Создайте окружение с помощью `conda`:
    ```bash
    conda env create -f environment.yml
    ```

2. Активируйте окружение:
    ```bash
    conda activate dpp-recs
    ```

3. Запустите сервер FastAPI с помощью `uvicorn`:
    ```bash
    uvicorn main:app --reload
    ```

## Описание функционала

### 1. Команда - кейс
Функционал подбора кейса для команды:

- Для каждой команды на основе её навыков система подбирает подходящий кейс.
- В кейсах указаны необходимые роли, которые должна выполнить команда.
- Команда должна удовлетворять требованиям по ролям, чтобы иметь возможность выбрать кейс.


### 2. Кейс - команда
Функционал подбора команды для кейса:
- Для каждого кейса система предлагает команды, которые соответствуют требованиям по навыкам.
- Подбираются команды с участниками, имеющими подходящие навыки для выполнения задач, описанных в кейсе.

### 3. Человек - команда
Функционал подбора команды для участника:
- У каждого участника есть определенные навыки.
- Команды уже выбрали свои кейсы, и система предлагает участнику команды, в которые его навыки и предпочтения лучше всего подходят.
- Рекомендуются команды с учетом потребностей текущего кейса и недостающих ролей.

## Список доступных ролей

Ниже представлен список ролей, которые могут быть необходимы в кейсах:

- Java Backend
- C# Backend
- Go Backend
- Python Backend
- C++ Backend
- Frontend
- ML engineer
- DevOps
- Тестировщик
- Аналитик
- Дизайнер
- Инженер БПЛА
- CV engineer
- ML Ops Engineer


### Описание методов API

#### 1. Рекомендация "Команда — Кейс" (Подбор кейса для команды)

**Эндпоинт**: `/recommend_case_to_team`  
**Метод**: `POST`

Эндпоинт возвращает наиболее подходящий кейс для данной команды на основе её навыков и требуемых ролей в кейсах.

**Параметры**:
- `team`: объект `Team`, представляющий команду, которой подбирается кейс.
- `cases`: список объектов `Case`, представляющих доступные кейсы.
- `alpha`: вес для эмбеддингового сходства (по умолчанию 0.5).
- `beta`: вес для сходства по навыкам (по умолчанию 0.5).

**Описание работы**:
1. Для каждого кейса в списке `cases` рассчитывается сходство между навыками команды и требованиями кейса двумя методами:
   - **Эмбеддинговое сходство**: учитывается текстовое описание кейса и навыков команды, которые преобразуются в эмбеддинги.
   - **Сходство по навыкам**: вычисляется сходство между требуемыми и имеющимися навыками с использованием представления навыков в виде векторов.
2. Гибридное сходство (`hybrid_similarity`) вычисляется с учётом значений `alpha` и `beta`.
3. На основании полученных значений сходства выбирается кейс с наибольшим гибридным значением.

**Пример запроса**:
```json
{
  "team": {
    "team_id": 1,
    "name": "Team 1",
    "skills": {
      "Member 1": ["C#", "Back-end разработка", "Git", "SQL", "Построение Rest API", "Docker"],
      "Member 2": ["C#", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
      "Member 3": ["HTML", "CSS", "React", "Git", "Next", "Tailwind", "JavaScript"],
      "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
      "Member 5": ["Умение работать с API", "PostgreSQL", "Python", "Atlassian stack [Jira, Confluence]", "Linux"],
      "Member 6": ["Data Science", "SQL", "Pandas", "Математическая статистика", "Управление проектами"],
      "Member 7": ["Canva", "Figma", "CSS", "UI/UX", "Adobe XD", "Photoshop"]
    },
    "required_roles": ["C# Backend", "Тестировщик", "Аналитик"]
  },
  "cases": [
    {
      "id": 1,
      "title": "Система контроля качества",
      "description": "Система для контроля качества продукции",
      "required_roles": "C# Backend, Тестировщик, Аналитик"
    },
    {
      "id": 2,
      "title": "Разработка ECM для авиации",
      "description": "Моделирование авиационного двигателя",
      "required_roles": "ML engineer, Аналитик, Python Backend, DevOps"
    }
  ],
  "alpha": 0.6,
  "beta": 0.4
}
```

---

#### 2. Рекомендация "Кейс — Команда" (Подбор команды для кейса)

**Эндпоинт**: `/recommend_team_to_case`  
**Метод**: `POST`

Эндпоинт подбирает команду, которая лучше всего соответствует требованиям конкретного кейса. 

**Параметры**:
- `case`: объект `Case`, представляющий кейс, для которого подбирается команда.
- `teams`: список объектов `Team`, представляющих доступные команды.
- `alpha`: вес для эмбеддингового сходства (по умолчанию 0.5).
- `beta`: вес для сходства по навыкам (по умолчанию 0.5).

**Описание работы**:
1. Для каждой команды в списке `teams` рассчитывается её соответствие требованиям кейса по эмбеддинговому и векторному сходству.
2. Вычисляется гибридное значение сходства, учитывающее веса `alpha` и `beta`.
3. Возвращается команда с наибольшим значением гибридного сходства.

**Пример запроса**:
```json
{
  "case": {
    "id": 1,
    "title": "Система контроля качества продуктов АО 'Медитек'",
    "description": "Система контроля качества продуктов требуется для контроля качества и технических параметров приборов.",
    "required_roles": "C# Backend, Тестировщик, Аналитик"
  },
  "teams": [
    {
      "team_id": 1,
      "name": "Team 1",
      "skills": {
        "Member 1": ["C#", "Back-end разработка", "Git", "SQL", "Построение Rest API", "Docker"],
        "Member 2": ["C#", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
        "Member 3": ["HTML", "CSS", "React", "Git", "Next", "Tailwind", "JavaScript"],
        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
        "Member 5": ["Умение работать с API", "PostgreSQL", "Python", "Atlassian stack [Jira, Confluence]", "Linux"],
        "Member 6": ["Data Science", "SQL", "Pandas", "Математическая статистика", "Управление проектами"],
        "Member 7": ["Canva", "Figma", "CSS", "UI/UX", "Adobe XD", "Photoshop"]
      }
    },
    {
      "team_id": 2,
      "name": "Team 2",
      "skills": {
        "Member 1": ["Python", "Back-end разработка", "Django", "Docker", "Git", "SQL", "Построение Rest API"],
        "Member 2": ["Python", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
        "Member 3": ["Machine Learning", "Data Science", "Python", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow"],
        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
        "Member 5": ["Python", "PostgreSQL", "Умение работать с API", "Atlassian stack [Jira, Confluence]", "Linux"],
        "Member 6": ["Data Science", "SQL", "Математическая статистика", "Pandas", "Scikit-Learn"],
        "Member 7": ["DevOps", "Machine Learning", "AirFlow", "Docker", "Kubernetes", "ONNX Runtime"]
      }
    }
  ],
  "alpha": 0.6,
  "beta": 0.4
}
```

---

#### 3. Рекомендация "Человек — Команда" (Подбор команды для участника)

**Эндпоинт**: `/recommend_team_to_person`  
**Метод**: `POST`

Эндпоинт возвращает команду, которая лучше всего соответствует навыкам нового участника.

**Параметры**:
- `person_skills`: список навыков участника.
- `teams`: список объектов `Team`, представляющих доступные команды.
- `threshold`: порог для заполненности роли (по умолчанию 0.5).
- `unfilled_role_weight`: вес для незаполненных ролей (по умолчанию 1.5).

**Описание работы**:
1. Для каждой команды оцениваются заполненные роли и схожесть навыков участника и команды.
2. Если в команде есть незаполненные роли, то вычисляется сходство с учетом необходимых навыков для закрытия этих ролей.
3. Возвращается команда с наибольшим значением схожести.

**Пример запроса**:
```json
{
  "person_skills": ["Python", "Docker", "Kubernetes", "Linux", "Machine Learning"],
  "teams": [
    {
      "team_id": 1,
      "name": "Система контроля качества продуктов АО Медитек",
      "skills": {
        "Member 1": ["C#", "Back-end разработка", "Git", "SQL", "

Построение Rest API", "Docker"],
        "Member 2": ["C#", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
        "Member 3": ["HTML", "CSS", "React", "Git", "Next", "Tailwind", "JavaScript"],
        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
        "Member 5": ["Умение работать с API", "PostgreSQL", "Python", "Atlassian stack [Jira, Confluence]", "Linux"],
        "Member 6": ["Data Science", "SQL", "Pandas", "Математическая статистика", "Управление проектами"],
        "Member 7": ["Canva", "Figma", "CSS", "UI/UX", "Adobe XD", "Photoshop"]
      },
      "required_roles": ["C# Backend", "Тестировщик", "Аналитик"]
    },
    {
      "team_id": 2,
      "name": "Разработка системы ECM для авиационного двигателя",
      "skills": {
        "Member 1": ["Python", "Back-end разработка", "Django", "Docker", "Git", "SQL", "Построение Rest API"],
        "Member 2": ["Python", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
        "Member 3": ["Machine Learning", "Data Science", "Python", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow"],
        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
        "Member 5": ["Python", "PostgreSQL", "Умение работать с API", "Atlassian stack [Jira, Confluence]", "Linux"],
        "Member 6": ["Data Science", "SQL", "Математическая статистика", "Pandas", "Scikit-Learn"],
        "Member 7": ["DevOps", "Machine Learning", "AirFlow", "Docker", "Kubernetes", "ONNX Runtime"]
      },
      "required_roles": ["ML engineer", "Аналитик", "Python Backend", "DevOps", "ML Ops Engineer"]
    }
  ],
  "threshold": 0.5,
  "unfilled_role_weight": 1.5
}
```


