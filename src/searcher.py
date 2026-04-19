import src.db as db

def search(query):
    """
    Given a query, return all relevant URLs. 
    Returns list of triples: (relevant_url, origin_url, depth)
    """
    # Simple relevancy: assume keywords are separated by spaces
    keywords = [k.strip() for k in query.split() if k.strip()]
    
    if not keywords:
        return []
        
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # We will build a naive SQL query that checks if ANY keyword exists.
    # A true relevance score would rank by how many keywords match, but this 
    # suffices for the native-language project bounds.
    
    conditions = " OR ".join(["text_content LIKE ?" for _ in keywords])
    params = [f"%{k}%" for k in keywords]
    
    sql = f"""
        SELECT c.id, u.url, u.origin_url, u.depth, c.text_content
        FROM content_index c
        JOIN urls u ON c.url_id = u.id
        WHERE {conditions}
    """
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    
    # Calculate true relevance score based on keyword frequency overlapping
    scored_results = []
    for row in results:
        _id, relevant_url, origin_url, depth, text_content = row
        score = 0
        text_lower = text_content.lower()
        for k in keywords:
            score += text_lower.count(k.lower())
        
        scored_results.append({
            'url': relevant_url,
            'origin': origin_url,
            'depth': depth,
            'score': score
        })
        
    # Sort descending by score
    scored_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Map to expected output format
    triples = []
    for res in scored_results:
        triples.append((res['url'], res['origin'], res['depth']))
        
    return triples
