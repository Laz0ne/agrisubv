"""
Moteur de matching V2 pour AgriSubv
Calcule le score de compatibilité entre un profil agriculteur et une aide
"""

from typing import List, Optional, Tuple
from datetime import datetime, timezone
from models_v2 import (
    AideAgricoleV2, ProfilAgriculteur, ResultatMatching, 
    DetailCritere, TypeProduction, TypeProjet, StatutMatching
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Moteur de matching avec scoring pondéré et explications détaillées
    """
    
    # Poids des catégories de critères (total = 100)
    POIDS_LOCALISATION = 25.0
    POIDS_PRODUCTION = 20.0
    POIDS_PROJET = 15.0
    POIDS_STATUT = 10.0
    POIDS_AGE = 10.0
    POIDS_SURFACE = 10.0
    POIDS_LABELS = 10.0
    
    # Seuil d'éligibilité (score minimum)
    SEUIL_ELIGIBILITE = 60.0

    # Tags indiquant qu'une aide est hors secteur agricole
    NON_AGRICULTURAL_TAGS = {
        'sport', 'sports', 'culture', 'patrimoine', 'tourisme',
        'loisirs', 'spectacle', 'musique', 'théâtre', 'cinéma',
        'santé', 'médical', 'social', 'urbanisme', 'transport',
        'numérique', 'industrie', 'commerce', 'artisanat',
    }

    # Tags indiquant qu'une aide est agricole
    AGRICULTURAL_TAGS = {
        'agriculture', 'agricole', 'rural', 'exploitation', 'élevage',
        'bio', 'irrigation', 'foncier', 'pac', 'maec', 'pcae',
        'développement-rural', 'nature-environnement', 'eau-assainissement',
        'energie', 'formation-emploi',
    }
    
    def __init__(self):
        """Initialise le moteur de matching"""
        pass
    
    def calculate_match(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> ResultatMatching:
        """
        Calcule le score de matching entre une aide et un profil
        
        Args:
            aide: L'aide agricole à évaluer
            profil: Le profil de l'agriculteur
            
        Returns:
            ResultatMatching avec score, détails et recommandations
        """
        details_criteres: List[DetailCritere] = []
        score_total = 0.0
        criteres_bloquants_ko: List[str] = []

        # 0.bis Vérification date limite de dépôt
        if aide.date_limite_depot:
            try:
                deadline = datetime.fromisoformat(str(aide.date_limite_depot).replace('Z', '+00:00'))
                if deadline < datetime.now(timezone.utc):
                    details_criteres.append(DetailCritere(
                        nom="Date limite",
                        valide=False,
                        bloquant=True,
                        points=0.0,
                        points_max=0.0,
                        explication=f"❌ Date limite de dépôt dépassée ({aide.date_limite_depot})"
                    ))
                    criteres_bloquants_ko.append("Date limite dépassée")
            except (ValueError, TypeError):
                pass

        # 0. Vérification du public cible (targeted_audiences)
        score_public, detail_public, bloquant_public = self._evaluer_public_cible(aide, profil)
        details_criteres.extend(detail_public)
        if bloquant_public:
            criteres_bloquants_ko.append("Public cible")
        else:
            score_total += score_public
        
        # 1. Critères géographiques (25 points)
        score_geo, detail_geo, bloquant_geo = self._evaluer_localisation(aide, profil)
        details_criteres.extend(detail_geo)
        if bloquant_geo:
            criteres_bloquants_ko.append("Localisation")
        else:
            score_total += score_geo
        
        # 2. Critères de production (20 points)
        score_prod, detail_prod, bloquant_prod = self._evaluer_production(aide, profil)
        details_criteres.extend(detail_prod)
        if bloquant_prod:
            criteres_bloquants_ko.append("Production")
        else:
            score_total += score_prod
        
        # 3. Critères de projet (15 points)
        score_projet, detail_projet = self._evaluer_projet(aide, profil)
        details_criteres.extend(detail_projet)
        score_total += score_projet
        
        # 4. Critères de statut juridique (10 points)
        score_statut, detail_statut, bloquant_statut = self._evaluer_statut(aide, profil)
        details_criteres.extend(detail_statut)
        if bloquant_statut:
            criteres_bloquants_ko.append("Statut juridique")
        else:
            score_total += score_statut
        
        # 5. Critères d'âge (10 points)
        score_age, detail_age, bloquant_age = self._evaluer_age(aide, profil)
        details_criteres.extend(detail_age)
        if bloquant_age:
            criteres_bloquants_ko.append("Âge")
        else:
            score_total += score_age
        
        # 6. Critères de surface (10 points)
        score_surface, detail_surface, bloquant_surface = self._evaluer_surface(aide, profil)
        details_criteres.extend(detail_surface)
        if bloquant_surface:
            criteres_bloquants_ko.append("Surface")
        else:
            score_total += score_surface
        
        # 7. Critères de labels (10 points)
        score_labels, detail_labels = self._evaluer_labels(aide, profil)
        details_criteres.extend(detail_labels)
        score_total += score_labels
        
        # Calcul du score final
        score_final = min(100.0, max(0.0, score_total))
        
        # Si critères bloquants non validés, pénalité proportionnelle (max -60)
        if criteres_bloquants_ko:
            penalty = min(len(criteres_bloquants_ko) * 15, 60)
            score_final = max(0.0, score_final - penalty)
        
        # Éligibilité : score >= seuil ET aucun critère bloquant échoué
        eligible = score_final >= self.SEUIL_ELIGIBILITE and not criteres_bloquants_ko
        
        # Comptage des critères
        criteres_valides = sum(1 for d in details_criteres if d.valide)
        criteres_total = len(details_criteres)
        
        # Estimation du montant
        montant_min, montant_max = self._estimer_montant(aide, profil)
        
        # Génération du résumé et recommandations
        resume = self._generer_resume(eligible, score_final, criteres_bloquants_ko)
        recommandations = self._generer_recommandations(aide, profil, details_criteres, criteres_bloquants_ko)
        
        # Statut de matching à 4 niveaux
        statut_matching = self._get_statut_matching(score_final, eligible, criteres_bloquants_ko, details_criteres)
        
        return ResultatMatching(
            aide_id=aide.aid_id,
            profil_id=profil.profil_id,
            score=score_final,
            eligible=eligible,
            details_criteres=details_criteres,
            criteres_valides=criteres_valides,
            criteres_total=criteres_total,
            criteres_bloquants_ko=criteres_bloquants_ko,
            montant_estime_min=montant_min,
            montant_estime_max=montant_max,
            resume=resume,
            recommandations=recommandations,
            statut_matching=statut_matching
        )
    
    def _get_statut_matching(
        self,
        score: float,
        eligible: bool,
        criteres_bloquants_ko: list,
        details_criteres: list
    ) -> str:
        """
        Classifie le résultat du matching en 4 niveaux :
        - tres_probable : éligible ET score >= 80
        - probable : éligible ET score >= 60
        - a_verifier : score >= 40 avec au plus 1 critère bloquant échoué
                       (inclut les aides presque éligibles)
        - non_retenue : 2+ critères bloquants échoués, ou score < 40
        """
        if eligible and score >= 80.0:
            return StatutMatching.TRES_PROBABLE.value
        if eligible and score >= 60.0:
            return StatutMatching.PROBABLE.value
        # Presque éligible : score >= 40 avec au plus 1 critère bloquant échoué
        if score >= 40.0 and len(criteres_bloquants_ko) <= 1:
            return StatutMatching.A_VERIFIER.value
        return StatutMatching.NON_RETENUE.value
    
    def _evaluer_public_cible(
        self,
        aide: AideAgricoleV2,
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere], bool]:
        """Évalue si l'aide est destinée aux agriculteurs via targeted_audiences"""
        details = []
        
        targeted = getattr(aide, 'targeted_audiences', []) or []
        
        # Si pas de restriction de public → vérifier les tags pour détecter les aides non-agricoles
        if not targeted:
            tags = getattr(aide, 'tags', []) or []
            tags_lower = {str(t).lower() for t in tags}

            has_non_agri = bool(tags_lower & self.NON_AGRICULTURAL_TAGS)
            has_agri = bool(tags_lower & self.AGRICULTURAL_TAGS)

            if has_non_agri and not has_agri:
                details.append(DetailCritere(
                    nom="Public cible",
                    valide=False,
                    bloquant=True,
                    points=0.0,
                    points_max=0.0,
                    explication="❌ Cette aide ne concerne pas le secteur agricole"
                ))
                return 0.0, details, True

            return 0.0, details, False
        
        # Audiences considérées comme agricoles (selon API Aides-Territoires)
        # "farmer" = exploitants agricoles, "private_person" = particuliers (inclut auto-entrepreneurs),
        # "association" = structures collectives pouvant être agricoles
        AGRICULTURAL_AUDIENCES = {"farmer", "private_person", "association"}
        
        # Vérifier si l'aide cible des agriculteurs
        targeted_set = {str(a).lower() for a in targeted}
        is_for_farmers = bool(targeted_set & AGRICULTURAL_AUDIENCES)
        
        # Si uniquement pour collectivités/organismes publics → bloquant pour exploitations agricoles
        # "commune", "epci", "department", "region" = collectivités territoriales
        # "public_org" = organismes publics, "public_cpe" = établissements publics,
        # "special" = publics spéciaux (universités, hôpitaux, etc.)
        NON_FARMER_ONLY = {"commune", "epci", "department", "region", "public_org", "public_cpe", "special"}
        is_only_non_farmer = targeted_set and not is_for_farmers and bool(targeted_set & NON_FARMER_ONLY)
        
        if is_only_non_farmer:
            public_label = ', '.join(sorted(targeted_set & NON_FARMER_ONLY))
            details.append(DetailCritere(
                nom="Public cible",
                valide=False,
                bloquant=True,
                points=0.0,
                points_max=0.0,
                explication=f"❌ Cette aide est réservée aux collectivités/organismes ({public_label}), pas aux exploitations agricoles"
            ))
            return 0.0, details, True
        
        return 0.0, details, False
    
    def _evaluer_localisation(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere], bool]:
        """Évalue les critères géographiques"""
        details = []
        score = 0.0
        bloquant = False
        
        regions = aide.criteres.regions
        departements = aide.criteres.departements
        
        # Si pas de restriction géographique, points automatiques sans ajouter de détail
        if not regions and not departements:
            return self.POIDS_LOCALISATION, details, False
        
        # Vérification région
        region_ok = False
        if regions:
            if "National" in regions or "France" in regions:
                region_ok = True
            elif profil.region in regions:
                region_ok = True
            
            if region_ok:
                details.append(DetailCritere(
                    nom="Région",
                    valide=True,
                    bloquant=True,
                    points=self.POIDS_LOCALISATION * 0.7,
                    points_max=self.POIDS_LOCALISATION * 0.7,
                    explication=f"✅ Région {profil.region} éligible"
                ))
                score += self.POIDS_LOCALISATION * 0.7
            else:
                details.append(DetailCritere(
                    nom="Région",
                    valide=False,
                    bloquant=True,
                    points=0.0,
                    points_max=self.POIDS_LOCALISATION * 0.7,
                    explication=f"❌ Région {profil.region} non éligible (régions acceptées: {', '.join(regions)})"
                ))
                bloquant = True
        
        # Vérification département
        if departements and profil.departement:
            dept_ok = profil.departement in departements
            if dept_ok:
                details.append(DetailCritere(
                    nom="Département",
                    valide=True,
                    bloquant=True,
                    points=self.POIDS_LOCALISATION * 0.3,
                    points_max=self.POIDS_LOCALISATION * 0.3,
                    explication=f"✅ Département {profil.departement} éligible"
                ))
                score += self.POIDS_LOCALISATION * 0.3
            else:
                details.append(DetailCritere(
                    nom="Département",
                    valide=False,
                    bloquant=True,
                    points=0.0,
                    points_max=self.POIDS_LOCALISATION * 0.3,
                    explication=f"❌ Département {profil.departement} non éligible (départements acceptés: {', '.join(departements)})"
                ))
                bloquant = True
        elif not departements and regions:
            # Pas de restriction de département, bonus si région OK
            if region_ok:
                details.append(DetailCritere(
                    nom="Département",
                    valide=True,
                    bloquant=False,
                    points=self.POIDS_LOCALISATION * 0.3,
                    points_max=self.POIDS_LOCALISATION * 0.3,
                    explication="✅ Aucune restriction départementale"
                ))
                score += self.POIDS_LOCALISATION * 0.3
        
        return score, details, bloquant
    
    def _evaluer_production(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere], bool]:
        """Évalue les critères de production"""
        details = []
        score = 0.0
        bloquant = False
        
        types_prod = aide.criteres.types_production
        
        # Si pas de restriction de production → tous types acceptés, points automatiques sans détail
        if not types_prod:
            return self.POIDS_PRODUCTION, details, False
        
        # Si le profil n'a pas de productions renseignées → ne pas bloquer mais donner 0 points
        if not profil.productions:
            details.append(DetailCritere(
                nom="Type de production",
                valide=False,
                bloquant=False,  # ⚠️ Ne pas bloquer si non renseigné
                points=0.0,
                points_max=self.POIDS_PRODUCTION,
                explication="⚠️ Productions non renseignées dans votre profil"
            ))
            return 0.0, details, False  # False = non bloquant
        
        # Vérification correspondance
        correspondances = [p for p in profil.productions if p in types_prod]
        
        if correspondances:
            details.append(DetailCritere(
                nom="Type de production",
                valide=True,
                bloquant=True,
                points=self.POIDS_PRODUCTION,
                points_max=self.POIDS_PRODUCTION,
                explication=f"✅ Production(s) éligible(s): {', '.join([p.value for p in correspondances])}"
            ))
            score = self.POIDS_PRODUCTION
        else:
            prod_requises = ', '.join([p.value for p in types_prod])
            prod_profil = ', '.join([p.value for p in profil.productions])
            details.append(DetailCritere(
                nom="Type de production",
                valide=False,
                bloquant=True,
                points=0.0,
                points_max=self.POIDS_PRODUCTION,
                explication=f"❌ Productions non éligibles. Requises: {prod_requises}. Vos productions: {prod_profil}"
            ))
            bloquant = True
        
        return score, details, bloquant
    
    def _evaluer_projet(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere]]:
        """Évalue les critères de projet (non bloquant)"""
        details = []
        score = 0.0
        
        types_projet = aide.criteres.types_projets
        
        # Si pas de restriction de projet, points automatiques sans détail
        if not types_projet:
            return self.POIDS_PROJET, details
        
        # Vérification correspondance
        correspondances = [p for p in profil.projets_en_cours if p in types_projet]
        
        if correspondances:
            details.append(DetailCritere(
                nom="Type de projet",
                valide=True,
                bloquant=False,
                points=self.POIDS_PROJET,
                points_max=self.POIDS_PROJET,
                explication=f"✅ Projet(s) correspondant(s): {', '.join([p.value for p in correspondances])}"
            ))
            score = self.POIDS_PROJET
        else:
            projets_requis = ', '.join([p.value for p in types_projet])
            details.append(DetailCritere(
                nom="Type de projet",
                valide=False,
                bloquant=False,
                points=0.0,
                points_max=self.POIDS_PROJET,
                explication=f"⚠️ Projets suggérés: {projets_requis}"
            ))
        
        return score, details
    
    def _evaluer_statut(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere], bool]:
        """Évalue le statut juridique"""
        details = []
        score = 0.0
        bloquant = False
        
        statuts_acceptes = aide.criteres.statuts_juridiques
        
        # Si pas de restriction de statut, points automatiques sans détail
        if not statuts_acceptes:
            return self.POIDS_STATUT, details, False
        
        # Vérification
        if profil.statut_juridique in statuts_acceptes:
            details.append(DetailCritere(
                nom="Statut juridique",
                valide=True,
                bloquant=True,
                points=self.POIDS_STATUT,
                points_max=self.POIDS_STATUT,
                explication=f"✅ Statut {profil.statut_juridique.value} accepté"
            ))
            score = self.POIDS_STATUT
        else:
            statuts_str = ', '.join([s.value for s in statuts_acceptes])
            details.append(DetailCritere(
                nom="Statut juridique",
                valide=False,
                bloquant=True,
                points=0.0,
                points_max=self.POIDS_STATUT,
                explication=f"❌ Statut {profil.statut_juridique.value} non accepté. Statuts requis: {statuts_str}"
            ))
            bloquant = True
        
        return score, details, bloquant
    
    def _evaluer_age(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere], bool]:
        """Évalue les critères d'âge"""
        details = []
        score = 0.0
        bloquant = False
        
        age_min = aide.criteres.age_min
        age_max = aide.criteres.age_max
        jeune_requis = aide.criteres.jeune_agriculteur
        
        # Si pas de restriction d'âge, points automatiques sans détail
        if age_min is None and age_max is None and jeune_requis is None:
            return self.POIDS_AGE, details, False
        
        # Si l'âge n'est pas renseigné dans le profil
        if profil.age is None and (age_min or age_max or jeune_requis):
            details.append(DetailCritere(
                nom="Âge",
                valide=False,
                bloquant=False,
                points=0.0,
                points_max=self.POIDS_AGE,
                explication="⚠️ Âge non renseigné dans le profil"
            ))
            return 0.0, details, False
        
        # Vérification jeune agriculteur
        if jeune_requis is True:
            if profil.jeune_agriculteur:
                details.append(DetailCritere(
                    nom="Jeune agriculteur",
                    valide=True,
                    bloquant=True,
                    points=self.POIDS_AGE,
                    points_max=self.POIDS_AGE,
                    explication="✅ Statut jeune agriculteur validé"
                ))
                score = self.POIDS_AGE
            else:
                details.append(DetailCritere(
                    nom="Jeune agriculteur",
                    valide=False,
                    bloquant=True,
                    points=0.0,
                    points_max=self.POIDS_AGE,
                    explication="❌ Aide réservée aux jeunes agriculteurs (< 40 ans)"
                ))
                bloquant = True
            return score, details, bloquant
        
        # Vérification âge min/max
        age_ok = True
        explication_parts = []
        
        if age_min is not None and profil.age is not None:
            if profil.age >= age_min:
                explication_parts.append(f"âge >= {age_min} ans ✅")
            else:
                age_ok = False
                explication_parts.append(f"âge < {age_min} ans requis ❌")
        
        if age_max is not None and profil.age is not None:
            if profil.age <= age_max:
                explication_parts.append(f"âge <= {age_max} ans ✅")
            else:
                age_ok = False
                explication_parts.append(f"âge > {age_max} ans maximum ❌")
        
        if age_ok:
            details.append(DetailCritere(
                nom="Âge",
                valide=True,
                bloquant=True,
                points=self.POIDS_AGE,
                points_max=self.POIDS_AGE,
                explication=f"✅ Critère d'âge respecté ({', '.join(explication_parts)})"
            ))
            score = self.POIDS_AGE
        else:
            details.append(DetailCritere(
                nom="Âge",
                valide=False,
                bloquant=True,
                points=0.0,
                points_max=self.POIDS_AGE,
                explication=f"❌ Critère d'âge non respecté ({', '.join(explication_parts)})"
            ))
            bloquant = True
        
        return score, details, bloquant
    
    def _evaluer_surface(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere], bool]:
        """Évalue les critères de surface"""
        details = []
        score = 0.0
        bloquant = False
        
        surf_min = aide.criteres.superficie_min
        surf_max = aide.criteres.superficie_max
        
        # Si pas de restriction, points automatiques sans détail
        if surf_min is None and surf_max is None:
            return self.POIDS_SURFACE, details, False
        
        surface_ok = True
        explication_parts = []
        
        if surf_min is not None:
            if profil.sau_totale >= surf_min:
                explication_parts.append(f"SAU >= {surf_min} ha ✅")
            else:
                surface_ok = False
                explication_parts.append(f"SAU < {surf_min} ha requis ❌")
        
        if surf_max is not None:
            if profil.sau_totale <= surf_max:
                explication_parts.append(f"SAU <= {surf_max} ha ✅")
            else:
                surface_ok = False
                explication_parts.append(f"SAU > {surf_max} ha maximum ❌")
        
        if surface_ok:
            details.append(DetailCritere(
                nom="Surface",
                valide=True,
                bloquant=True,
                points=self.POIDS_SURFACE,
                points_max=self.POIDS_SURFACE,
                explication=f"✅ Surface éligible: {profil.sau_totale} ha ({', '.join(explication_parts)})"
            ))
            score = self.POIDS_SURFACE
        else:
            details.append(DetailCritere(
                nom="Surface",
                valide=False,
                bloquant=True,
                points=0.0,
                points_max=self.POIDS_SURFACE,
                explication=f"❌ Surface non éligible: {profil.sau_totale} ha ({', '.join(explication_parts)})"
            ))
            bloquant = True
        
        return score, details, bloquant
    
    def _evaluer_labels(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[float, List[DetailCritere]]:
        """Évalue les labels (avec détail des labels manquants)"""
        details = []
        score = 0.0
        
        labels_requis = aide.criteres.labels_requis
        labels_bonus = aide.criteres.labels_bonus
        
        # Labels requis
        if labels_requis:
            labels_profil = [l.lower() for l in profil.labels]
            labels_ok = all(
                any(req.lower() in lp or lp in req.lower() for lp in labels_profil)
                for req in labels_requis
            )
            
            if labels_ok:
                details.append(DetailCritere(
                    nom="Labels requis",
                    valide=True,
                    bloquant=False,
                    points=self.POIDS_LABELS * 0.6,
                    points_max=self.POIDS_LABELS * 0.6,
                    explication=f"✅ Labels requis présents: {', '.join(labels_requis)}"
                ))
                score += self.POIDS_LABELS * 0.6
            else:
                # ⚠️ DÉTAILLER les labels manquants
                labels_manquants = [
                    req for req in labels_requis 
                    if not any(req.lower() in lp or lp in req.lower() for lp in labels_profil)
                ]
                details.append(DetailCritere(
                    nom="Labels requis",
                    valide=False,
                    bloquant=False,
                    points=0.0,
                    points_max=self.POIDS_LABELS * 0.6,
                    explication=f"❌ Label(s) manquant(s): {', '.join(labels_manquants)}. Cette aide nécessite: {', '.join(labels_requis)}"
                ))
        else:
            # Pas de labels requis, points automatiques sans détail
            score += self.POIDS_LABELS * 0.6
        
        # Labels bonus
        if labels_bonus:
            labels_profil = [l.lower() for l in profil.labels]
            labels_bonus_profil = [
                lb for lb in labels_bonus 
                if any(lb.lower() in lp or lp in lb.lower() for lp in labels_profil)
            ]
            if labels_bonus_profil:
                ratio = len(labels_bonus_profil) / len(labels_bonus)
                points = self.POIDS_LABELS * 0.4 * ratio
                details.append(DetailCritere(
                    nom="Labels bonus",
                    valide=True,
                    bloquant=False,
                    points=points,
                    points_max=self.POIDS_LABELS * 0.4,
                    explication=f"✅ Labels bonus: {', '.join(labels_bonus_profil)}"
                ))
                score += points
            else:
                details.append(DetailCritere(
                    nom="Labels bonus",
                    valide=False,
                    bloquant=False,
                    points=0.0,
                    points_max=self.POIDS_LABELS * 0.4,
                    explication=f"💡 Labels bonus possibles: {', '.join(labels_bonus)}"
                ))
        else:
            # Pas de labels bonus, points automatiques
            score += self.POIDS_LABELS * 0.4
        
        return score, details
    
    def _estimer_montant(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur
    ) -> Tuple[Optional[float], Optional[float]]:
        """Estime le montant de l'aide pour le profil"""
        montant = aide.montant
        
        montant_min = montant.montant_min
        montant_max = montant.montant_max
        
        # Calcul selon le type de montant
        if montant.type_montant == "Surface" and montant.montant_par_unite:
            # Calcul basé sur la surface
            montant_estime = montant.montant_par_unite * profil.sau_totale
            if montant.plafond:
                montant_estime = min(montant_estime, montant.plafond)
            return montant_estime, montant_estime
        
        return montant_min, montant_max
    
    def _generer_resume(
        self, 
        eligible: bool, 
        score: float, 
        criteres_bloquants_ko: List[str]
    ) -> str:
        """Génère un résumé du matching"""
        if eligible:
            return f"✅ Éligible à cette aide avec un score de {score:.1f}/100"
        elif criteres_bloquants_ko:
            criteres_str = ', '.join(criteres_bloquants_ko)
            return f"❌ Non éligible - Critères bloquants non respectés: {criteres_str}"
        else:
            return f"⚠️ Score insuffisant ({score:.1f}/100, minimum requis: {self.SEUIL_ELIGIBILITE})"
    
    def _generer_recommandations(
        self, 
        aide: AideAgricoleV2, 
        profil: ProfilAgriculteur,
        details_criteres: List[DetailCritere],
        criteres_bloquants_ko: List[str]
    ) -> List[str]:
        """Génère des recommandations pour améliorer l'éligibilité"""
        recommandations = []
        
        # Recommandations basées sur les critères non validés
        for detail in details_criteres:
            if not detail.valide and detail.bloquant:
                if "Région" in detail.nom or "Département" in detail.nom:
                    recommandations.append("Cette aide n'est pas disponible dans votre zone géographique")
                elif "production" in detail.nom.lower():
                    recommandations.append("Votre type de production n'est pas éligible pour cette aide")
                elif "Statut" in detail.nom:
                    recommandations.append("Votre statut juridique ne correspond pas aux critères requis")
                elif "Âge" in detail.nom or "Jeune" in detail.nom:
                    recommandations.append("Vérifiez les critères d'âge pour cette aide")
                elif "Surface" in detail.nom:
                    recommandations.append("Votre surface agricole ne correspond pas aux critères requis")
        
        # Recommandations pour améliorer le score
        if not criteres_bloquants_ko:
            for detail in details_criteres:
                if not detail.valide and not detail.bloquant:
                    if "projet" in detail.nom.lower():
                        recommandations.append("Envisagez un projet correspondant aux types soutenus par cette aide")
                    elif "label" in detail.nom.lower():
                        recommandations.append("Obtenez les labels requis pour maximiser vos chances")
        
        # Si aucune recommandation spécifique
        if not recommandations and not criteres_bloquants_ko:
            if aide.source_url or aide.lien_officiel:
                recommandations.append("Consultez la fiche officielle pour déposer votre dossier")
            if aide.date_limite_depot:
                recommandations.append(f"Date limite de dépôt : {aide.date_limite_depot}")
            if aide.demarche:
                recommandations.append("Des informations sur les démarches sont disponibles pour cette aide")
            if not recommandations:
                recommandations.append("Votre profil est bien adapté à cette aide, n'hésitez pas à candidater")
        
        return recommandations[:5]  # Limiter à 5 recommandations
    
    def find_best_matches(
        self, 
        aides: List[AideAgricoleV2], 
        profil: ProfilAgriculteur,
        top_n: int = 10
    ) -> List[ResultatMatching]:
        """
        Trouve les meilleures correspondances pour un profil
        
        Args:
            aides: Liste des aides à évaluer
            profil: Profil de l'agriculteur
            top_n: Nombre de résultats à retourner
            
        Returns:
            Liste des meilleurs résultats de matching, triés par score
        """
        resultats = []
        
        for aide in aides:
            try:
                resultat = self.calculate_match(aide, profil)
                resultats.append(resultat)
            except Exception as e:
                logger.error(f"Erreur lors du matching pour aide {aide.aid_id}: {e}")
        
        # Tri par score décroissant, puis par éligibilité
        resultats.sort(key=lambda r: (r.eligible, r.score), reverse=True)
        
        return resultats[:top_n]
