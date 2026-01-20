#!/usr/bin/env python3
"""
Demo Data Seeder for SK Brands Retail AI Platform
=================================================
Creates controlled demo scenarios for showcase demonstrations.
Uses existing stores from sk_stores table.

Usage:
    python demo_seeder.py --scenario 1   # Winter stock crisis scenario
    python demo_seeder.py --scenario 2   # Spring sales opportunity scenario
    python demo_seeder.py --clear        # Clear all demo data
"""

import argparse
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent to path for imports
sys.path.insert(0, '.')

from config.aws import get_dynamodb_resource
from config.settings import settings

dynamodb = get_dynamodb_resource()

# ============================================================================
# PRODUCT DATA (Same for both scenarios)
# ============================================================================
PRODUCTS = [
    # Winterwear (3)
    {"product_id": "PROD_WS001", "name": "Wool Blend Sweater", "category": "Winterwear", "cost": 600, "price": 1799, "sku_base": "WS001", "seasons": ["Winter"]},
    {"product_id": "PROD_LJ002", "name": "Lightweight Jacket", "category": "Outerwear", "cost": 800, "price": 2499, "sku_base": "LJ002", "seasons": ["Winter", "Monsoon"]},
    {"product_id": "PROD_TH008", "name": "Track Hoodie", "category": "Athleisure", "cost": 400, "price": 1199, "sku_base": "TH008", "seasons": ["Winter", "Monsoon"]},
    
    # Traditional (3)
    {"product_id": "PROD_CK003", "name": "Cotton Kurta", "category": "Traditional", "cost": 300, "price": 999, "sku_base": "CK003", "seasons": ["All-Season"]},
    {"product_id": "PROD_SK007", "name": "Silk Saree", "category": "Traditional", "cost": 1500, "price": 4999, "sku_base": "SK007", "seasons": ["All-Season"]},
    {"product_id": "PROD_PJ009", "name": "Patiala Suit", "category": "Traditional", "cost": 700, "price": 1899, "sku_base": "PJ009", "seasons": ["All-Season"]},
    
    # Bottomwear (4)
    {"product_id": "PROD_DJ004", "name": "Denim Jeans", "category": "Bottomwear", "cost": 450, "price": 1499, "sku_base": "DJ004", "seasons": ["All-Season"]},
    {"product_id": "PROD_FC006", "name": "Formal Chinos", "category": "Bottomwear", "cost": 500, "price": 1299, "sku_base": "FC006", "seasons": ["All-Season"]},
    {"product_id": "PROD_CT010", "name": "Cargo Trousers", "category": "Bottomwear", "cost": 480, "price": 1399, "sku_base": "CT010", "seasons": ["All-Season"]},
    {"product_id": "PROD_SH011", "name": "Cotton Shorts", "category": "Bottomwear", "cost": 250, "price": 699, "sku_base": "SH011", "seasons": ["Summer"]},
    
    # Casualwear (4)
    {"product_id": "PROD_PS005", "name": "Polo Shirt", "category": "Casualwear", "cost": 350, "price": 899, "sku_base": "PS005", "seasons": ["Summer", "All-Season"]},
    {"product_id": "PROD_CT012", "name": "Cotton T-Shirt", "category": "Casualwear", "cost": 200, "price": 599, "sku_base": "CT012", "seasons": ["Summer", "All-Season"]},
    {"product_id": "PROD_HN013", "name": "Henley Neck Tee", "category": "Casualwear", "cost": 280, "price": 799, "sku_base": "HN013", "seasons": ["All-Season"]},
    {"product_id": "PROD_LS014", "name": "Linen Shirt", "category": "Casualwear", "cost": 450, "price": 1199, "sku_base": "LS014", "seasons": ["Summer"]},
    
    # Formalwear (3)
    {"product_id": "PROD_FS015", "name": "Formal Shirt", "category": "Formalwear", "cost": 400, "price": 1099, "sku_base": "FS015", "seasons": ["All-Season"]},
    {"product_id": "PROD_BZ016", "name": "Blazer", "category": "Formalwear", "cost": 1200, "price": 3499, "sku_base": "BZ016", "seasons": ["Winter", "All-Season"]},
    {"product_id": "PROD_FT017", "name": "Formal Trousers", "category": "Formalwear", "cost": 550, "price": 1499, "sku_base": "FT017", "seasons": ["All-Season"]},
    
    # Athleisure (3)
    {"product_id": "PROD_JG018", "name": "Jogger Pants", "category": "Athleisure", "cost": 380, "price": 999, "sku_base": "JG018", "seasons": ["All-Season"]},
    {"product_id": "PROD_SW019", "name": "Sweatshirt", "category": "Athleisure", "cost": 450, "price": 1299, "sku_base": "SW019", "seasons": ["Winter"]},
    {"product_id": "PROD_TK020", "name": "Track Suit", "category": "Athleisure", "cost": 700, "price": 1999, "sku_base": "TK020", "seasons": ["Winter", "All-Season"]},
]

# SCENARIO 1: Winter Stock Crisis (Minimal Data - Quick Demo)
# Focus on a few critical situations
# ============================================================================
SCENARIO_1 = {
    "name": "Winter Stock Crisis",
    "description": "Peak winter season causing stock volatility - Minimal demo data",
    "store_configs": {
        # Tamil Nadu stores only
        "STORE_CHN": {"ws": 5, "lj": 45, "ck": 80, "dj": 35, "issue": "CRITICAL_LOW_SWEATERS"},
        "STORE_CBE": {"ws": 120, "lj": 60, "ck": 200, "dj": 55, "issue": "OVERSTOCKED_KURTAS"},
        "STORE_MDU": {"ws": 200, "lj": 150, "ck": 100, "dj": 80, "issue": "WELL_STOCKED_DONOR"},
        "STORE_TCH": {"ws": 60, "lj": 5, "ck": 70, "dj": 50, "issue": "CRITICAL_LOW_JACKETS"},
        "STORE_SLM": {"ws": 40, "lj": 35, "ck": 30, "dj": 0, "issue": "OUT_OF_STOCK_JEANS"},
        "STORE_TPR": {"ws": 80, "lj": 70, "ck": 60, "dj": 120, "issue": "OVERSTOCKED_JEANS_DONOR"},
        "STORE_VLR": {"ws": 50, "lj": 40, "ck": 50, "dj": 46},
        "STORE_TJV": {"ws": 46, "lj": 36, "ck": 54, "dj": 44},
        "STORE_ERD": {"ws": 48, "lj": 38, "ck": 52, "dj": 42},
        "STORE_NGL": {"ws": 44, "lj": 34, "ck": 48, "dj": 40},
    },
    "sales": [
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 25, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 22, "days_ago": 2},
        {"store_id": "STORE_TCH", "product_id": "PROD_LJ002", "quantity": 18, "days_ago": 1},
        {"store_id": "STORE_CBE", "product_id": "PROD_CK003", "quantity": 2, "days_ago": 1},
    ],
    "forecasts": [
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "forecasted_demand": 150, "confidence": 0.92},
        {"store_id": "STORE_SLM", "product_id": "PROD_DJ004", "forecasted_demand": 120, "confidence": 0.89},
        {"store_id": "STORE_TCH", "product_id": "PROD_LJ002", "forecasted_demand": 100, "confidence": 0.91},
    ],
}

