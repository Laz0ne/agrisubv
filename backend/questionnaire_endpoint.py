"""
Endpoint pour servir la configuration du questionnaire dynamique
Génère le questionnaire optimal basé sur l'analyse des 507 aides
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

async def get_questionnaire_config():
    """
    Retourne la configuration complète du questionnaire dynamique
    """
    try:
        # Charger le fichier JSON
        config_path = Path(__file__).parent / "questionnaire_config.json"
        
        if not config_path.exists():
            logger.error("❌ Fichier questionnaire_config.json introuvable")
            return {
                "status": "error",
                "message": "Configuration du questionnaire introuvable"
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info("✅ Configuration du questionnaire chargée avec succès")
        
        return {
            "status": "success",
            "config": config,
            "stats": {
                "total_sections": len(config.get("sections", [])),
                "total_questions": sum(
                    len(section.get("questions", []))
                    for section in config.get("sections", [])
                ),
                "estimated_time_minutes": config.get("metadata", {}).get("estimated_time_minutes", 5)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur chargement questionnaire: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
