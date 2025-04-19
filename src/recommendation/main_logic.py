from typing import List, Dict, Tuple

def sort_articles(
    preferences: List[str],
    weights: Dict[str, float],
    interactions: Dict[str, Tuple[int, float]],
    articles: List[Dict]
) -> List[Dict]:
    """
    Rank a list of articles by user preference and engagement.

    :param preferences: Ordered list of user preference categories.
    :param weights: Mapping from preference category to its weight.
    :param interactions: Mapping from category to a tuple (clicks, total_view_time).
    :param articles: List of articles with id, category, clicks, view_time.
    :return: Articles sorted by descending recommendation score.
    """
    scored = []
    
    max_clicks = max((art.get('clicks', 0) for art in articles), default=1)
    max_view_time = max((art.get('view_time', 0.0) for art in articles), default=1.0)
    
    for art in articles:
        cat = art.get('category')
        
        if cat in weights:
            art_clicks = art.get('clicks', 0) / max_clicks if max_clicks > 0 else 0
            art_time = art.get('view_time', 0.0) / max_view_time if max_view_time > 0 else 0
            
            preference_score = weights[cat]
            
            popularity_score = 0.6 * art_clicks + 0.4 * art_time
            
            user_clicks, user_time = interactions.get(cat, (0, 0.0))
            engagement_bonus = 0.0
            if user_clicks > 0 or user_time > 0:
                engagement_bonus = 0.2
            
            score = preference_score * (1.0 + popularity_score + engagement_bonus)
        else:
            score = 0.0
            
        scored.append((art, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored]

def update_weights(
    weights: Dict[str, float],
    interactions: Dict[str, Tuple[int, float]],
    article_category: str,
    clicked: bool,
    view_time: float,
    learning_rate: float = 0.1
) -> Dict[str, float]:
    """
    Update the weights when a user interacts with an article.

    :param weights: Current weights per category.
    :param interactions: Current interaction history.
    :param article_category: Category of the article.
    :param clicked: Whether the article was clicked.
    :param view_time: Time spent viewing the article.
    :param learning_rate: Weight adjustment rate.
    :return: Updated weights normalized to sum to 1.
    """
    prev_clicks, prev_time = interactions.get(article_category, (0, 0.0))
    interactions[article_category] = (prev_clicks + (1 if clicked else 0), prev_time + view_time)
    
    if article_category in weights:
        feedback = (1.0 if clicked else 0.0) + min(view_time / 60.0, 1.0)
        
        weights[article_category] += learning_rate * feedback
        
        total = sum(weights.values())
        if total > 0:
            for cat in weights:
                weights[cat] /= total
    
    return weights

# Example usage
if __name__ == "__main__":
    preferences = ["sports", "technology", "health"]
    weights = {"sports": 0.33, "technology": 0.33, "health": 0.33}

    interactions = {
        "sports": (0, 0),  # 10 clicks, 120 seconds view time
        "technology": (0, 0),  # 5 clicks, 60 seconds view time
        "health": (0, 0)  # 2 clicks, 30 seconds view time
    }

    articles = [
        {"id": 1, "category": "sports", "clicks": 15, "view_time": 200.0},
        {"id": 2, "category": "technology", "clicks": 5, "view_time": 50.0},
        {"id": 3, "category": "health", "clicks": 2, "view_time": 2000.0},
        {"id": 4, "category": "business", "clicks": 8, "view_time": 100.0},
        {"id": 5, "category": "technology", "clicks": 10, "view_time": 120.0}
    ]

    print("Sorted Articles:")
    sorted_articles = sort_articles(preferences, weights, interactions, articles)
    for article in sorted_articles:
        print(article)

    print("\nUpdated Weights:")
    updated_weights = update_weights(weights, interactions, "sports", True, 30.0)
    print(updated_weights)