# ============================================================================
# SCENARIO 2: Spring Sales Opportunity (Minimal Data)
# Seasonal transition clearance
# ============================================================================
SCENARIO_2 = {
    "name": "Spring Sales Opportunity",
    "description": "Transition to spring, clearing winter stock - Minimal demo data",
    "store_configs": {
        "STORE_CHN": {"ws": 85, "lj": 70, "ck": 50, "dj": 40, "issue": "WINTER_CLEARANCE"},
        "STORE_CBE": {"ws": 60, "lj": 55, "ck": 45, "dj": 38},
        "STORE_MDU": {"ws": 40, "lj": 35, "ck": 60, "dj": 15, "issue": "HIGH_DENIM_DEMAND"},
        "STORE_TCH": {"ws": 70, "lj": 60, "ck": 150, "dj": 80, "issue": "NEW_COLLECTION_PREP"},
        "STORE_SLM": {"ws": 55, "lj": 40, "ck": 65, "dj": 50},
        "STORE_TPR": {"ws": 45, "lj": 40, "ck": 55, "dj": 30},
        "STORE_VLR": {"ws": 50, "lj": 40, "ck": 54, "dj": 44},
        "STORE_TJV": {"ws": 46, "lj": 36, "ck": 52, "dj": 40},
        "STORE_ERD": {"ws": 48, "lj": 38, "ck": 50, "dj": 42},
        "STORE_NGL": {"ws": 52, "lj": 38, "ck": 58, "dj": 44},
    },
    "sales": [
        {"store_id": "STORE_MDU", "product_id": "PROD_DJ004", "quantity": 18, "days_ago": 1},
        {"store_id": "STORE_MDU", "product_id": "PROD_DJ004", "quantity": 22, "days_ago": 2},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 2, "days_ago": 1},
        {"store_id": "STORE_TCH", "product_id": "PROD_CK003", "quantity": 20, "days_ago": 1},
    ],
    "forecasts": [
        {"store_id": "STORE_MDU", "product_id": "PROD_DJ004", "forecasted_demand": 150, "confidence": 0.94},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "forecasted_demand": 15, "confidence": 0.80},
        {"store_id": "STORE_TCH", "product_id": "PROD_CK003", "forecasted_demand": 200, "confidence": 0.92},
    ],
}

# ============================================================================
# SCENARIO 3: Full Retail Operations (Comprehensive Data)
# More products, more sales, more forecasts - for thorough demo
# ============================================================================
SCENARIO_3 = {
    "name": "Full Retail Operations",
    "description": "Comprehensive scenario with rich data across all stores and products",
    "store_configs": {
        "STORE_CHN": {"ws": 15, "lj": 25, "ck": 180, "dj": 45, "issue": "LOW_WINTER_HIGH_TRADITIONAL"},
        "STORE_CBE": {"ws": 90, "lj": 80, "ck": 55, "dj": 30, "issue": "BALANCED_WINTER"},
        "STORE_MDU": {"ws": 35, "lj": 25, "ck": 200, "dj": 65, "issue": "HIGH_TRADITIONAL_DEMAND"},
        "STORE_TCH": {"ws": 70, "lj": 65, "ck": 45, "dj": 40, "issue": "BALANCED"},
        "STORE_SLM": {"ws": 8, "lj": 12, "ck": 90, "dj": 100, "issue": "CRITICAL_WINTER_LOW"},
        "STORE_TPR": {"ws": 150, "lj": 120, "ck": 30, "dj": 25, "issue": "OVERSTOCKED_WINTER"},
        "STORE_VLR": {"ws": 25, "lj": 20, "ck": 65, "dj": 5, "issue": "LOW_JEANS"},
        "STORE_TJV": {"ws": 55, "lj": 50, "ck": 110, "dj": 85, "issue": "FESTIVE_READY"},
        "STORE_ERD": {"ws": 40, "lj": 35, "ck": 75, "dj": 60},
        "STORE_NGL": {"ws": 60, "lj": 55, "ck": 40, "dj": 35},
    },
    "sales": [
        # Chennai - High demand for sweaters (sold out fast)
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 35, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 40, "days_ago": 2},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 30, "days_ago": 3},
        {"store_id": "STORE_CHN", "product_id": "PROD_LJ002", "quantity": 20, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_CK003", "quantity": 15, "days_ago": 1},
        
        # Madurai - Strong traditional wear demand (temple city)
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 45, "days_ago": 1},
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 50, "days_ago": 2},
        {"store_id": "STORE_MDU", "product_id": "PROD_DJ004", "quantity": 25, "days_ago": 1},
        
        # Salem - Running out of winter stock
        {"store_id": "STORE_SLM", "product_id": "PROD_WS001", "quantity": 28, "days_ago": 1},
        {"store_id": "STORE_SLM", "product_id": "PROD_LJ002", "quantity": 22, "days_ago": 1},
        
        # Vellore - Student demand for jeans (VIT nearby)
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "quantity": 32, "days_ago": 1},
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "quantity": 28, "days_ago": 2},
        
        # Tiruppur - Slow winter sales (local competition)
        {"store_id": "STORE_TPR", "product_id": "PROD_WS001", "quantity": 3, "days_ago": 1},
        {"store_id": "STORE_TPR", "product_id": "PROD_LJ002", "quantity": 2, "days_ago": 1},
        
        # Thanjavur - Festive demand surge
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "quantity": 35, "days_ago": 1},
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "quantity": 30, "days_ago": 2},
        
        # Coimbatore - Steady corporate sales
        {"store_id": "STORE_CBE", "product_id": "PROD_LJ002", "quantity": 18, "days_ago": 1},
        {"store_id": "STORE_CBE", "product_id": "PROD_DJ004", "quantity": 15, "days_ago": 1},
    ],
    "forecasts": [
        # Critical needs
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "forecasted_demand": 200, "confidence": 0.95},
        {"store_id": "STORE_CHN", "product_id": "PROD_LJ002", "forecasted_demand": 150, "confidence": 0.92},
        {"store_id": "STORE_SLM", "product_id": "PROD_WS001", "forecasted_demand": 100, "confidence": 0.90},
        {"store_id": "STORE_SLM", "product_id": "PROD_LJ002", "forecasted_demand": 80, "confidence": 0.88},
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "forecasted_demand": 120, "confidence": 0.93},
        
        # Traditional wear for temples/festivals
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "forecasted_demand": 250, "confidence": 0.96},
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "forecasted_demand": 180, "confidence": 0.91},
        
        # Low demand (overstock situations)
        {"store_id": "STORE_TPR", "product_id": "PROD_WS001", "forecasted_demand": 20, "confidence": 0.85},
        {"store_id": "STORE_TPR", "product_id": "PROD_LJ002", "forecasted_demand": 15, "confidence": 0.82},
        
        # Balanced stores
        {"store_id": "STORE_TCH", "product_id": "PROD_WS001", "forecasted_demand": 70, "confidence": 0.88},
        {"store_id": "STORE_CBE", "product_id": "PROD_LJ002", "forecasted_demand": 90, "confidence": 0.90},
        {"store_id": "STORE_ERD", "product_id": "PROD_CK003", "forecasted_demand": 85, "confidence": 0.87},
    ],
}

