from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import engine, get_db
import app.models as models
import app.schemas as schemas


# ==========================================
# CRIAÇÃO DAS TABELAS
# ==========================================

models.Base.metadata.create_all(bind=engine)


# ==========================================
# CONFIGURAÇÃO DA API
# ==========================================

app = FastAPI(
    title="DevShowcase API",
    description="API para sistema de portfólio de desenvolvedores",
    version="1.2.0"
)


# ==========================================
# TRATAMENTO GLOBAL DE ERROS HTTP
# ==========================================

@app.exception_handler(StarletteHTTPException)
async def tratar_http_exception(
    request: Request,
    exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "sucesso": False,
            "status": exc.status_code,
            "erro": "Erro na requisição",
            "mensagem": str(exc.detail)
        }
    )


# ==========================================
# TRATAMENTO GLOBAL DE VALIDAÇÃO
# ==========================================

@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    exc: RequestValidationError
):

    erros = []

    for erro in exc.errors():

        campo = " -> ".join(
            str(item) for item in erro["loc"]
        )

        erros.append({
            "campo": campo,
            "mensagem": erro["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "sucesso": False,
            "status": 422,
            "erro": "Erro de validação",
            "mensagem": "Verifique os dados enviados.",
            "detalhes": erros
        }
    )


# ==========================================
# TRATAMENTO GLOBAL DE ERRO INTERNO
# ==========================================

@app.exception_handler(Exception)
async def tratar_erro_interno(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=500,
        content={
            "sucesso": False,
            "status": 500,
            "erro": "Erro interno do servidor",
            "mensagem": "Ocorreu um erro inesperado."
        }
    )


# ==========================================
# INÍCIO DA API
# ==========================================

@app.get("/")
def inicio():

    return {
        "sistema": "DevShowcase",
        "mensagem": "API funcionando com sucesso!",
        "site": "/site",
        "documentacao": "/docs"
    }


# ==========================================
# PROFILE - CRIAR
# ==========================================

@app.post(
    "/api/profiles",
    response_model=schemas.ProfileResponse
)
def criar_profile(
    profile: schemas.ProfileCreate,
    db: Session = Depends(get_db)
):

    existente = db.query(models.Profile).filter(
        models.Profile.email == profile.email
    ).first()

    if existente:

        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    novo_profile = models.Profile(
        name=profile.name,
        email=profile.email,
        bio=profile.bio,
        github_url=(
            str(profile.github_url)
            if profile.github_url
            else None
        )
    )

    db.add(novo_profile)

    db.commit()

    db.refresh(novo_profile)

    return novo_profile


# ==========================================
# PROFILE - BUSCAR POR ID
# ==========================================

@app.get(
    "/api/profiles/{profile_id}",
    response_model=schemas.ProfileResponse
)
def buscar_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):

    profile = db.query(
        models.Profile
    ).filter(
        models.Profile.id == profile_id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Perfil não encontrado"
        )

    return profile


# ==========================================
# PROFILE - LISTAR TODOS
# ==========================================

@app.get(
    "/api/profiles",
    response_model=list[schemas.ProfileResponse]
)
def listar_profiles(
    db: Session = Depends(get_db)
):

    profiles = (
        db.query(models.Profile)
        .order_by(models.Profile.name.asc())
        .all()
    )

    return profiles


# ==========================================
# TECHNOLOGY - CRIAR
# ==========================================

@app.post(
    "/api/technologies",
    response_model=schemas.TechnologyResponse
)
def criar_tecnologia(
    technology: schemas.TechnologyCreate,
    db: Session = Depends(get_db)
):

    existente = db.query(
        models.Technology
    ).filter(
        models.Technology.name == technology.name
    ).first()

    if existente:

        raise HTTPException(
            status_code=400,
            detail="Tecnologia já cadastrada"
        )

    nova_tecnologia = models.Technology(
        name=technology.name
    )

    db.add(nova_tecnologia)

    db.commit()

    db.refresh(nova_tecnologia)

    return nova_tecnologia


# ==========================================
# TECHNOLOGY - LISTAR
# ==========================================

