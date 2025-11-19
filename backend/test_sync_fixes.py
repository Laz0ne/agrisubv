"""
Tests for sync_aides_territoires_v2.py fixes
Testing robust handling of different API data types
"""

from sync_aides_territoires_v2 import AidesTerritoiresSync
from unittest.mock import Mock


def test_recurrence_as_string():
    """Test that recurrence field handles string type (e.g., 'Permanente')"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '123',
        'name': 'Test Aide',
        'description': 'Test description',
        'recurrence': 'Permanente',  # String instead of dict
        'financers': ['Test Org'],
        'programs': [],
        'categories': [],
        'aid_types': [],
        'url': 'https://example.com'
    }
    
    # Should not raise AttributeError
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    assert aide_v2.date_fin is None  # "Permanente" means no end date


def test_recurrence_as_dict():
    """Test that recurrence field handles dict type"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '124',
        'name': 'Test Aide',
        'description': 'Test description',
        'recurrence': {'end_date': '2025-12-31'},  # Dict with end_date
        'financers': ['Test Org'],
        'programs': [],
        'categories': [],
        'aid_types': [],
        'url': 'https://example.com'
    }
    
    # Should not raise AttributeError
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    assert aide_v2.date_fin == '2025-12-31'


def test_financers_full_priority():
    """Test that financers_full takes priority over financers"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '125',
        'name': 'Test Aide',
        'description': 'Test description',
        'financers': ['AFD', 'Ministère'],
        'financers_full': [
            {'id': 48, 'name': 'Agence Française de Développement', 'logo': '...'},
            {'id': 49, 'name': 'Ministère de l\'Agriculture', 'logo': '...'}
        ],
        'programs': [],
        'categories': [],
        'aid_types': [],
        'url': 'https://example.com'
    }
    
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    # Should use full names from financers_full
    assert 'Agence Française de Développement' in aide_v2.organisme
    assert 'Ministère de l\'Agriculture' in aide_v2.organisme


def test_financers_as_strings():
    """Test that financers field handles string list"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '126',
        'name': 'Test Aide',
        'description': 'Test description',
        'financers': ['AFD', 'Ministère'],  # List of strings
        'programs': [],
        'categories': [],
        'aid_types': [],
        'url': 'https://example.com'
    }
    
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    assert 'AFD' in aide_v2.organisme
    assert 'Ministère' in aide_v2.organisme


def test_categories_robust_handling():
    """Test that categories field handles list of strings robustly"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '127',
        'name': 'Test Aide',
        'description': 'Test description',
        'financers': ['Test Org'],
        'programs': [],
        'categories': ['Agriculture', 'Développement rural', 'Environnement'],
        'aid_types': ['Subvention', 'Prêt'],
        'url': 'https://example.com'
    }
    
    # Test detect_productions
    productions = syncer.detect_productions(aide_data)
    assert isinstance(productions, list)
    
    # Test detect_projets
    projets = syncer.detect_projets(aide_data)
    assert isinstance(projets, list)
    
    # Test full normalization
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    assert len(aide_v2.tags) > 0
    assert 'Agriculture' in aide_v2.tags
    assert 'Subvention' in aide_v2.tags


def test_categories_with_none_values():
    """Test that categories field handles None values in list"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '128',
        'name': 'Test Aide',
        'description': 'Test description',
        'financers': ['Test Org'],
        'programs': [],
        'categories': ['Agriculture', None, '', 'Environnement'],  # Contains None and empty string
        'aid_types': ['Subvention', None],
        'url': 'https://example.com'
    }
    
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    # Should filter out None and empty values
    assert None not in aide_v2.tags
    assert '' not in aide_v2.tags
    assert 'Agriculture' in aide_v2.tags
    assert 'Environnement' in aide_v2.tags


def test_aid_types_robust_handling():
    """Test that aid_types field handles list of strings robustly"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '129',
        'name': 'Test Aide avec investissement',
        'description': 'Test description',
        'financers': ['Test Org'],
        'programs': [],
        'categories': ['Agriculture'],
        'aid_types': ['Subvention', 'Aide fiscale', 'Prêt bonifié'],
        'url': 'https://example.com'
    }
    
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    assert 'Subvention' in aide_v2.tags
    assert 'Aide fiscale' in aide_v2.tags
    assert 'Prêt bonifié' in aide_v2.tags


def test_empty_lists():
    """Test that empty lists are handled correctly"""
    db = Mock()
    syncer = AidesTerritoiresSync(db)
    
    aide_data = {
        'id': '130',
        'name': 'Test Aide',
        'description': 'Test description',
        'financers': [],  # Empty
        'financers_full': [],  # Empty
        'programs': [],  # Empty
        'categories': [],  # Empty
        'aid_types': [],  # Empty
        'url': 'https://example.com'
    }
    
    aide_v2 = syncer.normalize_aide(aide_data)
    assert aide_v2 is not None
    assert aide_v2.organisme == 'Non spécifié'
    assert aide_v2.tags == []


if __name__ == '__main__':
    # Run tests manually
    test_recurrence_as_string()
    print("✅ test_recurrence_as_string passed")
    
    test_recurrence_as_dict()
    print("✅ test_recurrence_as_dict passed")
    
    test_financers_full_priority()
    print("✅ test_financers_full_priority passed")
    
    test_financers_as_strings()
    print("✅ test_financers_as_strings passed")
    
    test_categories_robust_handling()
    print("✅ test_categories_robust_handling passed")
    
    test_categories_with_none_values()
    print("✅ test_categories_with_none_values passed")
    
    test_aid_types_robust_handling()
    print("✅ test_aid_types_robust_handling passed")
    
    test_empty_lists()
    print("✅ test_empty_lists passed")
    
    print("\n🎉 All tests passed!")
