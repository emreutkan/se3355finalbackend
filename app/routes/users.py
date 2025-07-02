from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

from ..models import db, User, Movie, Watchlist
from ..services.user_service import UserService

users_bp = Blueprint('users', __name__)
user_service = UserService()

@users_bp.route('/me/watchlist/<movie_id>', methods=['POST'])
@jwt_required()
def toggle_watchlist(movie_id):
    """Add or remove a movie from user's watchlist
    ---
    tags:
      - Users
    summary: Toggle movie in watchlist
    description: Add or remove a movie from the authenticated user's watchlist
    security:
      - Bearer: []
    parameters:
      - name: movie_id
        in: path
        type: string
        format: uuid
        required: true
        description: Movie ID to add/remove from watchlist
    responses:
      200:
        description: Watchlist updated successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Movie added to watchlist"
            action:
              type: string
              enum: [added, removed]
              example: "added"
            movie_id:
              type: string
              format: uuid
              example: "123e4567-e89b-12d3-a456-426614174000"
      401:
        description: Authentication required
      404:
        description: User or movie not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Movie not found"
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'msg': 'Movie not found'}), 404
        
        # Check if movie is already in watchlist
        existing = Watchlist.query.filter_by(
            user_id=current_user_id,
            movie_id=movie_id
        ).first()
        
        if existing:
            # Remove from watchlist
            db.session.delete(existing)
            action = 'removed'
        else:
            # Add to watchlist
            watchlist_item = Watchlist(
                user_id=current_user_id,
                movie_id=movie_id
            )
            db.session.add(watchlist_item)
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'msg': f'Movie {action} from watchlist',
            'action': action,
            'movie_id': movie_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Toggle watchlist error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@users_bp.route('/me/watchlist', methods=['GET'])
@jwt_required()
def get_user_watchlist():
    """Get user's watchlist with pagination
    ---
    tags:
      - Users
    summary: Get user watchlist
    description: Retrieve the authenticated user's watchlist with pagination
    security:
      - Bearer: []
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
        description: Number of movies per page
    responses:
      200:
        description: Watchlist retrieved successfully
        schema:
          type: object
          properties:
            watchlist:
              type: array
              items:
                type: object
                properties:
                  user_id:
                    type: string
                    format: uuid
                  movie_id:
                    type: string
                    format: uuid
                  movie:
                    type: object
                    properties:
                      id:
                        type: string
                        format: uuid
                      title:
                        type: string
                      year:
                        type: integer
                      image_url:
                        type: string
                      imdb_score:
                        type: number
                        format: float
                  added_at:
                    type: string
                    format: date-time
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
      401:
        description: Authentication required
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        
        # Validate pagination parameters
        if size > 100:
            size = 100
        if page < 1:
            page = 1
        
        # Get watchlist with pagination
        watchlist_query = Watchlist.query.filter_by(
            user_id=current_user_id
        ).options(
            joinedload(Watchlist.movie)
        ).order_by(Watchlist.added_at.desc())
        
        pagination = watchlist_query.paginate(
            page=page,
            per_page=size,
            error_out=False
        )
        
        watchlist_items = []
        for item in pagination.items:
            item_dict = item.to_dict()
            watchlist_items.append(item_dict)
        
        return jsonify({
            'watchlist': watchlist_items,
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
        current_app.logger.error(f"Get watchlist error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@users_bp.route('/me/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user's profile
    ---
    tags:
      - Users
    summary: Get user profile
    description: Retrieve the authenticated user's profile information and statistics
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            profile:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                email:
                  type: string
                full_name:
                  type: string
                country:
                  type: string
                city:
                  type: string
                photo_url:
                  type: string
                auth_provider:
                  type: string
                  enum: [local, google]
                created_at:
                  type: string
                  format: date-time
                statistics:
                  type: object
                  properties:
                    total_ratings:
                      type: integer
                    average_rating:
                      type: number
                      format: float
                    watchlist_count:
                      type: integer
                    favorite_genres:
                      type: array
                      items:
                        type: string
      401:
        description: Authentication required
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        # Get user statistics
        stats = user_service.get_user_statistics(current_user_id)
        
        profile = user.to_dict()
        profile['statistics'] = stats
        
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user profile error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@users_bp.route('/me/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update user's profile
    ---
    tags:
      - Users
    summary: Update user profile
    description: Update the authenticated user's profile information
    security:
      - Bearer: []
    parameters:
      - in: body
        name: profile_data
        required: true
        schema:
          type: object
          properties:
            full_name:
              type: string
              example: "John Doe"
            country:
              type: string
              pattern: "^[A-Z]{2}$"
              example: "US"
            city:
              type: string
              example: "New York"
            photo_url:
              type: string
              format: uri
              example: "https://example.com/photo.jpg"
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Profile updated successfully"
            profile:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                full_name:
                  type: string
                country:
                  type: string
                city:
                  type: string
                photo_url:
                  type: string
      400:
        description: Bad request - invalid data
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Invalid country code"
      401:
        description: Authentication required
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'msg': 'No data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['full_name', 'country', 'city', 'photo_url']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Validate country code if provided
        if 'country' in data:
            from ..utils.validators import validate_country_code
            if not validate_country_code(data['country']):
                return jsonify({'msg': 'Invalid country code'}), 400
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Profile updated successfully',
            'profile': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update profile error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@users_bp.route('/me/ratings', methods=['GET'])
@jwt_required()
def get_user_ratings():
    """Get user's movie ratings with pagination
    ---
    tags:
      - Users
    summary: Get user ratings
    description: Retrieve the authenticated user's movie ratings with pagination
    security:
      - Bearer: []
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
        description: Number of ratings per page
    responses:
      200:
        description: User ratings retrieved successfully
        schema:
          type: object
          properties:
            ratings:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  movie:
                    type: object
                    properties:
                      id:
                        type: integer
                      title:
                        type: string
                      year:
                        type: integer
                      image_url:
                        type: string
                  rating:
                    type: integer
                    minimum: 1
                    maximum: 5
                  review:
                    type: string
                  created_at:
                    type: string
                    format: date-time
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
      401:
        description: Authentication required
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        
        # Validate pagination parameters
        if size > 100:
            size = 100
        if page < 1:
            page = 1
        
        # Get ratings with pagination
        from ..models import Rating
        ratings_query = Rating.query.filter_by(
            user_id=current_user_id
        ).options(
            joinedload(Rating.movie)
        ).order_by(Rating.created_at.desc())
        
        pagination = ratings_query.paginate(
            page=page,
            per_page=size,
            error_out=False
        )
        
        ratings = []
        for rating in pagination.items:
            rating_dict = rating.to_dict(include_user=False)
            rating_dict['movie'] = rating.movie.to_dict(include_actors=False) if rating.movie else None
            ratings.append(rating_dict)
        
        return jsonify({
            'ratings': ratings,
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
        current_app.logger.error(f"👤 💥 Get user ratings error: {str(e)}", exc_info=True)
        return jsonify({
            'msg': 'Failed to retrieve user ratings',
            'details': f'Error: {str(e)}',
            'user_id': current_user_id if 'current_user_id' in locals() else 'unknown'
        }), 500 