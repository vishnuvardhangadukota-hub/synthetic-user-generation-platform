from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate

class ExperimentService:
    @staticmethod
    def create_experiment(db: Session, schema: ExperimentCreate) -> Experiment:
        db_exp = Experiment(
            name=schema.name,
            product_name=schema.product_name,
            product_description=schema.product_description,
            target_audience=schema.target_audience,
            research_objectives=schema.research_objectives,
            number_of_personas=schema.number_of_personas
        )
        db.add(db_exp)
        db.commit()
        db.refresh(db_exp)
        return db_exp

    @staticmethod
    def get_experiment_by_id(db: Session, experiment_id: str) -> Optional[Experiment]:
        return db.query(Experiment).filter(Experiment.id == experiment_id).first()

    @staticmethod
    def get_all_experiments(db: Session, skip: int = 0, limit: int = 100) -> List[Experiment]:
        return db.query(Experiment).order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_experiment(db: Session, experiment_id: str, schema: ExperimentUpdate) -> Optional[Experiment]:
        db_exp = ExperimentService.get_experiment_by_id(db, experiment_id)
        if not db_exp:
            return None
        
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_exp, key, value)

        db.commit()
        db.refresh(db_exp)
        return db_exp

    @staticmethod
    def delete_experiment(db: Session, experiment_id: str) -> bool:
        db_exp = ExperimentService.get_experiment_by_id(db, experiment_id)
        if not db_exp:
            return False
        
        db.delete(db_exp)
        db.commit()
        return True