# ============================================================================
# SCENARIO 4: Comprehensive Retail Analysis (Large Dataset)
# 20 products, 10 stores, 200 inventory records, rich sales & forecasts
# Mixed inventory: CRITICAL (50-150), LOW (200-400), BALANCED (500-800), OVERSTOCKED (1500-2500)
# ============================================================================
SCENARIO_4 = {
    "name": "Comprehensive Retail Analysis",
    "description": "Mixed scenario with critical shortages, overstocks, and balanced items for full agent testing",
    "store_configs": {
        # Chennai - Metro hub, CRITICAL shortage on winterwear & denim, overstocked on traditional
        "STORE_CHN": {
            "PROD_WS001": 45, "PROD_LJ002": 80, "PROD_TH008": 120,  # CRITICAL - winter items
            "PROD_CK003": 2200, "PROD_SK007": 1800, "PROD_PJ009": 1650,  # OVERSTOCKED - traditional
            "PROD_DJ004": 95, "PROD_FC006": 180, "PROD_CT010": 220, "PROD_SH011": 350,  # LOW - bottoms
            "PROD_PS005": 750, "PROD_CT012": 680, "PROD_HN013": 720, "PROD_LS014": 580,  # BALANCED
            "PROD_FS015": 420, "PROD_BZ016": 65, "PROD_FT017": 380,  # LOW/CRITICAL formal
            "PROD_JG018": 850, "PROD_SW019": 150, "PROD_TK020": 280,
            "issue": "CRITICAL_WINTER_SHORTAGE"
        },
        # Coimbatore - Industrial hub, OVERSTOCKED on formal, LOW on casual
        "STORE_CBE": {
            "PROD_WS001": 650, "PROD_LJ002": 580, "PROD_TH008": 420, 
            "PROD_CK003": 380, "PROD_SK007": 250, "PROD_PJ009": 320,  # LOW traditional
            "PROD_DJ004": 180, "PROD_FC006": 2100, "PROD_CT010": 1850, "PROD_SH011": 120,  # Mixed bottoms
            "PROD_PS005": 95, "PROD_CT012": 85, "PROD_HN013": 110, "PROD_LS014": 450,  # CRITICAL casual
            "PROD_FS015": 1950, "PROD_BZ016": 2200, "PROD_FT017": 1780,  # OVERSTOCKED formal
            "PROD_JG018": 520, "PROD_SW019": 480, "PROD_TK020": 550,
            "issue": "OVERSTOCKED_FORMAL"
        },
        # Madurai - Temple city, CRITICAL on traditional (sold out!), overstocked on western
        "STORE_MDU": {
            "PROD_WS001": 1850, "PROD_LJ002": 1680, "PROD_TH008": 1520,  # OVERSTOCKED winter
            "PROD_CK003": 35, "PROD_SK007": 28, "PROD_PJ009": 55,  # CRITICAL - traditional sold out!
            "PROD_DJ004": 1450, "PROD_FC006": 1320, "PROD_CT010": 1180, "PROD_SH011": 980,  # OVERSTOCKED
            "PROD_PS005": 420, "PROD_CT012": 380, "PROD_HN013": 350, "PROD_LS014": 280,
            "PROD_FS015": 520, "PROD_BZ016": 1650, "PROD_FT017": 1420,
            "PROD_JG018": 280, "PROD_SW019": 320, "PROD_TK020": 250,
            "issue": "CRITICAL_TRADITIONAL_SHORTAGE"
        },
        # Trichy - Tech hub, CRITICAL athleisure shortage, balanced others
        "STORE_TCH": {
            "PROD_WS001": 450, "PROD_LJ002": 520, "PROD_TH008": 65,  # CRITICAL hoodie
            "PROD_CK003": 380, "PROD_SK007": 420, "PROD_PJ009": 350,
            "PROD_DJ004": 680, "PROD_FC006": 720, "PROD_CT010": 580, "PROD_SH011": 620,
            "PROD_PS005": 85, "PROD_CT012": 75, "PROD_HN013": 95, "PROD_LS014": 180,  # CRITICAL casual
            "PROD_FS015": 420, "PROD_BZ016": 380, "PROD_FT017": 450,
            "PROD_JG018": 42, "PROD_SW019": 55, "PROD_TK020": 68,  # CRITICAL athleisure
            "issue": "CRITICAL_ATHLEISURE"
        },
        # Salem - DONOR store, massively overstocked on everything
        "STORE_SLM": {
            "PROD_WS001": 2450, "PROD_LJ002": 2280, "PROD_TH008": 2150, 
            "PROD_CK003": 1980, "PROD_SK007": 1850, "PROD_PJ009": 1720,
            "PROD_DJ004": 2350, "PROD_FC006": 2180, "PROD_CT010": 1950, "PROD_SH011": 1820,
            "PROD_PS005": 2420, "PROD_CT012": 2580, "PROD_HN013": 2350, "PROD_LS014": 2150,
            "PROD_FS015": 2280, "PROD_BZ016": 1950, "PROD_FT017": 2120,
            "PROD_JG018": 2380, "PROD_SW019": 2520, "PROD_TK020": 2250,
            "issue": "MASSIVELY_OVERSTOCKED_DONOR"
        },
        # Tiruppur - Textile city, overstocked winter, CRITICAL on summer items
        "STORE_TPR": {
            "PROD_WS001": 2650, "PROD_LJ002": 2480, "PROD_TH008": 2320,  # OVERSTOCKED winter
            "PROD_CK003": 580, "PROD_SK007": 520, "PROD_PJ009": 480,
            "PROD_DJ004": 720, "PROD_FC006": 680, "PROD_CT010": 620, "PROD_SH011": 38,  # CRITICAL shorts
            "PROD_PS005": 45, "PROD_CT012": 52, "PROD_HN013": 48, "PROD_LS014": 35,  # CRITICAL summer
            "PROD_FS015": 620, "PROD_BZ016": 2150, "PROD_FT017": 680,
            "PROD_JG018": 720, "PROD_SW019": 2480, "PROD_TK020": 2250,
            "issue": "WINTER_OVERSTOCKED_SUMMER_CRITICAL"
        },
        # Vellore - University town, CRITICAL denim/casual (students bought all)
        "STORE_VLR": {
            "PROD_WS001": 480, "PROD_LJ002": 520, "PROD_TH008": 65, 
            "PROD_CK003": 1250, "PROD_SK007": 1180, "PROD_PJ009": 1080,  # OVERSTOCKED traditional
            "PROD_DJ004": 28, "PROD_FC006": 45, "PROD_CT010": 35, "PROD_SH011": 22,  # CRITICAL bottoms
            "PROD_PS005": 18, "PROD_CT012": 25, "PROD_HN013": 32, "PROD_LS014": 420,  # CRITICAL casual
            "PROD_FS015": 1480, "PROD_BZ016": 1350, "PROD_FT017": 1280,  # OVERSTOCKED formal
            "PROD_JG018": 55, "PROD_SW019": 480, "PROD_TK020": 520,
            "issue": "CRITICAL_YOUTH_ITEMS"
        },
        # Thanjavur - Festival hub, sold out on sarees/kurtas (festival rush)
        "STORE_TJV": {
            "PROD_WS001": 850, "PROD_LJ002": 780, "PROD_TH008": 720, 
            "PROD_CK003": 15, "PROD_SK007": 8, "PROD_PJ009": 22,  # CRITICAL - festival rush!
            "PROD_DJ004": 1580, "PROD_FC006": 1450, "PROD_CT010": 1320, "PROD_SH011": 1180,  # OVERSTOCKED
            "PROD_PS005": 550, "PROD_CT012": 620, "PROD_HN013": 480, "PROD_LS014": 420,
            "PROD_FS015": 680, "PROD_BZ016": 550, "PROD_FT017": 620,
            "PROD_JG018": 480, "PROD_SW019": 420, "PROD_TK020": 380,
            "issue": "FESTIVAL_SELLOUT"
        },
        # Erode - Small town, understocked on everything (supply chain issues)
        "STORE_ERD": {
            "PROD_WS001": 85, "PROD_LJ002": 95, "PROD_TH008": 78, 
            "PROD_CK003": 120, "PROD_SK007": 95, "PROD_PJ009": 110,
            "PROD_DJ004": 65, "PROD_FC006": 88, "PROD_CT010": 75, "PROD_SH011": 58,
            "PROD_PS005": 92, "PROD_CT012": 105, "PROD_HN013": 82, "PROD_LS014": 68,
            "PROD_FS015": 78, "PROD_BZ016": 55, "PROD_FT017": 72,
            "PROD_JG018": 85, "PROD_SW019": 62, "PROD_TK020": 75,
            "issue": "SUPPLY_CHAIN_CRITICAL"
        },
        # Nagercoil - Mall store, balanced but trending items selling fast
        "STORE_NGL": {
            "PROD_WS001": 650, "PROD_LJ002": 720, "PROD_TH008": 180,  # LOW hoodie (trending)
            "PROD_CK003": 580, "PROD_SK007": 520, "PROD_PJ009": 480,
            "PROD_DJ004": 220, "PROD_FC006": 680, "PROD_CT010": 620, "PROD_SH011": 550,  # LOW jeans
            "PROD_PS005": 185, "PROD_CT012": 165, "PROD_HN013": 195, "PROD_LS014": 580,  # LOW casual
            "PROD_FS015": 620, "PROD_BZ016": 550, "PROD_FT017": 680,
            "PROD_JG018": 145, "PROD_SW019": 480, "PROD_TK020": 420,  # LOW joggers
            "issue": "TRENDING_ITEMS_SELLING"
        },
    },
    "sales": [
        # Chennai - High sales across categories
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 85, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 78, "days_ago": 2},
        {"store_id": "STORE_CHN", "product_id": "PROD_LJ002", "quantity": 65, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_DJ004", "quantity": 92, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_CT012", "quantity": 120, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_PS005", "quantity": 88, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_BZ016", "quantity": 45, "days_ago": 1},
        
        # Coimbatore - Steady sales
        {"store_id": "STORE_CBE", "product_id": "PROD_FS015", "quantity": 55, "days_ago": 1},
        {"store_id": "STORE_CBE", "product_id": "PROD_FT017", "quantity": 48, "days_ago": 1},
        {"store_id": "STORE_CBE", "product_id": "PROD_FC006", "quantity": 62, "days_ago": 1},
        {"store_id": "STORE_CBE", "product_id": "PROD_DJ004", "quantity": 58, "days_ago": 2},
        {"store_id": "STORE_CBE", "product_id": "PROD_LJ002", "quantity": 42, "days_ago": 1},
        
        # Madurai - Traditional wear high demand
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 95, "days_ago": 1},
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 88, "days_ago": 2},
        {"store_id": "STORE_MDU", "product_id": "PROD_SK007", "quantity": 35, "days_ago": 1},
        {"store_id": "STORE_MDU", "product_id": "PROD_SK007", "quantity": 42, "days_ago": 2},
        {"store_id": "STORE_MDU", "product_id": "PROD_PJ009", "quantity": 65, "days_ago": 1},
        {"store_id": "STORE_MDU", "product_id": "PROD_DJ004", "quantity": 28, "days_ago": 1},
        
        # Trichy - Athleisure trending
        {"store_id": "STORE_TCH", "product_id": "PROD_TH008", "quantity": 72, "days_ago": 1},
        {"store_id": "STORE_TCH", "product_id": "PROD_JG018", "quantity": 85, "days_ago": 1},
        {"store_id": "STORE_TCH", "product_id": "PROD_TK020", "quantity": 58, "days_ago": 1},
        {"store_id": "STORE_TCH", "product_id": "PROD_CT012", "quantity": 95, "days_ago": 1},
        {"store_id": "STORE_TCH", "product_id": "PROD_PS005", "quantity": 78, "days_ago": 2},
        {"store_id": "STORE_TCH", "product_id": "PROD_SH011", "quantity": 65, "days_ago": 1},
        
        # Salem - Low sales (overstocked)
        {"store_id": "STORE_SLM", "product_id": "PROD_WS001", "quantity": 12, "days_ago": 1},
        {"store_id": "STORE_SLM", "product_id": "PROD_LJ002", "quantity": 15, "days_ago": 1},
        {"store_id": "STORE_SLM", "product_id": "PROD_DJ004", "quantity": 22, "days_ago": 1},
        {"store_id": "STORE_SLM", "product_id": "PROD_CK003", "quantity": 18, "days_ago": 2},
        
        # Tiruppur - Slow winter sales
        {"store_id": "STORE_TPR", "product_id": "PROD_WS001", "quantity": 8, "days_ago": 1},
        {"store_id": "STORE_TPR", "product_id": "PROD_LJ002", "quantity": 10, "days_ago": 1},
        {"store_id": "STORE_TPR", "product_id": "PROD_SW019", "quantity": 6, "days_ago": 2},
        {"store_id": "STORE_TPR", "product_id": "PROD_BZ016", "quantity": 5, "days_ago": 1},
        {"store_id": "STORE_TPR", "product_id": "PROD_CT012", "quantity": 35, "days_ago": 1},
        
        # Vellore - Youth/student demand
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "quantity": 88, "days_ago": 1},
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "quantity": 75, "days_ago": 2},
        {"store_id": "STORE_VLR", "product_id": "PROD_CT012", "quantity": 105, "days_ago": 1},
        {"store_id": "STORE_VLR", "product_id": "PROD_PS005", "quantity": 82, "days_ago": 1},
        {"store_id": "STORE_VLR", "product_id": "PROD_SH011", "quantity": 68, "days_ago": 1},
        {"store_id": "STORE_VLR", "product_id": "PROD_JG018", "quantity": 55, "days_ago": 2},
        
        # Thanjavur - Festival sales
        {"store_id": "STORE_TJV", "product_id": "PROD_SK007", "quantity": 48, "days_ago": 1},
        {"store_id": "STORE_TJV", "product_id": "PROD_SK007", "quantity": 52, "days_ago": 2},
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "quantity": 85, "days_ago": 1},
        {"store_id": "STORE_TJV", "product_id": "PROD_PJ009", "quantity": 72, "days_ago": 1},
        {"store_id": "STORE_TJV", "product_id": "PROD_PJ009", "quantity": 65, "days_ago": 2},
        
        # Erode - Moderate sales
        {"store_id": "STORE_ERD", "product_id": "PROD_CT012", "quantity": 42, "days_ago": 1},
        {"store_id": "STORE_ERD", "product_id": "PROD_DJ004", "quantity": 35, "days_ago": 1},
        {"store_id": "STORE_ERD", "product_id": "PROD_CK003", "quantity": 38, "days_ago": 2},
        {"store_id": "STORE_ERD", "product_id": "PROD_PS005", "quantity": 32, "days_ago": 1},
        
        # Nagercoil - Mixed demand
        {"store_id": "STORE_NGL", "product_id": "PROD_DJ004", "quantity": 52, "days_ago": 1},
        {"store_id": "STORE_NGL", "product_id": "PROD_CT012", "quantity": 58, "days_ago": 1},
        {"store_id": "STORE_NGL", "product_id": "PROD_CK003", "quantity": 45, "days_ago": 1},
        {"store_id": "STORE_NGL", "product_id": "PROD_FS015", "quantity": 38, "days_ago": 2},
        {"store_id": "STORE_NGL", "product_id": "PROD_WS001", "quantity": 35, "days_ago": 1},
        
        # === TRENDING PRODUCTS - High sales exceeding forecasts ===
        # Chennai - Sweaters selling like crazy (trending)
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 180, "days_ago": 3},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 195, "days_ago": 4},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 210, "days_ago": 5},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 188, "days_ago": 6},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 175, "days_ago": 7},
        
        # Madurai - Traditional wear EXPLODING in sales (festival effect)
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 320, "days_ago": 3},
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 285, "days_ago": 4},
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "quantity": 350, "days_ago": 5},
        {"store_id": "STORE_MDU", "product_id": "PROD_SK007", "quantity": 220, "days_ago": 3},
        {"store_id": "STORE_MDU", "product_id": "PROD_SK007", "quantity": 195, "days_ago": 4},
        
        # Trichy - Athleisure viral trend
        {"store_id": "STORE_TCH", "product_id": "PROD_JG018", "quantity": 280, "days_ago": 3},
        {"store_id": "STORE_TCH", "product_id": "PROD_JG018", "quantity": 245, "days_ago": 4},
        {"store_id": "STORE_TCH", "product_id": "PROD_JG018", "quantity": 310, "days_ago": 5},
        {"store_id": "STORE_TCH", "product_id": "PROD_TH008", "quantity": 250, "days_ago": 3},
        {"store_id": "STORE_TCH", "product_id": "PROD_TH008", "quantity": 220, "days_ago": 4},
        
        # Vellore - Student rush on casual wear
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "quantity": 320, "days_ago": 3},
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "quantity": 295, "days_ago": 4},
        {"store_id": "STORE_VLR", "product_id": "PROD_CT012", "quantity": 285, "days_ago": 3},
        {"store_id": "STORE_VLR", "product_id": "PROD_CT012", "quantity": 260, "days_ago": 4},
        
        # Thanjavur - Festival traditional rush
        {"store_id": "STORE_TJV", "product_id": "PROD_SK007", "quantity": 280, "days_ago": 3},
        {"store_id": "STORE_TJV", "product_id": "PROD_SK007", "quantity": 310, "days_ago": 4},
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "quantity": 350, "days_ago": 3},
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "quantity": 380, "days_ago": 4},
    ],
    "forecasts": [
        # Chennai - High forecasts (understocking expected)
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "forecasted_demand": 1500, "confidence": 0.94},
        {"store_id": "STORE_CHN", "product_id": "PROD_LJ002", "forecasted_demand": 920, "confidence": 0.92},
        {"store_id": "STORE_CHN", "product_id": "PROD_DJ004", "forecasted_demand": 1100, "confidence": 0.95},
        {"store_id": "STORE_CHN", "product_id": "PROD_BZ016", "forecasted_demand": 780, "confidence": 0.88},
        {"store_id": "STORE_CHN", "product_id": "PROD_CT012", "forecasted_demand": 1500, "confidence": 0.93},
        {"store_id": "STORE_CHN", "product_id": "PROD_PS005", "forecasted_demand": 1200, "confidence": 0.91},
        {"store_id": "STORE_CHN", "product_id": "PROD_TH008", "forecasted_demand": 950, "confidence": 0.89},
        
        # Coimbatore - Balanced forecasts
        {"store_id": "STORE_CBE", "product_id": "PROD_FS015", "forecasted_demand": 800, "confidence": 0.90},
        {"store_id": "STORE_CBE", "product_id": "PROD_FT017", "forecasted_demand": 750, "confidence": 0.88},
        {"store_id": "STORE_CBE", "product_id": "PROD_FC006", "forecasted_demand": 850, "confidence": 0.91},
        {"store_id": "STORE_CBE", "product_id": "PROD_DJ004", "forecasted_demand": 800, "confidence": 0.89},
        {"store_id": "STORE_CBE", "product_id": "PROD_LJ002", "forecasted_demand": 720, "confidence": 0.87},
        
        # Madurai - High traditional demand
        {"store_id": "STORE_MDU", "product_id": "PROD_CK003", "forecasted_demand": 1800, "confidence": 0.96},
        {"store_id": "STORE_MDU", "product_id": "PROD_SK007", "forecasted_demand": 1200, "confidence": 0.94},
        {"store_id": "STORE_MDU", "product_id": "PROD_PJ009", "forecasted_demand": 1100, "confidence": 0.92},
        {"store_id": "STORE_MDU", "product_id": "PROD_DJ004", "forecasted_demand": 400, "confidence": 0.85},
        
        # Trichy - Athleisure high demand
        {"store_id": "STORE_TCH", "product_id": "PROD_TH008", "forecasted_demand": 1100, "confidence": 0.93},
        {"store_id": "STORE_TCH", "product_id": "PROD_JG018", "forecasted_demand": 1200, "confidence": 0.91},
        {"store_id": "STORE_TCH", "product_id": "PROD_TK020", "forecasted_demand": 950, "confidence": 0.89},
        {"store_id": "STORE_TCH", "product_id": "PROD_CT012", "forecasted_demand": 1400, "confidence": 0.94},
        {"store_id": "STORE_TCH", "product_id": "PROD_PS005", "forecasted_demand": 1150, "confidence": 0.90},
        {"store_id": "STORE_TCH", "product_id": "PROD_SH011", "forecasted_demand": 1050, "confidence": 0.88},
        
        # Salem - Low forecasts (overstocked)
        {"store_id": "STORE_SLM", "product_id": "PROD_WS001", "forecasted_demand": 250, "confidence": 0.82},
        {"store_id": "STORE_SLM", "product_id": "PROD_LJ002", "forecasted_demand": 280, "confidence": 0.80},
        {"store_id": "STORE_SLM", "product_id": "PROD_DJ004", "forecasted_demand": 350, "confidence": 0.78},
        {"store_id": "STORE_SLM", "product_id": "PROD_CT012", "forecasted_demand": 400, "confidence": 0.75},
        
        # Tiruppur - Very low winterwear forecasts
        {"store_id": "STORE_TPR", "product_id": "PROD_WS001", "forecasted_demand": 150, "confidence": 0.75},
        {"store_id": "STORE_TPR", "product_id": "PROD_LJ002", "forecasted_demand": 180, "confidence": 0.72},
        {"store_id": "STORE_TPR", "product_id": "PROD_SW019", "forecasted_demand": 120, "confidence": 0.70},
        {"store_id": "STORE_TPR", "product_id": "PROD_BZ016", "forecasted_demand": 100, "confidence": 0.68},
        {"store_id": "STORE_TPR", "product_id": "PROD_CT012", "forecasted_demand": 600, "confidence": 0.82},
        
        # Vellore - High youth/casual demand
        {"store_id": "STORE_VLR", "product_id": "PROD_DJ004", "forecasted_demand": 1400, "confidence": 0.95},
        {"store_id": "STORE_VLR", "product_id": "PROD_CT012", "forecasted_demand": 1500, "confidence": 0.93},
        {"store_id": "STORE_VLR", "product_id": "PROD_PS005", "forecasted_demand": 1250, "confidence": 0.91},
        {"store_id": "STORE_VLR", "product_id": "PROD_SH011", "forecasted_demand": 1100, "confidence": 0.89},
        {"store_id": "STORE_VLR", "product_id": "PROD_JG018", "forecasted_demand": 950, "confidence": 0.87},
        
        # Thanjavur - Festival traditional demand
        {"store_id": "STORE_TJV", "product_id": "PROD_SK007", "forecasted_demand": 1350, "confidence": 0.95},
        {"store_id": "STORE_TJV", "product_id": "PROD_CK003", "forecasted_demand": 1500, "confidence": 0.94},
        {"store_id": "STORE_TJV", "product_id": "PROD_PJ009", "forecasted_demand": 1200, "confidence": 0.92},
        
        # Erode - Moderate forecasts (understocked)
        {"store_id": "STORE_ERD", "product_id": "PROD_CT012", "forecasted_demand": 600, "confidence": 0.86},
        {"store_id": "STORE_ERD", "product_id": "PROD_DJ004", "forecasted_demand": 550, "confidence": 0.84},
        {"store_id": "STORE_ERD", "product_id": "PROD_CK003", "forecasted_demand": 520, "confidence": 0.82},
        {"store_id": "STORE_ERD", "product_id": "PROD_PS005", "forecasted_demand": 480, "confidence": 0.80},
        
        # Nagercoil - Mixed forecasts
        {"store_id": "STORE_NGL", "product_id": "PROD_DJ004", "forecasted_demand": 750, "confidence": 0.88},
        {"store_id": "STORE_NGL", "product_id": "PROD_CT012", "forecasted_demand": 800, "confidence": 0.87},
        {"store_id": "STORE_NGL", "product_id": "PROD_CK003", "forecasted_demand": 700, "confidence": 0.85},
        {"store_id": "STORE_NGL", "product_id": "PROD_FS015", "forecasted_demand": 650, "confidence": 0.83},
        {"store_id": "STORE_NGL", "product_id": "PROD_WS001", "forecasted_demand": 600, "confidence": 0.81},
    ],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_existing_stores():
    """Fetch all stores from sk_stores table."""
    table = dynamodb.Table(settings.stores_table)
    response = table.scan()
    return response.get('Items', [])