@app.get(
    "/api/technologies",
    response_model=list[schemas.TechnologyResponse]
)
def listar_tecnologias(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Technology
    ).all()


# ==========================================
# PROJECT - CRIAR
# ==========================================

@app.post(
    "/api/projects",
    response_model=schemas.ProjectResponse
)
def criar_projeto(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):

    # Verifica se o perfil existe

    profile = db.query(
        models.Profile
    ).filter(
        models.Profile.id == project.profile_id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Perfil não encontrado"
        )

    # Cria o projeto

    novo_projeto = models.Project(
        title=project.title,
        description=project.description,
        repository_url=(
            str(project.repository_url)
            if project.repository_url
            else None
        ),
        profile_id=project.profile_id,
        upvotes=0,
        average_rating=0.0
    )

    # Relaciona as tecnologias

    if project.technology_ids:

        ids_unicos = set(
            project.technology_ids
        )

        tecnologias = db.query(
            models.Technology
        ).filter(
            models.Technology.id.in_(
                ids_unicos
            )
        ).all()

        if len(tecnologias) != len(ids_unicos):

            raise HTTPException(
                status_code=404,
                detail=(
                    "Uma ou mais tecnologias "
                    "não foram encontradas"
                )
            )

        novo_projeto.technologies = tecnologias

    db.add(novo_projeto)

    db.commit()

    db.refresh(novo_projeto)

    return novo_projeto


# ==========================================
# PROJECT - PESQUISAR
# ==========================================

@app.get(
    "/api/projects/search",
    response_model=list[schemas.ProjectResponse]
)
def pesquisar_projetos(
    q: str,
    db: Session = Depends(get_db)
):

    termo = q.strip()

    if not termo:

        raise HTTPException(
            status_code=400,
            detail="Informe um termo para pesquisa"
        )

    projetos = db.query(
        models.Project
    ).filter(
        or_(
            models.Project.title.ilike(
                f"%{termo}%"
            ),
            models.Project.description.ilike(
                f"%{termo}%"
            )
        )
    ).all()

    return projetos


# ==========================================
# PROJECT - RANKING
# ==========================================

@app.get(
    "/api/projects/ranking",
    response_model=list[schemas.ProjectResponse]
)
def ranking_projetos(
    limite: int = 10,
    db: Session = Depends(get_db)
):

    if limite < 1 or limite > 100:

        raise HTTPException(
            status_code=400,
            detail="O limite deve estar entre 1 e 100"
        )

    projetos = (
        db.query(models.Project)
        .order_by(
            models.Project.upvotes.desc(),
            models.Project.id.asc()
        )
        .limit(limite)
        .all()
    )

    return projetos


# ==========================================
# PROJECT - LISTAR / FILTRAR / PAGINAR
# ==========================================

@app.get(
    "/api/projects",
    response_model=list[schemas.ProjectResponse]
)
def listar_projetos(
    tecnologia: str | None = None,
    pagina: int = 1,
    limite: int = 10,
    db: Session = Depends(get_db)
):

    # Validação da página

    if pagina < 1:

        raise HTTPException(
            status_code=400,
            detail=(
                "A página deve ser "
                "maior ou igual a 1"
            )
        )

    # Validação do limite

    if limite < 1 or limite > 100:

        raise HTTPException(
            status_code=400,
            detail=(
                "O limite deve estar "
                "entre 1 e 100"
            )
        )

    consulta = db.query(
        models.Project
    )

    # ======================================
    # FILTRO POR TECNOLOGIA
    # ======================================

    if tecnologia:

        nome_tecnologia = tecnologia.strip()

        if nome_tecnologia:

            consulta = consulta.filter(
                models.Project.technologies.any(
                    models.Technology.name.ilike(
                        f"%{nome_tecnologia}%"
                    )
                )
            )

    # ======================================
    # PAGINAÇÃO
    # ======================================

    offset = (
        pagina - 1
    ) * limite

    projetos = (
        consulta
        .order_by(
            models.Project.id.desc()
        )
        .offset(offset)
        .limit(limite)
        .all()
    )

    return projetos


# ==========================================
# PROJECT - BUSCAR POR ID
# ==========================================

