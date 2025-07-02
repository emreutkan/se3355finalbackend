from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import joinedload

from ..models import db, Movie, Actor, MovieActor, Rating, User, PopularitySnapshot, Watchlist, MovieCategory
from ..services.movie_service import MovieService
from ..utils.validators import validate_rating

movies_bp = Blueprint('movies', __name__)
movie_service = MovieService()

@movies_bp.route('', methods=['GET'])
def get_movies():
    """Get paginated list of movies with filtering and sorting
    ---
    tags:
      - Movies
    summary: Get movies list
    description: Retrieve a paginated list of movies with optional filtering and sorting
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
      - name: sort
        in: query
        type: string
        enum: [popularity, rating, year, title]
        default: popularity
        description: Sort movies by field
      - name: search
        in: query
        type: string
        description: Search in movie title, original title, or summary
      - name: year
        in: query
        type: integer
        description: Filter by release year
      - name: min_rating
        in: query
        type: number
        format: float
        minimum: 0
        maximum: 10
        description: Filter by minimum IMDB rating
    responses:
      200:
        description: Movies retrieved successfully
        schema:
          type: object
          properties:
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
                  original_title:
                    type: string
                  year:
                    type: integer
                  summary:
                    type: string
                  imdb_score:
                    type: number
                    format: float
                  runtime_min:
                    type: integer
                  language:
                    type: string
                  image_url:
                    type: string
                  trailer_url:
                    type: string
                  release_date:
                    type: string
                    format: date
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
                        photo_url:
                          type: string
                  rating_count:
                    type: integer
                  popularity:
                    type: object
                    properties:
                      score:
                        type: number
                        format: float
                      snapshot_date:
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
      500:
        description: Internal server error
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        sort = request.args.get('sort', 'popularity')  # popularity, rating, year, title
        search = request.args.get('search', '')
        year = request.args.get('year', type=int)
        min_rating = request.args.get('min_rating', type=float)
        
        # Validate pagination parameters
        if size > 100:
            size = 100
        if page < 1:
            page = 1
        
        # Base query
        query = Movie.query.options(
            joinedload(Movie.ratings), 
            joinedload(Movie.categories).joinedload(MovieCategory.category)
        )
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Movie.title.ilike(search_term),
                    Movie.original_title.ilike(search_term),
                    Movie.summary.ilike(search_term)
                )
            )
        
        # Apply year filter
        if year:
            query = query.filter(Movie.year == year)
        
        # Apply rating filter
        if min_rating:
            query = query.filter(Movie.imdb_score >= min_rating)
        
        # Apply sorting
        if sort == 'popularity':
            # Subquery for latest popularity snapshots to sort on
            latest_snapshot_subq = db.session.query(
                PopularitySnapshot.movie_id,
                func.max(PopularitySnapshot.snapshot_date).label('latest_date')
            ).group_by(PopularitySnapshot.movie_id).subquery()

            query = query.outerjoin(
                latest_snapshot_subq,
                latest_snapshot_subq.c.movie_id == Movie.id
            ).outerjoin(
                PopularitySnapshot,
                and_(
                    PopularitySnapshot.movie_id == Movie.id,
                    PopularitySnapshot.snapshot_date == latest_snapshot_subq.c.latest_date
                )
            )
            query = query.order_by(db.case((PopularitySnapshot.score.is_(None), 1), else_=0), desc(PopularitySnapshot.score), desc(Movie.imdb_score))
        elif sort == 'rating':
            query = query.order_by(desc(Movie.imdb_score))
        elif sort == 'year':
            query = query.order_by(desc(Movie.year))
        elif sort == 'title':
            query = query.order_by(Movie.title)
        else:
            query = query.order_by(desc(Movie.created_at))
        
        # Execute paginated query
        pagination = query.paginate(
            page=page,
            per_page=size,
            error_out=False
        )
        
        movies = []
        for movie in pagination.items:
            # The movie object can be a tuple (Movie, PopularitySnapshot) if sorted by popularity
            current_movie = movie[0] if isinstance(movie, tuple) else movie
            movie_dict = current_movie.to_dict(include_actors=False, include_popularity=True)
            movie_dict['rating_count'] = len(current_movie.ratings)
            movies.append(movie_dict)
        
        return jsonify({
            'movies': movies,
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
        current_app.logger.error(f"Get movies error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('/<movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    """Get detailed movie information
    ---
    tags:
      - Movies
    summary: Get movie details
    description: Retrieve detailed information about a specific movie including actors, ratings, and popularity data
    parameters:
      - name: movie_id
        in: path
        type: string
        format: uuid
        required: true
        description: Movie ID
    responses:
      200:
        description: Movie details retrieved successfully
        schema:
          type: object
          properties:
            movie:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                title:
                  type: string
                original_title:
                  type: string
                year:
                  type: integer
                summary:
                  type: string
                imdb_score:
                  type: number
                  format: float
                runtime_min:
                  type: integer
                release_date:
                  type: string
                  format: date
                language:
                  type: string
                trailer_url:
                  type: string
                image_url:
                  type: string
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
                      photo_url:
                        type: string
                rating_count:
                  type: integer
                rating_distribution:
                  type: object
                  properties:
                    "1":
                      type: integer
                    "2":
                      type: integer
                    "3":
                      type: integer
                    "4":
                      type: integer
                    "5":
                      type: integer
                popularity:
                  type: object
                  properties:
                    score:
                      type: number
                      format: float
                    snapshot_date:
                      type: string
                      format: date-time
      404:
        description: Movie not found
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
        movie = Movie.query.options(
            joinedload(Movie.actors).joinedload(MovieActor.actor),
            joinedload(Movie.ratings)
        ).get(movie_id)
        
        if not movie:
            return jsonify({'msg': 'Movie not found'}), 404
        
        movie_dict = movie.to_dict(include_actors=True, include_popularity=True)
        
        # Add additional statistics
        movie_dict['rating_count'] = len(movie.ratings)
        movie_dict['rating_distribution'] = movie_service.get_rating_distribution(movie_id)
        
        return jsonify({'movie': movie_dict}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get movie detail error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('', methods=['POST'])
@jwt_required()
def create_movie():
    """Create a new movie (admin-only for seeding)
    ---
    tags:
      - Movies
    summary: Create a new movie
    description: Create a new movie entry (admin-only functionality for seeding data)
    security:
      - Bearer: []
    parameters:
      - in: body
        name: movie_data
        required: true
        schema:
          type: object
          required:
            - title
            - year
            - summary
          properties:
            title:
              type: string
              example: "The Shawshank Redemption"
            original_title:
              type: string
              example: "The Shawshank Redemption"
            year:
              type: integer
              example: 1994
            summary:
              type: string
              example: "Two imprisoned men bond over a number of years..."
            trailer_url:
              type: string
              format: uri
              example: "https://youtube.com/watch?v=xyz"
            image_url:
              type: string
              format: uri
              example: "https://example.com/movie-poster.jpg"
            runtime_min:
              type: integer
              example: 142
            release_date:
              type: string
              format: date
              example: "1994-09-23"
            language:
              type: string
              example: "English"
    responses:
      201:
        description: Movie created successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Movie created successfully"
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
                summary:
                  type: string
                created_at:
                  type: string
                  format: date-time
      400:
        description: Bad request - missing required fields
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Missing required field: title"
      401:
        description: Authentication required
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'msg': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'year', 'summary']
        for field in required_fields:
            if field not in data:
                return jsonify({'msg': f'Missing required field: {field}'}), 400
        
        # Create new movie
        movie = Movie(
            title=data['title'],
            original_title=data.get('original_title'),
            year=data['year'],
            summary=data['summary'],
            trailer_url=data.get('trailer_url'),
            image_url=data.get('image_url'),
            runtime_min=data.get('runtime_min'),
            release_date=data.get('release_date'),
            language=data.get('language')
        )
        
        db.session.add(movie)
        db.session.commit()
        
        return jsonify({
            'msg': 'Movie created successfully',
            'movie': movie.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create movie error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('/<movie_id>/ratings', methods=['GET'])
def get_movie_ratings(movie_id):
    """Get movie ratings with distribution by country
    ---
    tags:
      - Movies
    summary: Get movie ratings
    description: Retrieve all ratings for a specific movie with pagination and country distribution
    parameters:
      - name: movie_id
        in: path
        type: integer
        required: true
        description: Movie ID
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
        description: Movie ratings retrieved successfully
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
                  user:
                    type: object
                    properties:
                      id:
                        type: integer
                      full_name:
                        type: string
                      country:
                        type: string
                  rating:
                    type: integer
                    minimum: 1
                    maximum: 5
                  comment:
                    type: string
                  voter_country:
                    type: string
                  created_at:
                    type: string
                    format: date-time
            distribution:
              type: object
              properties:
                "1":
                  type: integer
                "2":
                  type: integer
                "3":
                  type: integer
                "4":
                  type: integer
                "5":
                  type: integer
                country_breakdown:
                  type: object
                  additionalProperties:
                    type: number
                    format: float
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
      404:
        description: Movie not found
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
        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'msg': 'Movie not found'}), 404
        
        # Get ratings with pagination
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        
        ratings_query = Rating.query.filter_by(movie_id=movie_id).options(
            joinedload(Rating.user)
        ).order_by(desc(Rating.created_at))
        
        pagination = ratings_query.paginate(
            page=page,
            per_page=size,
            error_out=False
        )
        
        ratings = [rating.to_dict() for rating in pagination.items]
        
        # Get distribution by country
        distribution = movie_service.get_rating_distribution(movie_id)
        
        return jsonify({
            'ratings': ratings,
            'distribution': distribution,
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
        current_app.logger.error(f"Get movie ratings error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('/<movie_id>/ratings', methods=['POST'])
@jwt_required()
def rate_movie(movie_id):
    """Rate a movie
    ---
    tags:
      - Movies
    summary: Rate a movie
    description: Submit a rating for a movie (authenticated users only)
    security:
      - Bearer: []
    parameters:
      - name: movie_id
        in: path
        type: string
        format: uuid
        required: true
        description: Movie ID to rate
      - in: body
        name: rating_data
        required: true
        schema:
          type: object
          required:
            - rating
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 10
              example: 8
            comment:
              type: string
              example: "Great movie with excellent acting!"
    responses:
      201:
        description: Rating submitted successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Rating submitted successfully"
            rating:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                user_id:
                  type: string
                  format: uuid
                movie_id:
                  type: string
                  format: uuid
                rating:
                  type: integer
                  minimum: 1
                  maximum: 10
                comment:
                  type: string
                voter_country:
                  type: string
                created_at:
                  type: string
                  format: date-time
      200:
        description: Rating updated successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Rating updated successfully"
            rating:
              type: object
      400:
        description: Invalid rating data
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Rating must be between 1 and 10"
      401:
        description: Authentication required
      404:
        description: Movie not found
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
        
        data = request.get_json()
        if not data or 'rating' not in data:
            return jsonify({'msg': 'Rating is required'}), 400
        
        if not validate_rating(data['rating']):
            return jsonify({'msg': 'Rating must be between 1 and 10'}), 400
        
        # Check if user has already rated this movie
        existing_rating = Rating.query.filter_by(
            movie_id=movie_id,
            user_id=current_user_id
        ).first()
        
        if existing_rating:
            # Update existing rating/comment - user can only have one rating per movie
            existing_rating.rating = data['rating']
            existing_rating.comment = data.get('comment')
            rating = existing_rating
            msg = 'Rating updated successfully'
            status_code = 200
        else:
            # Create new rating
            rating = Rating(
                movie_id=movie_id,
                user_id=current_user_id,
                rating=data['rating'],
                comment=data.get('comment'),
                voter_country=user.country
            )
            db.session.add(rating)
            msg = 'Rating submitted successfully'
            status_code = 201
        
        db.session.commit()
        
        # Update movie's cached average rating
        movie_service.update_movie_rating(movie_id)
        
        return jsonify({
            'msg': msg,
            'rating': rating.to_dict()
        }), status_code
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Rate movie error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('/<movie_id>/ratings/me', methods=['GET'])
@jwt_required()
def get_user_movie_rating(movie_id):
    """Get current user's rating for a specific movie
    ---
    tags:
      - Movies
    summary: Get user's movie rating
    description: Retrieve the authenticated user's rating and comment for a specific movie
    security:
      - Bearer: []
    parameters:
      - name: movie_id
        in: path
        type: string
        format: uuid
        required: true
        description: Movie ID
    responses:
      200:
        description: User's rating found
        schema:
          type: object
          properties:
            rating:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                movie_id:
                  type: string
                  format: uuid
                user_id:
                  type: string
                  format: uuid
                rating:
                  type: integer
                  minimum: 1
                  maximum: 10
                comment:
                  type: string
                voter_country:
                  type: string
                created_at:
                  type: string
                  format: date-time
      401:
        description: Authentication required
      404:
        description: No rating found for this user and movie
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "No rating found for this user and movie"
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if movie exists
        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'msg': 'Movie not found'}), 404
        
        # Query for user's rating on this specific movie
        user_rating = Rating.query.filter_by(
            movie_id=movie_id,
            user_id=current_user_id
        ).first()
        
        if user_rating:
            return jsonify({
                'rating': user_rating.to_dict()
            }), 200
        else:
            return jsonify({
                'msg': 'No rating found for this user and movie'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Get user movie rating error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('/<movie_id>/popularity', methods=['GET'])
def get_movie_popularity(movie_id):
    """Get movie's latest popularity snapshot
    ---
    tags:
      - Movies
    summary: Get movie popularity
    description: Retrieve the latest popularity data for a specific movie
    parameters:
      - name: movie_id
        in: path
        type: integer
        required: true
        description: Movie ID
    responses:
      200:
        description: Movie popularity retrieved successfully
        schema:
          type: object
          properties:
            popularity:
              type: object
              properties:
                id:
                  type: integer
                movie_id:
                  type: integer
                score:
                  type: number
                  format: float
                snapshot_date:
                  type: string
                  format: date-time
                views_count:
                  type: integer
                search_count:
                  type: integer
      404:
        description: Movie not found or no popularity data available
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "No popularity data available"
      500:
        description: Internal server error
    """
    try:
        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'msg': 'Movie not found'}), 404
        
        latest_snapshot = PopularitySnapshot.query.filter_by(
            movie_id=movie_id
        ).order_by(desc(PopularitySnapshot.snapshot_date)).first()
        
        if not latest_snapshot:
            return jsonify({'msg': 'No popularity data available'}), 404
        
        return jsonify({
            'popularity': latest_snapshot.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get movie popularity error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@movies_bp.route('/popular', methods=['GET'])
def get_popular_movies():
    """Get most popular movies based on latest snapshots
    ---
    tags:
      - Movies
    summary: Get popular movies
    description: Retrieve the most popular movies based on latest popularity snapshots
    parameters:
      - name: limit
        in: query
        type: integer
        minimum: 1
        maximum: 50
        default: 10
        description: Number of popular movies to return
    responses:
      200:
        description: Popular movies retrieved successfully
        schema:
          type: object
          properties:
            popular_movies:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  year:
                    type: integer
                  summary:
                    type: string
                  imdb_score:
                    type: number
                    format: float
                  image_url:
                    type: string
                  actors:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: integer
                        name:
                          type: string
                        photo_url:
                          type: string
                  popularity:
                    type: object
                    properties:
                      score:
                        type: number
                        format: float
                      snapshot_date:
                        type: string
                        format: date-time
                      views_count:
                        type: integer
                      search_count:
                        type: integer
      500:
        description: Internal server error
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50
        
        # Get latest snapshot date
        latest_date_subquery = db.session.query(
            func.max(PopularitySnapshot.snapshot_date)
        ).scalar_subquery()
        
        # Get movies with highest popularity scores
        popular_movies = db.session.query(Movie, PopularitySnapshot).join(
            PopularitySnapshot,
            Movie.id == PopularitySnapshot.movie_id
        ).filter(
            PopularitySnapshot.snapshot_date == latest_date_subquery
        ).order_by(
            desc(PopularitySnapshot.score)
        ).limit(limit).all()
        
        results = []
        for movie, snapshot in popular_movies:
            movie_dict = movie.to_dict(include_actors=True)
            movie_dict['popularity'] = snapshot.to_dict()
            results.append(movie_dict)
        
        return jsonify({'popular_movies': results}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get popular movies error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500
