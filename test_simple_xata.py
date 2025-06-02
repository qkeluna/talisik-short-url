#!/usr/bin/env python3
"""Simple test to isolate Xata constraint issue"""

import logging
from talisik.core.config import get_config
from xata import XataClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_insert():
    """Test the simplest possible insert to isolate constraint issue"""
    config = get_config()
    client = XataClient(
        api_key=config.xata_api_key,
        db_url=config.xata_database_url
    )
    
    # Test 1: Try with explicit xata_id
    logger.info("Test 1: Insert with explicit xata_id")
    try:
        result = client.sql().query(
            "INSERT INTO short_urls (xata_id, original_url, short_code, click_count, is_active) VALUES ($1, $2, $3, $4, $5) RETURNING xata_id",
            ["test-id-123", "https://google.com", "abc123", 0, True]
        )
        logger.info(f"SUCCESS with explicit xata_id: {result}")
        return True
    except Exception as e:
        logger.info(f"FAILED with explicit xata_id: {e}")
    
    # Test 2: Try with gen_random_uuid() for xata_id
    logger.info("Test 2: Insert with gen_random_uuid() for xata_id")
    try:
        result = client.sql().query(
            "INSERT INTO short_urls (xata_id, original_url, short_code, click_count, is_active) VALUES (gen_random_uuid()::text, $1, $2, $3, $4) RETURNING xata_id",
            ["https://google.com", "abc124", 0, True]
        )
        logger.info(f"SUCCESS with gen_random_uuid(): {result}")
        return True
    except Exception as e:
        logger.info(f"FAILED with gen_random_uuid(): {e}")
    
    # Test 3: Try with DEFAULT for all possible fields
    logger.info("Test 3: Insert with DEFAULT values")
    try:
        result = client.sql().query(
            "INSERT INTO short_urls (original_url, short_code, click_count, is_active, created_at) VALUES ($1, $2, DEFAULT, DEFAULT, DEFAULT) RETURNING xata_id",
            ["https://google.com", "abc125"]
        )
        logger.info(f"SUCCESS with DEFAULT: {result}")
        return True
    except Exception as e:
        logger.info(f"FAILED with DEFAULT: {e}")
    
    # Test 4: Check if there are existing records that might cause UNIQUE constraint violation
    logger.info("Test 4: Check for existing records")
    try:
        result = client.sql().query("SELECT short_code FROM short_urls LIMIT 5")
        logger.info(f"Existing records: {result}")
        
        if result.get('records'):
            logger.info("Found existing records - UNIQUE constraint might be the issue")
        else:
            logger.info("No existing records found")
    except Exception as e:
        logger.info(f"Failed to check existing records: {e}")
    
    return False

if __name__ == "__main__":
    test_simple_insert() 