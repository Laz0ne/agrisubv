"""
Script de migration des aides existantes vers le modèle V2

Fonctionnalités:
- Détecte et filtre les aides factices (source='manual')
- Migre uniquement les aides PAC réelles vers le nouveau schéma V2
- Option --clean-fake-aids pour supprimer les aides factices de la collection originale

Usage:
    python migrate_to_v2.py                    # Migration sans suppression
    python migrate_to_v2.py --clean-fake-aids  # Migration avec suppression des aides factices
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from datetime import datetime, timezone

# Import des modèles V2
from models_v2 import (
    AideAgricoleV2, CriteresEligibilite, MontantAide,
    TypeProduction, TypeProjet, StatutJuridique, TypeMontant
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


class MigrationV2:
    """Classe pour gérer la migration vers le modèle V2"""
    
    # Mapping des productions depuis l'ancien format
    PRODUCTION_MAPPING = {
        "Céréales": TypeProduction.CEREALES,
        "Maraîchage": TypeProduction.MARAICHAGE,
        "Viticulture": TypeProduction.VITICULTURE,
        "Arboriculture": TypeProduction.ARBORICULTURE,
        "Élevage": TypeProduction.ELEVAGE_BOVIN,
        "Élevage bovin": TypeProduction.ELEVAGE_BOVIN,
        "Élevage ovin": TypeProduction.ELEVAGE_OVIN,
        "Élevage caprin": TypeProduction.ELEVAGE_CAPRIN,
        "Élevage porcin": TypeProduction.ELEVAGE_PORCIN,
        "Élevage avicole": TypeProduction.ELEVAGE_AVICOLE,
        "Élevage laitier": TypeProduction.ELEVAGE_LAITIER,
        "Grandes cultures": TypeProduction.GRANDES_CULTURES,
        "Horticulture": TypeProduction.HORTICULTURE,
        "Apiculture": TypeProduction.APICULTURE,
    }
    
    # Mapping des projets depuis les tags
    PROJET_KEYWORDS = {
        TypeProjet.INSTALLATION: ["installation", "jeune", "dja", "reprise"],
        TypeProjet.CONVERSION_BIO: ["bio", "conversion", "agriculture biologique"],
        TypeProjet.MODERNISATION: ["modernisation", "rénovation", "amélioration"],
        TypeProjet.DIVERSIFICATION: ["diversification", "agrotourisme", "transformation"],
        TypeProjet.IRRIGATION: ["irrigation", "eau", "goutte-à-goutte"],
        TypeProjet.BATIMENT: ["bâtiment", "construction", "aménagement"],
        TypeProjet.MATERIEL: ["matériel", "équipement", "tracteur"],
        TypeProjet.ENERGIE: ["énergie", "méthanisation", "photovoltaïque", "biogaz"],
        TypeProjet.ENVIRONNEMENT: ["environnement", "biodiversité", "agroforesterie", "haie"],
        TypeProjet.FORMATION: ["formation", "conseil", "accompagnement"],
        TypeProjet.COMMERCIALISATION: ["circuit court", "vente directe", "marché"],
        TypeProjet.NUMERIQUE: ["numérique", "robot", "automatisation", "précision"],
        TypeProjet.BIEN_ETRE_ANIMAL: ["bien-être animal", "animal"],
    }
    
    # Mapping des statuts
    STATUT_MAPPING = {
        "Exploitation individuelle": StatutJuridique.INDIVIDUEL,
        "EARL": StatutJuridique.EARL,
        "GAEC": StatutJuridique.GAEC,
        "SCEA": StatutJuridique.SCEA,
        "SA": StatutJuridique.SA,
        "CUMA": StatutJuridique.CUMA,
        "Coopérative": StatutJuridique.COOPERATIVE,
    }
    
    def __init__(self, db):
        self.db = db
    
    def is_fake_aide(self, aide: Dict[str, Any]) -> bool:
        """
        Détecte si une aide est factice (test)
        Les 11 premières aides manuelles sont considérées comme factices
        """
        # Critère 1: Source manuelle
        source = aide.get('source', 'manual')
        if source != 'manual':
            return False
        
        # Critère 2: Pas d'aid_id réel ou aid_id commençant par 'test_' ou 'fake_'
        aid_id = aide.get('aid_id', '')
        if aid_id.startswith('test_') or aid_id.startswith('fake_'):
            return True
        
        # Critère 3: Titre contenant "test" ou "exemple"
        titre = aide.get('titre', '').lower()
        if 'test' in titre or 'exemple' in titre or 'factice' in titre:
            return True
        
        return True  # Par défaut, les aides manuelles sans critères clairs sont considérées comme factices
    
    def detect_productions(self, aide_old: Dict[str, Any]) -> List[TypeProduction]:
        """Détecte les types de production depuis l'ancienne aide"""
        productions = []
        
        # Depuis le champ productions
        for prod_str in aide_old.get('productions', []):
            if prod_str in self.PRODUCTION_MAPPING:
                prod_type = self.PRODUCTION_MAPPING[prod_str]
                if prod_type not in productions:
                    productions.append(prod_type)
        
        # Depuis les tags
        tags = aide_old.get('criteres_mous_tags', [])
        titre = aide_old.get('titre', '').lower()
        
        for tag in tags + [titre]:
            tag_lower = str(tag).lower()
            if 'céréale' in tag_lower or 'blé' in tag_lower:
                if TypeProduction.CEREALES not in productions:
                    productions.append(TypeProduction.CEREALES)
            elif 'maraîchage' in tag_lower or 'légume' in tag_lower:
                if TypeProduction.MARAICHAGE not in productions:
                    productions.append(TypeProduction.MARAICHAGE)
            elif 'viticul' in tag_lower or 'vigne' in tag_lower:
                if TypeProduction.VITICULTURE not in productions:
                    productions.append(TypeProduction.VITICULTURE)
            elif 'bovin' in tag_lower or 'vache' in tag_lower:
                if TypeProduction.ELEVAGE_BOVIN not in productions:
                    productions.append(TypeProduction.ELEVAGE_BOVIN)
            elif 'ovin' in tag_lower or 'mouton' in tag_lower or 'brebis' in tag_lower:
                if TypeProduction.ELEVAGE_OVIN not in productions:
                    productions.append(TypeProduction.ELEVAGE_OVIN)
            elif 'caprin' in tag_lower or 'chèvre' in tag_lower:
                if TypeProduction.ELEVAGE_CAPRIN not in productions:
                    productions.append(TypeProduction.ELEVAGE_CAPRIN)
        
        return productions
    
    def detect_projets(self, aide_old: Dict[str, Any]) -> List[TypeProjet]:
        """Détecte les types de projets depuis les tags et le titre"""
        projets = []
        
        tags = aide_old.get('criteres_mous_tags', [])
        titre = aide_old.get('titre', '').lower()
        description = aide_old.get('conditions_clefs', '').lower()
        
        all_text = ' '.join([str(t).lower() for t in tags] + [titre, description])
        
        for type_projet, keywords in self.PROJET_KEYWORDS.items():
            if any(kw in all_text for kw in keywords):
                if type_projet not in projets:
                    projets.append(type_projet)
        
        return projets
    
    def detect_statuts(self, aide_old: Dict[str, Any]) -> List[StatutJuridique]:
        """Détecte les statuts juridiques depuis l'ancienne aide"""
        statuts = []
        
        for statut_str in aide_old.get('statuts', []):
            if statut_str in self.STATUT_MAPPING:
                statut = self.STATUT_MAPPING[statut_str]
                if statut not in statuts:
                    statuts.append(statut)
        
        # Si aucun statut défini, tous sont acceptés
        if not statuts:
            statuts = list(StatutJuridique)
        
        return statuts
    
    def migrate_criteres_durs(self, aide_old: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les critères durs de l'ancien format
        Note: Conservation du format d'expression pour compatibilité
        """
        return aide_old.get('criteres_durs_expr', {})
    
    def migrate_aide(self, aide_old: Dict[str, Any]) -> AideAgricoleV2:
        """Migre une aide de l'ancien format vers V2"""
        
        # Détection intelligente
        productions = self.detect_productions(aide_old)
        projets = self.detect_projets(aide_old)
        statuts = self.detect_statuts(aide_old)
        
        # Détermination de la source
        source = aide_old.get('source', 'manual')
        if not source or source == '':
            source = 'manual'
        
        # Construction des critères d'éligibilité
        criteres = CriteresEligibilite(
            regions=aide_old.get('regions', []),
            departements=aide_old.get('departements', []),
            types_production=productions,
            types_projets=projets,
            statuts_juridiques=statuts,
            labels_requis=aide_old.get('labels', [])
        )
        
        # Détermination du type de montant
        type_montant = TypeMontant.FORFAITAIRE
        if aide_old.get('taux_min_pct') or aide_old.get('taux_max_pct'):
            type_montant = TypeMontant.POURCENTAGE
        elif 'ha' in aide_old.get('titre', '').lower() or 'hectare' in aide_old.get('titre', '').lower():
            type_montant = TypeMontant.SURFACE
        
        # Construction du montant
        montant = MontantAide(
            type_montant=type_montant,
            montant_min=aide_old.get('montant_min_eur'),
            montant_max=aide_old.get('montant_max_eur'),
            taux_min=aide_old.get('taux_min_pct'),
            taux_max=aide_old.get('taux_max_pct'),
            plafond=aide_old.get('plafond_eur')
        )
        
        # Détermination du statut
        expiree = aide_old.get('expiree', False)
        statut = 'expiree' if expiree else 'active'
        
        # Construction de l'aide V2
        aide_v2 = AideAgricoleV2(
            aid_id=aide_old.get('aid_id'),
            titre=aide_old.get('titre', 'Aide sans titre'),
            description=aide_old.get('conditions_clefs', ''),
            organisme=aide_old.get('organisme', 'Non spécifié'),
            programme=aide_old.get('programme', ''),
            source=source,
            source_url=aide_old.get('source_url', ''),
            derniere_maj=aide_old.get('derniere_maj', datetime.now(timezone.utc).isoformat()),
            date_debut=aide_old.get('date_ouverture'),
            date_fin=aide_old.get('date_limite'),
            date_limite_depot=aide_old.get('date_limite'),
            statut=statut,
            criteres=criteres,
            montant=montant,
            conditions_eligibilite=aide_old.get('conditions_clefs', ''),
            lien_officiel=aide_old.get('lien_officiel', ''),
            confiance=aide_old.get('confiance', 1.0),
            tags=aide_old.get('criteres_mous_tags', []),
            raw_data={'old_criteres_durs': aide_old.get('criteres_durs_expr', {})}
        )
        
        return aide_v2
    
    async def migrate_all(self, clean_fake_aids: bool = False) -> Dict[str, Any]:
        """Migre toutes les aides existantes vers V2"""
        
        logger.info("=" * 60)
        logger.info("MIGRATION DES AIDES VERS LE MODÈLE V2")
        logger.info("=" * 60)
        
        # Récupération des aides existantes
        logger.info("\n📥 Récupération des aides existantes...")
        aides_old = await self.db.aides.find({}).to_list(length=1000)
        logger.info(f"   ✅ {len(aides_old)} aides trouvées")
        
        # Statistiques par source
        sources = {}
        for aide in aides_old:
            source = aide.get('source', 'manual')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info(f"\n📊 Répartition par source:")
        for source, count in sources.items():
            logger.info(f"   - {source}: {count} aides")
        
        # Séparer les aides factices des aides réelles
        aides_factices = []
        aides_reelles = []
        
        for aide in aides_old:
            if self.is_fake_aide(aide):
                aides_factices.append(aide)
            else:
                aides_reelles.append(aide)
        
        logger.info(f"\n🔍 Analyse des aides:")
        logger.info(f"   - Aides factices détectées: {len(aides_factices)}")
        logger.info(f"   - Aides réelles (PAC): {len(aides_reelles)}")
        
        # Suppression des aides factices si demandé
        fake_deleted_count = 0
        if clean_fake_aids and aides_factices:
            logger.warning(f"\n⚠️  SUPPRESSION DES AIDES FACTICES EN COURS...")
            fake_ids = [aide.get('aid_id') or str(aide.get('_id')) for aide in aides_factices]
            result = await self.db.aides.delete_many({
                '$or': [
                    {'aid_id': {'$in': fake_ids}},
                    {'source': 'manual'}
                ]
            })
            fake_deleted_count = result.deleted_count
            logger.info(f"   ✅ {fake_deleted_count} aides factices supprimées de la collection 'aides'")
        
        # Migrer seulement les aides réelles
        aides_to_migrate = aides_reelles
        logger.info(f"\n🔄 Migration de {len(aides_to_migrate)} aides réelles...")
        aides_v2 = []
        erreurs = []
        
        for i, aide_old in enumerate(aides_to_migrate, 1):
            try:
                aide_v2 = self.migrate_aide(aide_old)
                aides_v2.append(aide_v2)
                logger.info(f"   ✅ [{i}/{len(aides_to_migrate)}] {aide_v2.titre[:50]}")
            except Exception as e:
                logger.error(f"   ❌ [{i}/{len(aides_to_migrate)}] Erreur: {e}")
                erreurs.append({
                    'aid_id': aide_old.get('aid_id', 'unknown'),
                    'titre': aide_old.get('titre', 'unknown'),
                    'erreur': str(e)
                })
        
        # Sauvegarde dans la collection V2
        logger.info(f"\n💾 Sauvegarde dans la collection 'aides_v2'...")
        
        # Supprimer la collection V2 si elle existe
        await self.db.aides_v2.delete_many({})
        
        # Insertion des aides migrées
        inserted_count = 0
        for aide_v2 in aides_v2:
            try:
                aide_dict = aide_v2.model_dump()
                await self.db.aides_v2.insert_one(aide_dict)
                inserted_count += 1
            except Exception as e:
                logger.error(f"   ❌ Erreur insertion {aide_v2.aid_id}: {e}")
                erreurs.append({
                    'aid_id': aide_v2.aid_id,
                    'titre': aide_v2.titre,
                    'erreur': f"Insertion: {str(e)}"
                })
        
        logger.info(f"   ✅ {inserted_count} aides insérées dans aides_v2")
        
        # Validation post-migration
        logger.info(f"\n✅ Validation post-migration...")
        count_v2 = await self.db.aides_v2.count_documents({})
        logger.info(f"   - Aides dans aides_v2: {count_v2}")
        
        # Statistiques V2
        logger.info(f"\n📊 Statistiques V2:")
        
        # Par statut
        stats_statut = {}
        for aide in aides_v2:
            stats_statut[aide.statut] = stats_statut.get(aide.statut, 0) + 1
        logger.info(f"   Par statut:")
        for statut, count in stats_statut.items():
            logger.info(f"      - {statut}: {count}")
        
        # Par source
        stats_source = {}
        for aide in aides_v2:
            stats_source[aide.source] = stats_source.get(aide.source, 0) + 1
        logger.info(f"   Par source:")
        for source, count in stats_source.items():
            logger.info(f"      - {source}: {count}")
        
        # Productions détectées
        productions_count = {}
        for aide in aides_v2:
            for prod in aide.criteres.types_production:
                productions_count[prod.value] = productions_count.get(prod.value, 0) + 1
        logger.info(f"   Productions détectées:")
        for prod, count in sorted(productions_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"      - {prod}: {count}")
        
        # Projets détectés
        projets_count = {}
        for aide in aides_v2:
            for proj in aide.criteres.types_projets:
                projets_count[proj.value] = projets_count.get(proj.value, 0) + 1
        logger.info(f"   Projets détectés:")
        for proj, count in sorted(projets_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"      - {proj}: {count}")
        
        # Résumé final
        logger.info(f"\n" + "=" * 60)
        logger.info(f"RÉSUMÉ DE LA MIGRATION")
        logger.info(f"=" * 60)
        if clean_fake_aids:
            logger.info(f"🗑️  Aides factices supprimées: {fake_deleted_count}")
        else:
            logger.info(f"⚠️  Aides factices détectées (non supprimées): {len(aides_factices)}")
        logger.info(f"✅ Aides PAC migrées avec succès: {len(aides_v2)}")
        logger.info(f"❌ Erreurs: {len(erreurs)}")
        logger.info(f"💾 Aides dans collection V2: {count_v2}")
        if not clean_fake_aids:
            count_aides = await self.db.aides.count_documents({})
            logger.info(f"📋 Aides dans collection originale: {count_aides}")
        else:
            count_aides = await self.db.aides.count_documents({})
            logger.info(f"📋 Aides dans collection originale: {count_aides} (après suppression)")
        logger.info(f"=" * 60)
        
        if erreurs:
            logger.warning(f"\n⚠️  Erreurs détectées:")
            for err in erreurs:
                logger.warning(f"   - {err['aid_id']}: {err['erreur']}")
        
        return {
            'success': True,
            'total_old': len(aides_old),
            'total_fake': len(aides_factices),
            'fake_deleted': fake_deleted_count,
            'total_real': len(aides_reelles),
            'total_migrated': len(aides_v2),
            'total_inserted': inserted_count,
            'errors': len(erreurs),
            'errors_details': erreurs,
            'stats': {
                'by_status': stats_statut,
                'by_source': stats_source,
                'productions': productions_count,
                'projets': projets_count
            }
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migration des aides vers le modèle V2')
    parser.add_argument('--clean-fake-aids', action='store_true',
                       help='Supprimer les 11 aides factices de la collection aides')
    args = parser.parse_args()
    
    if args.clean_fake_aids:
        logger.warning("\n⚠️  MODE NETTOYAGE ACTIVÉ - Les aides factices seront supprimées !")
        logger.warning("⚠️  Cette opération est irréversible !")
        confirm = input("Confirmer la suppression des aides factices ? (oui/non): ")
        if confirm.lower() != 'oui':
            logger.info("❌ Opération annulée")
            sys.exit(0)
    
    async def run_migration():
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'agrisubv_db')]
        
        migration = MigrationV2(db)
        result = await migration.migrate_all(clean_fake_aids=args.clean_fake_aids)
        
        client.close()
        return result
    
    result = asyncio.run(run_migration())
    sys.exit(0 if result['success'] else 1)
