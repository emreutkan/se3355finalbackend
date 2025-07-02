from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import joinedload

from ..models import db, Actor, MovieActor
from ..services.movie_service import MovieService

actors_bp = Blueprint('actors', __name__)
movie_service = MovieService()

@actors_bp.route('/<actor_id>', methods=['GET'])
def get_actor_detail(actor_id):
    """Get detailed actor information
    ---
    tags:
      - Actors
    summary: Get actor details
    description: Retrieve detailed information about a specific actor including their movies
    parameters:
      - name: actor_id
        in: path
        type: string
        format: uuid
        required: true
        description: Actor ID
    responses:
      200:
        description: Actor details retrieved successfully
        schema:
          type: object
          properties:
            actor:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                full_name:
                  type: string
                birth_date:
                  type: string
                  format: date
                bio:
                  type: string
                photo_url:
                  type: string
                movies:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        format: uuid
                      title:
                        type: string
                      year:
                        type: integer
                      imdb_score:
                        type: number
                        format: float
                      image_url:
                        type: string
      404:
        description: Actor not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Actor not found"
      500:
        description: Internal server error
    """
    try:
        actor = Actor.query.options(
            joinedload(Actor.movies).joinedload(MovieActor.movie)
        ).get(actor_id)
        
        if not actor:
            return jsonify({'msg': 'Actor not found'}), 404
        
        actor_dict = actor.to_dict(include_movies=True)
        
        return jsonify({'actor': actor_dict}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get actor detail error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@actors_bp.route('', methods=['GET'])
def search_actors():
    """Search actors with pagination
    ---
    tags:
      - Actors
    summary: Search actors
    description: Search for actors by name or bio with pagination
    parameters:
      - name: page
        in: query
        type: integer
        minimum: 1
        default: 1
        description: Page number
      - name: size
        in: query
        type: integer
        minimum: 1
        maximum: 100
        default: 20
        description: Number of actors per page
      - name: search
        in: query
        type: string
        description: Search term for actor name or bio
    responses:
      200:
        description: Actors search results
        schema:
          type: object
          properties:
            actors:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                  full_name:
                    type: string
                  birth_date:
                    type: string
                    format: date
                  bio:
                    type: string
                  photo_url:
                    type: string
            pagination:
              type: object
              properties:
                page:
                  type: integer
                size:
                  type: integer
                total:
                  type: integer
                pages:
                  type: integer
                has_next:
                  type: boolean
                has_prev:
                  type: boolean
      500:
        description: Internal server error
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        search = request.args.get('search', '')
        
        # Validate pagination parameters
        if size > 100:
            size = 100
        if page < 1:
            page = 1
        
        query = Actor.query
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Actor.full_name.ilike(search_term),
                    Actor.bio.ilike(search_term)
                )
            )
        
        # Order by name
        query = query.order_by(Actor.full_name)
        
        # Execute paginated query
        pagination = query.paginate(
            page=page,
            per_page=size,
            error_out=False
        )
        
        actors = [actor.to_dict() for actor in pagination.items]
        
        return jsonify({
            'actors': actors,
            'pagination': {
                'page': page,
                'size': size,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Search actors error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500 