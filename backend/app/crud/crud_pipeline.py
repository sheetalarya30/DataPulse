from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.pipeline import Pipeline, PipelineRun
from app.schemas.pipeline import PipelineCreate, PipelineWithStatsResponse


def get_pipeline(db: Session, pipeline_id: str) -> Optional[Pipeline]:
    return db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()


def get_pipeline_by_code(db: Session, code: str) -> Optional[Pipeline]:
    return db.query(Pipeline).filter(Pipeline.code == code).first()


def get_pipelines(db: Session, skip: int = 0, limit: int = 50) -> List[Pipeline]:
    return db.query(Pipeline).offset(skip).limit(limit).all()


def get_pipelines_with_stats(db: Session) -> List[PipelineWithStatsResponse]:
    pipelines = db.query(Pipeline).all()
    results = []

    for pipe in pipelines:
        # Aggregate run statistics
        runs = (
            db.query(PipelineRun)
            .filter(PipelineRun.pipeline_id == pipe.id)
            .order_by(desc(PipelineRun.started_at))
            .all()
        )
        total_runs = len(runs)
        successful_runs = sum(1 for r in runs if r.status == "success")
        success_rate = round((successful_runs / total_runs * 100), 1) if total_runs > 0 else 0.0

        last_run = runs[0] if runs else None

        results.append(
            PipelineWithStatsResponse(
                id=pipe.id,
                name=pipe.name,
                code=pipe.code,
                description=pipe.description,
                source_type=pipe.source_type,
                target_type=pipe.target_type,
                schedule=pipe.schedule,
                status=pipe.status,
                created_at=pipe.created_at,
                updated_at=pipe.updated_at,
                total_runs=total_runs,
                last_run_status=last_run.status if last_run else None,
                last_run_time=last_run.started_at if last_run else None,
                last_run_duration_ms=last_run.duration_ms if last_run else None,
                success_rate=success_rate,
            )
        )
    return results


def create_pipeline(db: Session, obj_in: PipelineCreate) -> Pipeline:
    pipe_id = obj_in.id or f"pipe-{obj_in.code.lower().replace('_', '-')}"
    db_obj = Pipeline(
        id=pipe_id,
        name=obj_in.name,
        code=obj_in.code,
        description=obj_in.description,
        source_type=obj_in.source_type,
        target_type=obj_in.target_type,
        schedule=obj_in.schedule,
        status=obj_in.status,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
