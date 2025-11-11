"""
Script automatique pour exécuter la migration V2 avec suppression des aides factices
Usage: python run_migration.py
"""

import asyncio
import sys
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Importer la classe de migration
from migrate_to_v2 import MigrationV2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


async def main():
    """Exécute la migration automatiquement"""
    
    logger.info("=" * 70)
    logger.info("🚀 MIGRATION AUTOMATIQUE V2 - SUPPRESSION AIDES FACTICES")
    logger.info("=" * 70)
    
    try:
        # Connexion MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'agrisubv_db')
        
        logger.info(f"\n📡 Connexion à MongoDB...")
        logger.info(f"   Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Vérifier la connexion
        await db.command('ping')
        logger.info("   ✅ Connexion réussie")
        
        # Compter les aides avant migration
        count_before = await db.aides.count_documents({})
        logger.info(f"\n📊 État initial:")
        logger.info(f"   - Aides dans la collection: {count_before}")
        
        # Créer l'instance de migration
        migration = MigrationV2(db)
        
        # Exécuter la migration avec suppression automatique
        logger.info(f"\n🔄 Lancement de la migration...")
        logger.info(f"   ⚠️  MODE: Suppression des aides factices ACTIVÉ")
        
        result = await migration.migrate_all(clean_fake_aids=True)
        
        # Afficher le résumé
        logger.info("\n" + "=" * 70)
        logger.info("📊 RÉSUMÉ DE LA MIGRATION")
        logger.info("=" * 70)
        
        if result['success']:
            logger.info(f"✅ Migration réussie !")
            logger.info(f"\n📈 Statistiques:")
            logger.info(f"   - Total aides traitées: {result['total_old']}")
            logger.info(f"   - Aides factices détectées: {result['total_fake']}")
            logger.info(f"   - Aides factices supprimées: {result['fake_deleted']}")
            logger.info(f"   - Aides PAC réelles: {result['total_real']}")
            logger.info(f"   - Aides migrées vers V2: {result['total_migrated']}")
            logger.info(f"   - Erreurs: {result['errors']}")
            
            # État final
            count_aides = await db.aides.count_documents({})
            count_v2 = await db.aides_v2.count_documents({})
            
            logger.info(f"\n📊 État final des collections:")
            logger.info(f"   - Collection 'aides': {count_aides} documents")
            logger.info(f"   - Collection 'aides_v2': {count_v2} documents")
            
            # Statistiques détaillées
            if result.get('stats'):
                logger.info(f"\n📊 Répartition par source:")
                for source, count in result['stats']['by_source'].items():
                    logger.info(f"   - {source}: {count}")
                
                if result['stats'].get('productions'):
                    logger.info(f"\n🌾 Productions détectées:")
                    for prod, count in sorted(
                        result['stats']['productions'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]:  # Top 5
                        logger.info(f"   - {prod}: {count}")
                
                if result['stats'].get('projets'):
                    logger.info(f"\n🎯 Projets détectés:")
                    for proj, count in sorted(
                        result['stats']['projets'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]:  # Top 5
                        logger.info(f"   - {proj}: {count}")
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 70)
            
            logger.info("\n📝 Prochaines étapes:")
            logger.info("   1. Vérifier les données dans MongoDB")
            logger.info("   2. Tester les nouveaux endpoints V2")
            logger.info("   3. Importer les aides Aides-Territoires (dès réception clé API)")
            
            return_code = 0
        else:
            logger.error("❌ La migration a échoué")
            return_code = 1
        
        # Fermeture connexion
        client.close()
        logger.info("\n👋 Connexion MongoDB fermée")
        
        return return_code
        
    except Exception as e:
        logger.error(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        return_code = asyncio.run(main())
        sys.exit(return_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Migration interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)
