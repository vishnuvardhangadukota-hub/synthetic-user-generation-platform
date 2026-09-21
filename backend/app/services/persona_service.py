from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate

class PersonaService:
    @staticmethod
    def create_persona(db: Session, experiment_id: str, data: Dict[str, Any], is_synthetic_test_data: bool = False) -> Persona:
        db_persona = Persona(
            experiment_id=experiment_id,
            name=data.get("name", "Unknown Persona"),
            age=data.get("age", 25),
            occupation=data.get("occupation", "Unspecified"),
            location=data.get("location", "Hyderabad"),
            demographics=data.get("demographics", {}),
            personality_traits=data.get("personality_traits", []),
            behavioral_patterns=data.get("behavioral_patterns", []),
            psychological_profile=data.get("psychological_profile", {}),
            preferences=data.get("preferences", {}),
            opinions=data.get("opinions", {}),
            memory_summary=data.get("memory_summary", ""),
            is_synthetic_test_data=is_synthetic_test_data
        )
        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)
        return db_persona

    @staticmethod
    def save_personas_bulk(db: Session, experiment_id: str, personas_data: List[Dict[str, Any]], is_synthetic_test_data: bool = False) -> List[Persona]:
        created_personas = []
        for data in personas_data:
            db_persona = Persona(
                experiment_id=experiment_id,
                name=data.get("name", "Unknown Persona"),
                age=data.get("age", 25),
                occupation=data.get("occupation", "Unspecified"),
                location=data.get("location", "Hyderabad"),
                demographics=data.get("demographics", {}),
                personality_traits=data.get("personality_traits", []),
                behavioral_patterns=data.get("behavioral_patterns", []),
                psychological_profile=data.get("psychological_profile", {}),
                preferences=data.get("preferences", {}),
                opinions=data.get("opinions", {}),
                memory_summary=data.get("memory_summary", ""),
                is_synthetic_test_data=is_synthetic_test_data
            )
            db.add(db_persona)
            created_personas.append(db_persona)

        db.commit()
        for p in created_personas:
            db.refresh(p)
        return created_personas

    @staticmethod
    def get_persona_by_id(db: Session, persona_id: str) -> Optional[Persona]:
        return db.query(Persona).filter(Persona.id == persona_id).first()

    @staticmethod
    def get_personas_by_experiment(db: Session, experiment_id: str) -> List[Persona]:
        return db.query(Persona).filter(Persona.experiment_id == experiment_id).order_by(Persona.created_at.asc()).all()

    @staticmethod
    def delete_persona(db: Session, persona_id: str) -> bool:
        db_persona = PersonaService.get_persona_by_id(db, persona_id)
        if not db_persona:
            return False
        
        db.delete(db_persona)
        db.commit()
        return True
