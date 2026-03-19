from mlxtend.frequent_patterns import apriori, association_rules

def generate_association_rules(basket, min_support=0.02, min_threshold=1.2, min_confidence=0.5):

    frequent_items = apriori(basket, min_support=min_support, use_colnames=True)
    
    rules = association_rules(frequent_items, metric="lift", min_threshold=min_threshold)
    rules = rules[rules['confidence'] >= min_confidence]
    
    rules_filtered = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
    rules_filtered = rules_filtered.round(3)
    
    return rules_filtered.sort_values('lift', ascending=False)