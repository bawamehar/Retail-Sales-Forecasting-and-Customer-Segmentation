from mlxtend.frequent_patterns import apriori, association_rules

def generate_association_rules(basket, min_support=0.02, min_threshold=1.2, min_confidence=0.5):
    """
    Runs Apriori and generates Association Rules based on Lift and Confidence.
    """
    # 1. Find Frequent Itemsets
    frequent_items = apriori(basket, min_support=min_support, use_colnames=True)
    
    # 2. Generate Rules
    rules = association_rules(frequent_items, metric="lift", min_threshold=min_threshold)
    
    # 3. Apply your Confidence filter
    rules = rules[rules['confidence'] >= min_confidence]
    
    # 4. Select and Clean your columns
    rules_filtered = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
    rules_filtered = rules_filtered.round(3)
    
    return rules_filtered.sort_values('lift', ascending=False)