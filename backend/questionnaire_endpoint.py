"""
Endpoint pour servir la configuration du questionnaire dynamique
Génère le questionnaire optimal basé sur l'analyse des 507 aides
"""

import json
import logging
from pathlib import Path

from questionnaire_engine import QuestionnaireEngine

logger = logging.getLogger(__name__)

# Instance partagée du moteur
_engine = QuestionnaireEngine()


async def get_questionnaire_config(db=None):
    """
    Retourne la configuration complète du questionnaire.
    Si la base de données est disponible, enrichit les options depuis les aides réelles.
    Retombe sur le fichier JSON statique en cas d'erreur.
    """
    if db is not None:
        try:
            state = await _engine.start_session(db)
            question = await _engine.get_next_question(db, state)

            # Construire une config compatible avec l'ancien format
            return {
                "status": "success",
                "config": {
                    "engine": "dynamic",
                    "session_id": state.session_id,
                    "total_aids": state.total_aids_count,
                    "first_question": question,
                },
                "stats": {
                    "total_sections": 1,
                    "total_questions": len(_engine.CRITERION_DEFINITIONS),
                    "estimated_time_minutes": 3,
                },
            }
        except Exception as e:
            logger.warning(f"⚠️ Moteur dynamique indisponible, fallback JSON statique: {e}")

    # Fallback : fichier JSON statique
    return await _load_static_config()


async def _load_static_config() -> dict:
    """Charge le fichier questionnaire_config.json statique."""
    try:
        config_path = Path(__file__).parent / "questionnaire_config.json"

        if not config_path.exists():
            logger.error("❌ Fichier questionnaire_config.json introuvable")
            return {
                "status": "error",
                "message": "Configuration du questionnaire introuvable",
            }

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        logger.info("✅ Configuration du questionnaire chargée depuis JSON statique")

        return {
            "status": "success",
            "config": config,
            "stats": {
                "total_sections": len(config.get("sections", [])),
                "total_questions": sum(
                    len(section.get("questions", []))
                    for section in config.get("sections", [])
                ),
                "estimated_time_minutes": config.get("metadata", {}).get(
                    "estimated_time_minutes", 5
                ),
            },
        }

    except Exception as e:
        logger.error(f"❌ Erreur chargement questionnaire: {e}")
        import traceback

        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
        }

