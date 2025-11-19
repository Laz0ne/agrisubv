"""
Test script to validate the debug improvements to sync_aides_territoires_v2.py
"""

import asyncio
import sys
from sync_aides_territoires_v2 import AidesTerritoiresSync


class MockDB:
    """Mock database for testing"""
    pass


def test_normalize_aide_robustness():
    """Test that normalize_aide handles various edge cases robustly"""
    
    syncer = AidesTerritoiresSync(MockDB())
    
    # Test case 1: Empty financers list
    aide_data = {
        'id': '123',
        'name': 'Test Aide',
        'description': 'Test description',
        'financers': [],
        'programs': [],
        'url': '/test-url',
    }
    
    try:
        result = syncer.normalize_aide(aide_data)
        print("✅ Test 1 passed: Empty financers handled correctly")
        assert result.organisme == 'Non spécifié', f"Expected 'Non spécifié', got {result.organisme}"
        assert result.programme == '', f"Expected empty string, got {result.programme}"
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test case 2: financers as strings instead of dicts
    aide_data['financers'] = ['Org1', 'Org2']
    
    try:
        result = syncer.normalize_aide(aide_data)
        print("✅ Test 2 passed: String financers handled correctly")
        assert result.organisme == 'Org1, Org2', f"Expected 'Org1, Org2', got {result.organisme}"
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test case 3: programs as dict
    aide_data['financers'] = [{'name': 'Test Org'}]
    aide_data['programs'] = [{'name': 'Test Program'}]
    
    try:
        result = syncer.normalize_aide(aide_data)
        print("✅ Test 3 passed: Dict programs handled correctly")
        assert result.programme == 'Test Program', f"Expected 'Test Program', got {result.programme}"
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test case 4: programs as dict with slug
    aide_data['programs'] = [{'slug': 'test-slug'}]
    
    try:
        result = syncer.normalize_aide(aide_data)
        print("✅ Test 4 passed: Dict programs with slug handled correctly")
        assert result.programme == 'test-slug', f"Expected 'test-slug', got {result.programme}"
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    # Test case 5: programs as strings
    aide_data['programs'] = ['Program String']
    
    try:
        result = syncer.normalize_aide(aide_data)
        print("✅ Test 5 passed: String programs handled correctly")
        assert result.programme == 'Program String', f"Expected 'Program String', got {result.programme}"
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        return False
    
    # Test case 6: None values for name and description
    aide_data_none = {
        'id': '124',
        'name': None,
        'description': None,
        'financers': [],
        'programs': [],
        'url': '/test-url',
    }
    
    try:
        result = syncer.normalize_aide(aide_data_none)
        print("✅ Test 6 passed: None values handled correctly")
        assert result.titre == 'Aide sans titre', f"Expected 'Aide sans titre', got {result.titre}"
        assert result.description == '', f"Expected empty string, got {result.description}"
    except Exception as e:
        print(f"❌ Test 6 failed: {e}")
        return False
    
    # Test case 7: Non-string name (integer)
    aide_data_int = {
        'id': '125',
        'name': 12345,
        'description': 67890,
        'financers': [],
        'programs': [],
        'url': '/test-url',
    }
    
    try:
        result = syncer.normalize_aide(aide_data_int)
        print("✅ Test 7 passed: Non-string values handled correctly")
        assert result.titre == '12345', f"Expected '12345', got {result.titre}"
        assert result.description == '67890', f"Expected '67890', got {result.description}"
    except Exception as e:
        print(f"❌ Test 7 failed: {e}")
        return False
    
    return True


async def test_debug_first_aide_function():
    """Test that debug_first_aide function is callable"""
    from sync_aides_territoires_v2 import debug_first_aide
    
    print("\n🔍 Testing debug_first_aide function signature...")
    
    # Check that function exists and is async
    import inspect
    assert inspect.iscoroutinefunction(debug_first_aide), "debug_first_aide should be async"
    
    # Check function signature
    sig = inspect.signature(debug_first_aide)
    assert 'db' in sig.parameters, "debug_first_aide should have 'db' parameter"
    
    print("✅ debug_first_aide function signature is correct")
    return True


def test_server_imports():
    """Test that server.py can import the new function"""
    
    print("\n📦 Testing server imports...")
    
    try:
        from server import debug_first_aide_endpoint
        print("✅ debug_first_aide_endpoint imported successfully from server.py")
        
        # Check that it's a FastAPI endpoint
        assert hasattr(debug_first_aide_endpoint, '__call__'), "Should be callable"
        return True
    except ImportError as e:
        print(f"❌ Failed to import from server.py: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("TESTING DEBUG IMPROVEMENTS")
    print("=" * 80)
    
    # Test 1: Robustness of normalize_aide
    print("\n📋 Test 1: normalize_aide robustness")
    test1 = test_normalize_aide_robustness()
    
    # Test 2: debug_first_aide function
    print("\n📋 Test 2: debug_first_aide function")
    test2 = asyncio.run(test_debug_first_aide_function())
    
    # Test 3: Server imports
    print("\n📋 Test 3: Server imports")
    test3 = test_server_imports()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"1. normalize_aide robustness: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"2. debug_first_aide function: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"3. Server imports: {'✅ PASSED' if test3 else '❌ FAILED'}")
    print("=" * 80)
    
    return test1 and test2 and test3


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
