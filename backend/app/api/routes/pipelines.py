from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.pipeline import (
    PipelineResponse,
    PipelineWithStatsResponse,
    PipelineRunResponse,
    PipelineRunTriggerRequest,
)
from app.crud.crud_pipeline import (
    get_pipelines,
    get_pipelines_with_stats,
    get_pipeline,
)
from app.crud.crud_run import get_runs_by_pipeline
from app.core.exceptions import EntityNotFoundError

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("", response_model=List[PipelineWithStatsResponse])
def list_pipelines(db: Session = Depends(get_db)):
    """Retrieve all registered pipelines with computed execution statistics."""
    return get_pipelines_with_stats(db)


@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline_details(pipeline_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed information for a specific pipeline."""
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        raise EntityNotFoundError("Pipeline", pipeline_id)
    return pipeline


@router.get("/{pipeline_id}/runs", response_model=List[PipelineRunResponse])
def get_pipeline_runs(
    pipeline_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve execution history for a specific pipeline."""
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        raise EntityNotFoundError("Pipeline", pipeline_id)
    return get_runs_by_pipeline(db, pipeline_id, skip=skip, limit=limit)


@router.post("/{pipeline_id}/runs", response_model=PipelineRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_pipeline_run(
    pipeline_id: str,
    body: PipelineRunTriggerRequest,
    db: Session = Depends(get_db),
):
    """
    Trigger a live demo pipeline execution with one of the 7 deterministic test scenarios:
    - success
    - missing_records
    - duplicate_orders
    - null_values
    - invalid_formats
    - schema_mismatch
    - pipeline_failure
    """
    from app.etl.pipeline_runner import PipelineRunner
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        raise EntityNotFoundError("Pipeline", pipeline_id)
    
    run = PipelineRunner.execute(db=db, pipeline_id=pipeline_id, scenario=body.scenario)
    return run

