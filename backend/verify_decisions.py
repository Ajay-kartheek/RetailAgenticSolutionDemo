
import boto3
import json
from decimal import Decimal

# Helper to convert Decimal to float for printing
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('sk_decisions')

response = table.scan()
decisions = response.get('Items', [])

found = False
for d in decisions:
    # Check for transfer of Wool Blend Sweater (PROD_WS001) or generic transfer to CHN
    details = d.get('data', d.get('details', {}))  # Data might be in 'data' field
    product_id = details.get('product_id') or d.get('product_id')
    target_store = details.get('target_store_id') or d.get('store_id')
    
    if target_store == 'STORE_CHN':
        print(f"Found decision for STORE_CHN: {d.get('decision_type')} - {product_id}")
        if product_id == 'PROD_WS001':
            print("\n✅ FOUND MATCHING DECISION:")
            print(json.dumps(d, cls=DecimalEncoder, indent=2))
            found = True

if not found:
    print("\n❌ NO MATCHING DECISION FOUND for PROD_WS001 transfer to STORE_CHN.")
    print(f"Total decisions scanned: {len(decisions)}")
    # Print a few examples
    if decisions:
        print("Example decision:", json.dumps(decisions[0], cls=DecimalEncoder, indent=2))