@app.get(
    "/api/projects/{project_id}",
    response_model=schemas.ProjectResponse
)
def buscar_projeto(
    project_id: int,
    db: Session = Depends(get_db)
):

    projeto = db.query(
        models.Project
    ).filter(
        models.Project.id == project_id
    ).first()

    if not projeto:

        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    return projeto


# ==========================================
# FEEDBACK - CRIAR
# ==========================================

@app.post(
    "/api/projects/{project_id}/feedbacks",
    response_model=schemas.FeedbackResponse
)
def criar_feedback(
    project_id: int,
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):

    # Verifica se o projeto existe

    projeto = db.query(
        models.Project
    ).filter(
        models.Project.id == project_id
    ).first()

    if not projeto:

        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    # Cria o feedback

    novo_feedback = models.Feedback(
        rating=feedback.rating,
        comment=feedback.comment,
        project_id=project_id
    )

    db.add(novo_feedback)

    db.commit()

    db.refresh(novo_feedback)

    # ======================================
    # CALCULA A MÉDIA DAS AVALIAÇÕES
    # ======================================

    media = db.query(
        func.avg(
            models.Feedback.rating
        )
    ).filter(
        models.Feedback.project_id
        == project_id
    ).scalar()

    # ======================================
    # ATUALIZA A MÉDIA DO PROJETO
    # ======================================

    projeto.average_rating = round(
        float(media or 0),
        2
    )

    db.commit()

    db.refresh(projeto)

    return novo_feedback


# ==========================================
# FEEDBACK - LISTAR POR PROJETO
# ==========================================

@app.get(
    "/api/projects/{project_id}/feedbacks",
    response_model=list[schemas.FeedbackResponse]
)
def listar_feedbacks(
    project_id: int,
    db: Session = Depends(get_db)
):

    projeto = db.query(
        models.Project
    ).filter(
        models.Project.id == project_id
    ).first()

    if not projeto:

        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    feedbacks = db.query(
        models.Feedback
    ).filter(
        models.Feedback.project_id
        == project_id
    ).all()

    return feedbacks


# ==========================================
# UPVOTE
# ==========================================

@app.put(
    "/api/projects/{project_id}/upvote",
    response_model=schemas.ProjectResponse
)
def dar_upvote(
    project_id: int,
    db: Session = Depends(get_db)
):

    projeto = db.query(
        models.Project
    ).filter(
        models.Project.id == project_id
    ).first()

    if not projeto:

        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    if projeto.upvotes is None:
        projeto.upvotes = 0

    projeto.upvotes += 1

    db.commit()

    db.refresh(projeto)

    return projeto


# ==========================================
# FRONT-END
# ==========================================

@app.get(
    "/site",
    include_in_schema=False
)


# ==========================================
# PROJECT - ATUALIZAR
# ==========================================

@app.put(
    "/api/projects/{project_id}",
    response_model=schemas.ProjectResponse
)
def atualizar_projeto(
    project_id: int,
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    projeto = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    profile = db.query(models.Profile).filter(
        models.Profile.id == project.profile_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil não encontrado"
        )

    tecnologias = []

    if project.technology_ids:
        ids_unicos = set(project.technology_ids)

        tecnologias = db.query(models.Technology).filter(
            models.Technology.id.in_(ids_unicos)
        ).all()

        if len(tecnologias) != len(ids_unicos):
            raise HTTPException(
                status_code=404,
                detail="Uma ou mais tecnologias não foram encontradas"
            )

    projeto.title = project.title
    projeto.description = project.description
    projeto.repository_url = (
        str(project.repository_url)
        if project.repository_url
        else None
    )
    projeto.profile_id = project.profile_id
    projeto.technologies = tecnologias

    db.commit()
    db.refresh(projeto)

    return projeto


# ==========================================
# PROJECT - EXCLUIR
# ==========================================

@app.delete("/api/projects/{project_id}")
def excluir_projeto(
    project_id: int,
    db: Session = Depends(get_db)
):
    projeto = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    db.delete(projeto)
    db.commit()

    return {
        "sucesso": True,
        "mensagem": "Projeto excluído com sucesso",
        "project_id": project_id
    }


def abrir_site():

    return FileResponse(
        "static/index.html"
    )