
import sys
import os
from pathlib import Path

# Add project root to python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, project_root)

from backend.agents.replenishment_agent.agent import ReplenishmentAgent
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class MockBedrock:
    def invoke_claude(self, **kwargs):
        print(" [MockBedrock] Invoking Claude (mocked)...")
        return """
Summary:
- Critical replenishment needed for Wool Blend Sweater at Chennai.
- Transfer available from Tiruppur.

Insights:
- High demand detected.
- Stock transfer is faster than manufacturer order.

Recommendations:
-approve_transfer_1
"""

print("Initializing Replenishment Agent...")
# Use mock bedrock to ensure we don't fail on LLM step (focus is on logic finding the plan)
agent = ReplenishmentAgent(bedrock_client=MockBedrock())

print("Running analysis...")
try:
    # Run analysis
    result = agent.analyze()
    
    print(f"Analysis complete. Generated {len(result.get('plans', []))} plans.\n")
    
    # Inspect internal valid plans vs skipped
    # Need to modify agent temporarily? 
    # Or just print 'plans' which are the NEW ones. 
    # If WS001 is missing here, and verification script says it's missing in DB, 
    # then maybe it wasn't found by search_inventory_items even after my fix?
    
    plans = result.get('plans', [])
    found = False
    for p in plans:
        pid = p.get('product_id')
        store = p.get('target_store_id')
        action = p.get('action_type')
        
        print(f"Plan: {pid} -> {store} ({action})")
        
        if pid == 'PROD_WS001' and store == 'STORE_CHN':
            print("\n✅ SUCCESS: Found Replenishment Plan for Wool Blend Sweater!")
            print(json.dumps(p, cls=DecimalEncoder, indent=2))
            found = True
            
    if not found:
        print("\n❌ FAILURE: Wool Blend Sweater plan NOT found.")
        print(f"Total plans: {len(plans)}")
        # Check if it was filtered by limit?
        # The agent limits to 10. If there are 14 valid plans, and WS001 is #11, it gets dropped.
        # Check prioritization.
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
