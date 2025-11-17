"""
Test script for Bearer Token authentication
Verifies that the authentication flow works correctly
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock DB for testing
class MockDB:
    pass

async def test_bearer_token_auth():
    """Test the Bearer Token authentication flow"""
    from sync_aides_territoires_v2 import AidesTerritoiresSync, API_TOKEN
    
    print("=" * 80)
    print("TEST BEARER TOKEN AUTHENTICATION")
    print("=" * 80)
    
    # Check if API token is configured
    if not API_TOKEN:
        print("❌ AIDES_TERRITOIRES_API_TOKEN not configured")
        print("   Set it in .env file or environment variable")
        return False
    
    print(f"✅ API Token configured: {API_TOKEN[:20]}...")
    
    # Create sync instance
    mock_db = MockDB()
    syncer = AidesTerritoiresSync(mock_db)
    
    # Test authentication
    print("\n🔐 Testing authentication...")
    bearer_token = await syncer.get_bearer_token()
    
    if bearer_token:
        print(f"✅ Bearer Token obtained successfully!")
        print(f"   Token (first 50 chars): {bearer_token[:50]}...")
        return True
    else:
        print("❌ Failed to obtain Bearer Token")
        return False

async def test_fetch_first_page():
    """Test fetching the first page with authentication"""
    from sync_aides_territoires_v2 import AidesTerritoiresSync, API_TOKEN
    
    print("\n" + "=" * 80)
    print("TEST FETCH FIRST PAGE")
    print("=" * 80)
    
    if not API_TOKEN:
        print("❌ Skipping (API_TOKEN not configured)")
        return False
    
    # Create sync instance
    mock_db = MockDB()
    syncer = AidesTerritoiresSync(mock_db)
    
    # Test fetching first page
    print("\n📥 Fetching first page of aides...")
    aides = await syncer.fetch_aides_paginated(max_pages=1)
    
    if aides:
        print(f"✅ Successfully fetched {len(aides)} aides from first page")
        if len(aides) > 0:
            first_aide = aides[0]
            print(f"\n📋 First aide:")
            print(f"   ID: {first_aide.get('id', 'N/A')}")
            print(f"   Name: {first_aide.get('name', 'N/A')[:80]}...")
        return True
    else:
        print("❌ No aides fetched")
        return False

async def main():
    """Run all tests"""
    print("\n🚀 Starting Bearer Token Authentication Tests\n")
    
    # Test 1: Authentication
    test1_passed = await test_bearer_token_auth()
    
    # Test 2: Fetch first page (only if authentication succeeded)
    test2_passed = False
    if test1_passed:
        test2_passed = await test_fetch_first_page()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"1. Bearer Token Authentication: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"2. Fetch First Page: {'✅ PASSED' if test2_passed else '❌ FAILED' if test1_passed else '⏭️  SKIPPED'}")
    print("=" * 80)
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
