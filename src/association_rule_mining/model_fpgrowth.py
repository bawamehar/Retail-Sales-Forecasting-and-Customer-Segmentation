from mlxtend.frequent_patterns import fpgrowth, association_rules

def run_fpgrowth_analysis(basket, min_support=0.01, min_threshold=1.2, min_confidence=0.6):
 
    frequent_itemsets = fpgrowth(basket, min_support=min_support, use_colnames=True)
    
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_threshold)
    
    rules = rules[rules['confidence'] >= min_confidence]
    
    rules_final = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].round(3)
    
    return rules_final.sort_values('lift', ascending=False)