from flask import Blueprint, request, jsonify, current_app

from ..services.movie_service import MovieService

search_bp = Blueprint('search', __name__)
movie_service = MovieService()

@search_bp.route('', methods=['GET'])
def search():
    """General search endpoint for movies, actors, etc.
    ---
    tags:
      - Search
    summary: General search
    description: Search for movies, actors, and other content. Searches movie titles, summaries, and actors.
    parameters:
      - name: q
        in: query
        type: string
        required: true
        minLength: 1
        description: Search query
      - name: type
        in: query
        type: string
        enum: [all, title, summary, people]
        default: all
        description: "Type of search: 'all' (title+summary+actors), 'title' (title only), 'summary' (summary only), 'people' (actors only)"
    responses:
      200:
        description: Search results in Titles and People sections
        schema:
          type: object
          properties:
            query:
              type: string
              example: "brad pitt"
            type:
              type: string
              example: "all"
            results:
              type: object
              properties:
                titles:
                  type: array
                  description: Movies found (includes movies starring searched actors)
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      title:
                        type: string
                      year:
                        type: integer
                      imdb_score:
                        type: number
                        format: float
                people:
                  type: array
                  description: Actors found
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      full_name:
                        type: string
                      photo_url:
                        type: string
      400:
        description: Bad request - invalid search query
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Search query is required"
      500:
        description: Internal server error
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # all, title, people
        
        if not query:
            return jsonify({'msg': 'Search query is required'}), 400
        
        # Validate search type
        valid_types = ['all', 'title', 'summary', 'people']
        if search_type not in valid_types:
            search_type = 'all'
        
        results = movie_service.search_movies(query, search_type)
        
        return jsonify({
            'query': query,
            'type': search_type,
            'results': results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@search_bp.route('/typeahead', methods=['GET'])
def typeahead():
    """Typeahead search endpoint for auto-complete
    ---
    tags:
      - Search
    summary: Typeahead search (3+ characters)
    description: Fast typeahead search for auto-complete functionality. Shows maximum of 3 top items that satisfy the search text when user types 3+ letters.
    parameters:
      - name: q
        in: query
        type: string
        required: true
        minLength: 3
        description: Search query for typeahead suggestions (minimum 3 characters)
    responses:
      200:
        description: Typeahead suggestions (max 3 items)
        schema:
          type: object
          properties:
            query:
              type: string
              example: "bat"
            suggestions:
              type: array
              maxItems: 3
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  type:
                    type: string
                    enum: [movie, actor]
                  year:
                    type: integer
                  image_url:
                    type: string
      400:
        description: Need at least 3 characters
      500:
        description: Internal server error
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'suggestions': []}), 200
        
        # Requirement: "On first three letters, show maximum of 3 top items"
        if len(query) < 3:
            return jsonify({'msg': 'Please enter at least 3 characters for suggestions'}), 400
        
        suggestions = movie_service.get_typeahead_suggestions(query)
        
        return jsonify({
            'query': query,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Typeahead error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500 