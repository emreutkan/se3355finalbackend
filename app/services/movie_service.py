import math
from datetime import datetime, timedelta
from sqlalchemy import func, desc, text
from typing import Dict, List

from ..models import db, Movie, Rating, PopularitySnapshot, Watchlist

class MovieService:
    """Service class for movie-related business logic"""
    
    def get_rating_distribution(self, movie_id: str) -> List[Dict]:
        """
        Get rating distribution by country for a movie
        
        Args:
            movie_id: UUID of the movie
            
        Returns:
            List of dictionaries with country, votes, and average rating
        """
        try:
            distribution = db.session.query(
                Rating.voter_country,
                func.count(Rating.id).label('votes'),
                func.avg(Rating.rating).label('avg_rating')
            ).filter(
                Rating.movie_id == movie_id
            ).group_by(
                Rating.voter_country
            ).order_by(
                desc('votes')
            ).all()
            
            return [
                {
                    'country': row.voter_country,
                    'votes': row.votes,
                    'avg_rating': round(float(row.avg_rating), 2) if row.avg_rating else 0.0
                }
                for row in distribution
            ]
            
        except Exception as e:
            print(f"Error getting rating distribution: {str(e)}")
            return []
    
    def update_movie_rating(self, movie_id: str) -> bool:
        """
        Update the cached average rating for a movie
        
        Args:
            movie_id: UUID of the movie
            
        Returns:
            True if successful, False otherwise
        """
        try:
            avg_rating = db.session.query(
                func.avg(Rating.rating)
            ).filter(
                Rating.movie_id == movie_id
            ).scalar()
            
            movie = Movie.query.get(movie_id)
            if movie:
                movie.imdb_score = round(float(avg_rating), 1) if avg_rating else 0.0
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating movie rating: {str(e)}")
            db.session.rollback()
            return False
    
    def calculate_popularity_score(self, movie_id: str) -> float:
        """
        Calculate popularity score using the algorithm:
        score = 0.5 * (avg_rating / 10) +
                0.2 * log10(comment_count + 1) +
                0.2 * log10(page_views_last_7d + 1) +
                0.1 * log10(watchlist_adds_last_7d + 1)
        
        Args:
            movie_id: UUID of the movie
            
        Returns:
            Calculated popularity score
        """
        try:
            # Get average rating
            avg_rating_decimal = db.session.query(
                func.avg(Rating.rating)
            ).filter(
                Rating.movie_id == movie_id
            ).scalar() or 0.0
            avg_rating = float(avg_rating_decimal)
            
            # Get comment count
            comment_count = db.session.query(
                func.count(Rating.id)
            ).filter(
                Rating.movie_id == movie_id,
                Rating.comment.isnot(None)
            ).scalar() or 0
            
            # Get watchlist adds in last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            watchlist_adds_7d = db.session.query(
                func.count(Watchlist.user_id)
            ).filter(
                Watchlist.movie_id == movie_id,
                Watchlist.added_at >= seven_days_ago
            ).scalar() or 0
            
            # For now, simulate page views (in a real app, this would come from analytics)
            page_views_7d = comment_count * 5  # Rough approximation
            
            # Calculate score components
            rating_component = 0.5 * (avg_rating / 10.0)
            comment_component = 0.2 * math.log10(comment_count + 1)
            views_component = 0.2 * math.log10(page_views_7d + 1)
            watchlist_component = 0.1 * math.log10(watchlist_adds_7d + 1)
            
            total_score = rating_component + comment_component + views_component + watchlist_component
            
            return round(total_score, 2)
            
        except Exception as e:
            print(f"Error calculating popularity score: {str(e)}")
            return 0.0
    
    def update_popularity_snapshots(self) -> bool:
        """
        Update popularity snapshots for all movies (to be run nightly)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            today = datetime.utcnow().date()
            
            # Get all movies
            movies = Movie.query.all()
            
            for movie in movies:
                # Calculate popularity score
                score = self.calculate_popularity_score(str(movie.id))
                
                # Create or update snapshot
                snapshot = PopularitySnapshot.query.filter_by(
                    movie_id=movie.id,
                    snapshot_date=today
                ).first()
                
                if snapshot:
                    snapshot.score = score
                else:
                    snapshot = PopularitySnapshot(
                        movie_id=movie.id,
                        snapshot_date=today,
                        score=score
                    )
                    db.session.add(snapshot)
            
            # Calculate ranks using SQLAlchemy (works on both MySQL and SQL Server)
            # Get all snapshots for today ordered by score
            snapshots_today = PopularitySnapshot.query.filter_by(
                snapshot_date=today
            ).order_by(PopularitySnapshot.score.desc()).all()
            
            # Update ranks
            for rank, snapshot in enumerate(snapshots_today, 1):
                snapshot.rank = rank
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Error updating popularity snapshots: {str(e)}")
            db.session.rollback()
            return False
    
    def search_movies(self, query: str, search_type: str = 'all') -> Dict:
        """
        Search movies by title, summary, or actors
        
        Search types:
        - 'all': searches titles, summaries, AND actors
        - 'title': searches only movie titles  
        - 'summary': searches only movie summaries
        - 'people': searches only actors
        
        When searching for an actor name, returns:
        1. The actor in 'people' section
        2. All movies starring that actor in 'titles' section
        
        Args:
            query: Search query string
            search_type: 'all', 'title', 'summary', or 'people'
            
        Returns:
            Dictionary with search results: {'titles': [], 'people': []}
        """
        try:
            results = {'titles': [], 'people': []}
            search_term = f"%{query}%"
            
            if search_type in ['all', 'title', 'summary']:
                movies_by_content = []
                
                # Search by title (for 'all' and 'title' types)
                if search_type in ['all', 'title']:
                    movies_by_title = Movie.query.filter(
                        db.or_(
                            Movie.title.ilike(search_term),
                            Movie.original_title.ilike(search_term)
                        )
                    ).limit(10).all()
                    movies_by_content.extend(movies_by_title)
                
                # Search by summary (for 'all' and 'summary' types)  
                if search_type in ['all', 'summary']:
                    movies_by_summary = Movie.query.filter(
                        Movie.summary.ilike(search_term)
                    ).limit(10).all()
                    movies_by_content.extend(movies_by_summary)
                
                # Search movies by actor names (only for 'all' type)
                if search_type == 'all':
                    from ..models import Actor, MovieActor
                    movies_by_actor = db.session.query(Movie).join(
                        MovieActor, Movie.id == MovieActor.movie_id
                    ).join(
                        Actor, MovieActor.actor_id == Actor.id
                    ).filter(
                        Actor.full_name.ilike(search_term)
                    ).limit(10).all()
                    movies_by_content.extend(movies_by_actor)
                
                # Combine and deduplicate movies
                all_movies = list(set(movies_by_content))
                results['titles'] = [movie.to_dict(include_actors=True) for movie in all_movies[:10]]
            
            if search_type in ['all', 'people']:
                # Search actors
                from ..models import Actor
                actors = Actor.query.filter(
                    Actor.full_name.ilike(search_term)
                ).limit(10).all()
                
                results['people'] = [actor.to_dict() for actor in actors]
            
            return results
            
        except Exception as e:
            print(f"Error searching movies: {str(e)}")
            return {'titles': [], 'people': []}
    
    def get_typeahead_suggestions(self, query: str) -> List[Dict]:
        """
        Get typeahead suggestions for search
        
        Shows maximum of 3 top items when user types 3+ letters.
        Prioritizes: exact matches, then popular movies, then actors.
        
        Args:
            query: Search query string (should be 3+ characters)
            
        Returns:
            List of suggestions (max 3 items)
        """
        try:
            suggestions = []
            search_term = f"%{query}%"
            exact_term = f"{query}%"  # For exact matches
            
            # Prioritize exact matches for movie titles
            exact_movies = Movie.query.filter(
                Movie.title.ilike(exact_term)
            ).order_by(Movie.imdb_score.desc()).limit(2).all()
            
            for movie in exact_movies:
                suggestions.append({
                    'type': 'movie',
                    'id': str(movie.id),
                    'title': movie.title,
                    'year': movie.year,
                    'image_url': movie.image_url,
                    'score': float(movie.imdb_score) if movie.imdb_score else 0.0
                })
            
            # If we still have room, add other movie matches
            if len(suggestions) < 3:
                other_movies = Movie.query.filter(
                    db.and_(
                        Movie.title.ilike(search_term),
                        ~Movie.title.ilike(exact_term)  # Exclude exact matches we already added
                    )
                ).order_by(Movie.imdb_score.desc()).limit(3 - len(suggestions)).all()
                
                for movie in other_movies:
                    suggestions.append({
                        'type': 'movie',
                        'id': str(movie.id),
                        'title': movie.title,
                        'year': movie.year,
                        'image_url': movie.image_url,
                        'score': float(movie.imdb_score) if movie.imdb_score else 0.0
                    })
            
            # If we still have room, add actor suggestions
            if len(suggestions) < 3:
                from ..models import Actor
                actors = Actor.query.filter(
                    Actor.full_name.ilike(search_term)
                ).limit(3 - len(suggestions)).all()
                
                for actor in actors:
                    suggestions.append({
                        'type': 'actor',
                        'id': str(actor.id),
                        'name': actor.full_name,
                        'photo_url': actor.photo_url
                    })
            
            return suggestions[:3]  # Ensure max 3 items
            
        except Exception as e:
            print(f"Error getting typeahead suggestions: {str(e)}")
            return [] 