def clear_table(table_name: str):
    """Delete all items from a table."""
    try:
        table = dynamodb.Table(table_name)
        scan = table.scan()
        items = scan.get("Items", [])
        
        key_names = [k["AttributeName"] for k in table.key_schema]
        
        with table.batch_writer() as batch:
            for item in items:
                key = {k: item[k] for k in key_names if k in item}
                batch.delete_item(Key=key)
        
        print(f"  ✓ Cleared {len(items)} items from {table_name}")
    except Exception as e:
        print(f"  ✗ Error clearing {table_name}: {e}")

def put_item(table_name: str, item: dict):
    """Put an item into a table."""
    table = dynamodb.Table(table_name)
    serialized = {}
    for k, v in item.items():
        if isinstance(v, float):
            serialized[k] = Decimal(str(v))
        else:
            serialized[k] = v
    table.put_item(Item=serialized)

def seed_products():
    """Seed product data."""
    print("\n🏷️  Seeding products...")
    for product in PRODUCTS:
        put_item(settings.products_table, product)
    print(f"  ✓ Added {len(PRODUCTS)} products")

def seed_transfer_routes(stores):
    """Generate transfer routes between major hubs."""
    print("\n🚚 Seeding transfer routes...")
    
    # Create a full mesh for the demo stores (since we use a small subset)
    # This ensures any store can transfer to any other store for the demo scenarios
    active_stores = [s["store_id"] for s in stores]
    
    routes = []
    for source in active_stores:
        for target in active_stores:
            if source == target:
                continue
                
            # Add route
            routes.append({
                "route_id": f"{source}#{target}",
                "from_store_id": source,
                "to_store_id": target,
                "transit_days": 1, # Simplified for demo
                "cost_per_unit": 15,
                "is_active": True,
            })
    
    # Batch write all routes
    table = dynamodb.Table(settings.store_transfers_table)
    with table.batch_writer() as batch:
        for route in routes:
            # Convert float to Decimal if needed (though we use ints here)
            batch.put_item(Item=route)
    
    print(f"  ✓ Added {len(routes)} routes (full mesh)")

