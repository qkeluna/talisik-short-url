#!/usr/bin/env python3
"""Test script to verify Xata integration is working"""

import sys
import logging
from datetime import datetime, UTC

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_xata_integration():
    """Test the Xata integration with URLShortener"""
    try:
        # Import our classes
        from talisik.core.shortener import URLShortener
        from talisik.core.models import ShortenRequest
        from talisik.core.config import get_config
        
        logger.info("Starting Xata integration test...")
        
        # Load configuration (should use Xata backend from .env)
        config = get_config()
        logger.info(f"Loaded config - Storage backend: {config.storage_backend}")
        logger.info(f"Base URL: {config.base_url}")
        
        # Initialize URLShortener
        shortener = URLShortener(config=config)
        logger.info("URLShortener initialized successfully")
        
        # Test URL shortening
        test_url = "https://example.com/test-xata-integration"
        logger.info(f"Shortening URL: {test_url}")
        
        request = ShortenRequest(url=test_url, custom_code=f"test-{int(datetime.now().timestamp())}")
        response = shortener.shorten(request)
        
        if response.success:
            logger.info("✅ URL shortened successfully!")
            logger.info(f"   Short URL: {response.short_url}")
            logger.info(f"   Short Code: {response.short_code}")
            
            # Test URL expansion
            logger.info(f"Testing expansion of code: {response.short_code}")
            expanded_url = shortener.expand(response.short_code)
            
            if expanded_url == test_url:
                logger.info("✅ URL expansion successful!")
                logger.info(f"   Expanded URL: {expanded_url}")
                
                # Test stats
                stats = shortener.get_stats()
                logger.info(f"📊 Stats: {stats}")
                
                return True
            else:
                logger.error(f"❌ URL expansion failed! Expected: {test_url}, Got: {expanded_url}")
                return False
        else:
            logger.error(f"❌ URL shortening failed: {response.error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_storage():
    """Test memory storage as a fallback"""
    try:
        from talisik.core.shortener import URLShortener
        from talisik.core.models import ShortenRequest
        from talisik.core.config import TalisikConfig
        
        logger.info("\n--- Testing Memory Storage Fallback ---")
        
        # Create config with memory storage
        config = TalisikConfig(
            xata_api_key="dummy", 
            xata_database_url="dummy",
            storage_backend="memory"
        )
        
        shortener = URLShortener(config=config)
        
        request = ShortenRequest(url="https://example.com/memory-test")
        response = shortener.shorten(request)
        
        # Check if response has success attribute
        if hasattr(response, 'success'):
            if response.success and shortener.expand(response.short_code) == "https://example.com/memory-test":
                logger.info(f"✅ Memory storage test passed! Short code: {response.short_code}")
                return True
            else:
                logger.error(f"❌ Memory storage test failed! Success: {response.success}, Error: {getattr(response, 'error', 'Unknown')}")
                return False
        else:
            # Fallback for old model format - check if we got a valid response
            if response.short_code and shortener.expand(response.short_code) == "https://example.com/memory-test":
                logger.info(f"✅ Memory storage test passed! Short code: {response.short_code}")
                return True
            else:
                logger.error("❌ Memory storage test failed!")
                return False
            
    except Exception as e:
        logger.error(f"❌ Memory storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_xata_response():
    """Debug the Xata response format"""
    try:
        from talisik.core.config import get_config
        from xata import XataClient
        
        logger.info("\n--- Debugging Xata Response Format ---")
        
        config = get_config()
        client = XataClient(
            api_key=config.xata_api_key,
            db_url=config.xata_database_url
        )
        
        # Try a simple query to see the response format
        logger.info("Testing direct Xata data().query()...")
        query_payload = {"page": {"size": 5}}
        response = client.data().query("short_urls", query_payload)
        
        logger.info(f"Raw Xata response: {response}")
        logger.info(f"Response type: {type(response)}")
        
        if hasattr(response, '__dict__'):
            logger.info(f"Response attributes: {response.__dict__}")
            
        # Check if we have records
        if response and response.get('records'):
            logger.info(f"Found {len(response['records'])} records")
            if len(response['records']) > 0:
                logger.info(f"First record structure: {response['records'][0]}")
        else:
            logger.info("No records found in response")
            
        # Try SQL query as fallback
        logger.info("\nTesting SQL query fallback...")
        try:
            sql_response = client.sql().query("SELECT * FROM short_urls LIMIT 5")
            logger.info(f"SQL response: {sql_response}")
            logger.info(f"SQL response type: {type(sql_response)}")
            
            if sql_response and sql_response.get('records'):
                logger.info(f"Found {len(sql_response['records'])} records via SQL")
                if len(sql_response['records']) > 0:
                    logger.info(f"First SQL record: {sql_response['records'][0]}")
            else:
                logger.info("No records found via SQL")
                
        except Exception as sql_e:
            logger.error(f"SQL query failed: {sql_e}")
            
        # Try direct insert test
        logger.info("\nTesting direct record insert...")
        try:
            test_record = {
                "original_url": "https://example.com/debug-test",
                "short_code": f"debug-{int(datetime.now(UTC).timestamp())}",
                "created_at": datetime.now(UTC).isoformat(),
                "click_count": 0,
                "is_active": True
            }
            
            logger.info(f"Inserting test record: {test_record}")
            insert_result = client.records().insert("short_urls", test_record)
            logger.info(f"Insert result: {insert_result}")
            logger.info(f"Insert result type: {type(insert_result)}")
            
            if hasattr(insert_result, 'is_success'):
                logger.info(f"Insert success status: {insert_result.is_success()}")
                if hasattr(insert_result, 'status_code'):
                    logger.info(f"Insert status code: {insert_result.status_code}")
            
            # Check if we can query the record back
            if insert_result and (insert_result.get('id') or insert_result.get('xata_id')):
                record_id = insert_result.get('id') or insert_result.get('xata_id')
                logger.info(f"Record inserted with ID: {record_id}")
                
                # Try to get it back
                get_result = client.records().get("short_urls", record_id)
                logger.info(f"Get result: {get_result}")
            
        except Exception as insert_e:
            logger.error(f"Direct insert test failed: {insert_e}")
        
        # Try to insert a very basic record to isolate which constraint is failing
        logger.info("Testing very basic insert...")
        try:
            basic_response = client.sql().query(
                "INSERT INTO short_urls (original_url, short_code) VALUES ('https://google.com', 'abc123') RETURNING xata_id"
            )
            logger.info(f"Basic insert result: {basic_response}")
            
        except Exception as e:
            logger.info(f"Basic insert failed: {e}")
            
        # Test different URL formats to see if URL constraint is the issue
        logger.info("Testing different URL formats...")
        test_urls = [
            "https://google.com",
            "http://example.com", 
            "https://www.example.com/test",
            "https://example.com/very/long/path/to/test/url/validation"
        ]
        
        for i, test_url in enumerate(test_urls):
            try:
                test_code = f"test{i}"
                response = client.sql().query(
                    "INSERT INTO short_urls (original_url, short_code, click_count, is_active) VALUES ($1, $2, $3, $4) RETURNING xata_id",
                    [test_url, test_code, 0, True]
                )
                logger.info(f"URL test {i} SUCCESS: {test_url} -> {response}")
                break  # If one succeeds, we found the issue
            except Exception as e:
                logger.info(f"URL test {i} FAILED: {test_url} -> {e}")
                
        # Test different short code formats
        logger.info("Testing different short code formats...")
        test_codes = [
            "a",           # minimum length
            "abc",         # short
            "test123",     # alphanumeric
            "a" * 50,      # maximum length
            "test-code",   # with dash
            "test_code"    # with underscore
        ]
        
        for i, test_code in enumerate(test_codes):
            try:
                response = client.sql().query(
                    "INSERT INTO short_urls (original_url, short_code, click_count, is_active) VALUES ($1, $2, $3, $4) RETURNING xata_id",
                    ["https://example.com", test_code, 0, True]
                )
                logger.info(f"Code test {i} SUCCESS: {test_code} -> {response}")
                break  # If one succeeds, we found the issue
            except Exception as e:
                logger.info(f"Code test {i} FAILED: {test_code} -> {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Xata debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_table_schema():
    """Debug the table schema to understand constraints"""
    try:
        from talisik.core.config import get_config
        from xata import XataClient
        
        logger.info("\n--- Debugging Table Schema ---")
        
        config = get_config()
        client = XataClient(
            api_key=config.xata_api_key,
            db_url=config.xata_database_url
        )
        
        # Try to get table schema information
        logger.info("Getting table schema information...")
        try:
            # Try a simple insert to see what the constraint error is
            sql_response = client.sql().query(
                "INSERT INTO short_urls (original_url, short_code, created_at, click_count, is_active) VALUES ($1, $2, $3, $4, $5) RETURNING xata_id",
                ["https://test.com", "test123", "2025-06-02T08:00:00+00:00", 0, True]
            )
            logger.info(f"Simple insert result: {sql_response}")
            
        except Exception as e:
            logger.info(f"Simple insert failed: {e}")
            
        # Try to describe the table structure 
        logger.info("Checking table structure...")
        try:
            schema_response = client.sql().query(
                "SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'short_urls'"
            )
            logger.info(f"Schema query result: {schema_response}")
            
        except Exception as e:
            logger.info(f"Schema query failed: {e}")
            
        # Check for constraints
        logger.info("Checking table constraints...")
        try:
            constraints_response = client.sql().query(
                "SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = 'short_urls'"
            )
            logger.info(f"Constraints query result: {constraints_response}")
            
        except Exception as e:
            logger.info(f"Constraints query failed: {e}")
            
        # Check for detailed constraint definitions
        logger.info("Getting detailed constraint definitions...")
        try:
            constraints_detail_response = client.sql().query(
                """
                SELECT 
                    tc.constraint_name, 
                    tc.constraint_type,
                    cc.check_clause
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.check_constraints cc 
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.table_name = 'short_urls'
                """
            )
            logger.info(f"Detailed constraints query result: {constraints_detail_response}")
            
        except Exception as e:
            logger.info(f"Detailed constraints query failed: {e}")
            
        # Try to insert a very basic record to isolate which constraint is failing
        logger.info("Testing very basic insert...")
        try:
            basic_response = client.sql().query(
                "INSERT INTO short_urls (original_url, short_code) VALUES ('https://google.com', 'abc123') RETURNING xata_id"
            )
            logger.info(f"Basic insert result: {basic_response}")
            
        except Exception as e:
            logger.info(f"Basic insert failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TALISIK XATA INTEGRATION TEST")
    print("=" * 60)
    
    xata_success = test_xata_integration()
    memory_success = test_memory_storage()
    debug_success = debug_xata_response()
    schema_success = debug_table_schema()
    
    print("\n" + "=" * 60)
    if xata_success and memory_success:
        print("✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        if not xata_success:
            print("   - Xata integration test failed")
        if not memory_success:
            print("   - Memory storage test failed")
        sys.exit(1) 