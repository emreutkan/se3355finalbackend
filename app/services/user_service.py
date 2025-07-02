from sqlalchemy import func
from typing import Dict

from ..models import db, User, Rating, Watchlist

class UserService:
    """Service class for user-related business logic"""
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """
        Get user statistics including ratings count, watchlist count, etc.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dictionary containing user statistics
        """
        try:
            # Get ratings count
            ratings_count = db.session.query(
                func.count(Rating.id)
            ).filter(
                Rating.user_id == user_id
            ).scalar() or 0
            
            # Get watchlist count
            watchlist_count = db.session.query(
                func.count(Watchlist.movie_id)
            ).filter(
                Watchlist.user_id == user_id
            ).scalar() or 0
            
            # Get average rating given by user
            avg_rating_given = db.session.query(
                func.avg(Rating.rating)
            ).filter(
                Rating.user_id == user_id
            ).scalar()
            
            avg_rating_given = round(float(avg_rating_given), 2) if avg_rating_given else 0.0
            
            # Get favorite genres (based on highest rated movies)
            # This would require a Genre model in a full implementation
            # For now, return placeholder data
            
            return {
                'ratings_count': ratings_count,
                'watchlist_count': watchlist_count,
                'average_rating_given': avg_rating_given,
                'favorite_genres': []  # Placeholder
            }
            
        except Exception as e:
            print(f"Error getting user statistics: {str(e)}")
            return {
                'ratings_count': 0,
                'watchlist_count': 0,
                'average_rating_given': 0.0,
                'favorite_genres': []
            }
    
    def get_user_recommendations(self, user_id: str, limit: int = 10) -> list:
        """
        Get movie recommendations for a user based on their ratings and watchlist
        
        Args:
            user_id: UUID of the user
            limit: Number of recommendations to return
            
        Returns:
            List of recommended movies
        """
        try:
            # This is a simplified recommendation algorithm
            # In a real system, you'd use collaborative filtering or content-based recommendations
            
            # Get user's highly rated movies (rating >= 8)
            highly_rated_movies = db.session.query(Rating.movie_id).filter(
                Rating.user_id == user_id,
                Rating.rating >= 8
            ).subquery()
            
            # Get movies not yet rated by the user with high average ratings
            from ..models import Movie
            recommendations = db.session.query(Movie).filter(
                Movie.imdb_score >= 7.0,
                ~Movie.id.in_(
                    db.session.query(Rating.movie_id).filter(
                        Rating.user_id == user_id
                    )
                ),
                ~Movie.id.in_(
                    db.session.query(Watchlist.movie_id).filter(
                        Watchlist.user_id == user_id
                    )
                )
            ).order_by(
                Movie.imdb_score.desc()
            ).limit(limit).all()
            
            return [movie.to_dict(include_actors=False) for movie in recommendations]
            
        except Exception as e:
            print(f"Error getting user recommendations: {str(e)}")
            return []
    
    def validate_user_permissions(self, user_id: str, action: str) -> bool:
        """
        Validate if user has permission to perform an action
        
        Args:
            user_id: UUID of the user
            action: Action to validate (e.g., 'rate_movie', 'admin_create')
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Basic permissions - all authenticated users can rate and manage watchlist
            basic_actions = ['rate_movie', 'manage_watchlist', 'update_profile']
            if action in basic_actions:
                return True
            
            # Admin actions would require additional role checking
            # For now, return False for admin actions
            admin_actions = ['admin_create', 'admin_delete', 'admin_update']
            if action in admin_actions:
                # In a real system, check user.role == 'admin'
                return False
            
            return False
            
        except Exception as e:
            print(f"Error validating user permissions: {str(e)}")
            return False 