def seed_inventory(scenario: dict, stores):
    """Seed inventory for ALL stores."""
    print("\n📦 Seeding inventory...")
    count = 0
    
    # Old format shorthand mapping (for scenarios 1-3)
    old_product_keys = {"ws": "PROD_WS001", "lj": "PROD_LJ002", "ck": "PROD_CK003", "dj": "PROD_DJ004"}
    
    def get_stock_status(qty: int) -> str:
        """Calculate stock status based on quantity thresholds."""
        if qty <= 0:
            return "out_of_stock"
        elif qty < 100:
            return "low_stock"
        elif qty < 300:
            return "low_stock"  # Still low for these volumes
        else:
            return "in_stock"
    
    for store in stores:
        store_id = store["store_id"]
        config = scenario["store_configs"].get(store_id, {})
        
        # Check if this is new format (has PROD_ keys) or old format (has ws, lj, etc.)
        is_new_format = any(k.startswith("PROD_") for k in config.keys())
        
        if is_new_format:
            # New format: iterate through all products
            for product in PRODUCTS:
                product_id = product["product_id"]
                quantity = config.get(product_id, 800)  # Default 800 for missing products
                stock_status = get_stock_status(quantity)
                
                item = {
                    "store_id": store_id,
                    "sku": f"{product['sku_base']}#M#DEFAULT",
                    "product_id": product_id,
                    "quantity": quantity,
                    "stock_status": stock_status,
                    "safety_stock": 100,
                    "reorder_point": 80,
                    "last_updated": datetime.utcnow().isoformat(),
                }
                put_item(settings.inventory_table, item)
                count += 1
        else:
            # Old format: use shorthand keys
            if not config:
                config = {"ws": 50, "lj": 40, "ck": 50, "dj": 45}
            
            for key, product_id in old_product_keys.items():
                product = next((p for p in PRODUCTS if p["product_id"] == product_id), None)
                if not product:
                    continue
                
                quantity = config.get(key, 50)
                stock_status = get_stock_status(quantity)
                
                item = {
                    "store_id": store_id,
                    "sku": f"{product['sku_base']}#M#DEFAULT",
                    "product_id": product_id,
                    "quantity": quantity,
                    "stock_status": stock_status,
                    "safety_stock": 40 if quantity < 40 else 30,
                    "reorder_point": 25 if quantity < 25 else 20,
                    "last_updated": datetime.utcnow().isoformat(),
                }
                put_item(settings.inventory_table, item)
                count += 1
    
    print(f"  ✓ Added {count} inventory records")

