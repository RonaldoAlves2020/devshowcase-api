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

    # Verifica se o perfil existe
    profile = db.query(models.Profile).filter(
        models.Profile.id == project.profile_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil não encontrado"
        )

    # Verifica as tecnologias
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

    # Atualiza os dados
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