def seed_sales(scenario: dict):
    """Seed sales data."""
    print("\n💰 Seeding sales data...")
    count = 0
    for sale in scenario["sales"]:
        sale_date = (datetime.utcnow() - timedelta(days=sale["days_ago"])).strftime("%Y-%m-%d")
        product = next((p for p in PRODUCTS if p["product_id"] == sale["product_id"]), None)
        if not product:
            continue
        
        item = {
            "store_product_id": f"{sale['store_id']}#{sale['product_id']}",
            "sale_date": sale_date,
            "store_id": sale["store_id"],
            "product_id": sale["product_id"],
            "quantity_sold": sale["quantity"],
            "revenue": sale["quantity"] * product["price"],
            "unit_price": product["price"],
        }
        put_item(settings.sales_table, item)
        count += 1
    print(f"  ✓ Added {count} sales records")

def seed_forecasts(scenario: dict, stores: list):
    """Seed ML demand forecasts for ALL product-store combinations."""
    import random
    print("\n📊 Seeding demand forecasts...")
    forecast_period = "2026-Q1"
    
    # Create lookup for explicit forecasts
    explicit_forecasts = {}
    for fc in scenario.get("forecasts", []):
        key = f"{fc['store_id']}#{fc['product_id']}"
        explicit_forecasts[key] = fc
    
    count = 0
    for store in stores:
        store_id = store["store_id"]
        for product in PRODUCTS:
            product_id = product["product_id"]
            key = f"{store_id}#{product_id}"
            
            # Use explicit forecast if available, otherwise generate a reasonable default
            if key in explicit_forecasts:
                fc = explicit_forecasts[key]
                forecasted_demand = fc["forecasted_demand"]
                confidence = fc["confidence"]
            else:
                # Generate default forecast based on category and store type
                # Base demand between 400-900 with some variance
                base_demand = random.randint(400, 900)
                
                # Adjust based on category popularity
                category = product.get("category", "")
                if category in ["Traditional", "Bottomwear"]:
                    base_demand = int(base_demand * 1.2)
                elif category in ["Winterwear", "Formalwear"]:
                    base_demand = int(base_demand * 0.8)
                
                forecasted_demand = base_demand
                confidence = round(random.uniform(0.75, 0.92), 2)
            
            item = {
                "product_store_id": f"{product_id}#{store_id}",
                "forecast_period": forecast_period,
                "store_id": store_id,
                "product_id": product_id,
                "product_name": product["name"],
                "forecasted_demand": forecasted_demand,
                "confidence": confidence,
                "model_version": "demo-v1",
                "generated_at": datetime.utcnow().isoformat(),
            }
            put_item(settings.demand_forecast_table, item)
            count += 1
    
    print(f"  ✓ Added {count} forecasts (all product-store combinations)")

def clear_all_data():
    """Clear demo tables."""
    print("\n🗑️  Clearing existing data...")
    tables = [
        settings.inventory_table,
        settings.sales_table,
        settings.demand_forecast_table,
        settings.decisions_table,
        settings.agent_activity_table,
        settings.agent_insights_table,
        settings.agent_runs_table,
    ]
    for table in tables:
        clear_table(table)

def seed_scenario(scenario_num: int):
    """Seed a specific demo scenario."""
    scenarios = {1: SCENARIO_1, 2: SCENARIO_2, 3: SCENARIO_3, 4: SCENARIO_4}
    scenario = scenarios.get(scenario_num, SCENARIO_1)
    
    print(f"\n{'='*60}")
    print(f"🎬 DEMO SCENARIO {scenario_num}: {scenario['name']}")
    print(f"   {scenario['description']}")
    print(f"{'='*60}")
    
    # Get existing stores
    stores = get_existing_stores()
    print(f"\n📍 Found {len(stores)} stores in database")
    
    # Clear existing data
    clear_all_data()
    
    # Seed data
    seed_products()
    seed_transfer_routes(stores)
    seed_inventory(scenario, stores)
    seed_sales(scenario)
    seed_forecasts(scenario, stores)
    
    print(f"\n{'='*60}")
    print(f"✅ SCENARIO {scenario_num} READY!")
    print(f"   {len(stores)} stores with inventory, sales, and forecasts")
    print(f"   Run 'Agent Analysis' in the dashboard")
    print(f"{'='*60}\n")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo Data Seeder for SK Brands Retail AI")
    parser.add_argument("--scenario", type=int, choices=[1, 2, 3, 4], help="Scenario to seed (1, 2, 3, or 4)")
    parser.add_argument("--clear", action="store_true", help="Clear all demo data")
    
    args = parser.parse_args()
    
    if args.clear:
        clear_all_data()
        print("\n✅ All demo data cleared!\n")
    elif args.scenario:
        seed_scenario(args.scenario)
    else:
        print(__doc__)
        print("\nAvailable scenarios:")
        print("  1 - Winter Stock Crisis: Critical shortages (minimal data)")
        print("  2 - Spring Sales Opportunity: Seasonal transitions (minimal data)")
        print("  3 - Full Retail Operations: Comprehensive data for thorough demo")
        print("  4 - Comprehensive Analysis: 20 products, 200 inventory (500-1500 qty), rich sales & forecasts")
        print("\nExamples:")
        print("  python demo_seeder.py --scenario 1")
        print("  python demo_seeder.py --scenario 4  # Recommended for analysis")
        print("  python demo_seeder.py --clear")
