import os
import sys
from datetime import date
from uuid import uuid4
import random

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Movie, Actor, MovieActor, User, Rating, PopularitySnapshot, Watchlist, Category, MovieCategory

def create_sample_movies():
    """Create sample movies"""
    movies_data = [
        {
            'title': 'The Shawshank Redemption',
            'title_tr': 'Esaretin Bedeli',
            'original_title': 'The Shawshank Redemption',
            'year': 1994,
            'summary': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            'summary_tr': 'İki mahkum adam, birkaç yıl boyunca aralarında bir bağ kurar, ortak nezaket eylemleriyle teselli ve nihai kurtuluşu bulur.',
            'imdb_score': 9.3, 'metascore': 80,
            'trailer_url': 'https://www.youtube.com/watch?v=6hB3S9bIaco',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BMDAyY2FhYjctNDc5OS00MDNlLThiMGUtY2UxYWVkNGY2ZjljXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 142,
            'release_date': date(1994, 9, 23),
            'language': 'English'
        },
        {
            'title': 'The Godfather',
            'title_tr': 'Baba',
            'original_title': 'The Godfather',
            'year': 1972,
            'summary': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
            'summary_tr': 'Yaşlanan bir organize suç hanedanının reisi, gizli imparatorluğunun kontrolünü isteksiz oğluna devreder.',
            'imdb_score': 9.2, 'metascore': 100,
            'trailer_url': 'https://www.youtube.com/watch?v=sY1S34973zA',
            'image_url': 'https://www.imdb.com/title/tt0068646/mediaviewer/rm746868224/?ref_=tt_ov_i',
            'runtime_min': 175,
            'release_date': date(1972, 3, 24),
            'language': 'English'
        },
        {
            'title': 'The Dark Knight',
            'title_tr': 'Kara Şövalye',
            'original_title': 'The Dark Knight',
            'year': 2008,
            'summary': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
            'summary_tr': 'Joker olarak bilinen tehdit Gotham halkına yıkım ve kaos getirdiğinde, Batman adaletsizlikle savaşma yeteneğinin en büyük psikolojik ve fiziksel testlerinden birini kabul etmelidir.',
            'imdb_score': 9.0, 'metascore': 84,
            'trailer_url': 'https://www.youtube.com/watch?v=EXeTwQWrcwY',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 152,
            'release_date': date(2008, 7, 18),
            'language': 'English'
        },
        {
            'title': 'Pulp Fiction',
            'title_tr': 'Ucuz Roman',
            'original_title': 'Pulp Fiction',
            'year': 1994,
            'summary': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
            'summary_tr': 'İki mafya tetikçisi, bir boksör, bir gangster ve karısı ile bir çift lokanta haydutunun hayatları, dört şiddet ve kurtuluş hikayesinde iç içe geçiyor.',
            'imdb_score': 8.9, 'metascore': 94,
            'trailer_url': 'https://www.youtube.com/watch?v=s7EdQ4FqbhY',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BYTViYTE3ZGQtNDBlMC00ZTAyLTkyODMtZGRiZDg0MjA2YThkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 154,
            'release_date': date(1994, 10, 14),
            'language': 'English'
        },
        {
            'title': "Schindler's List",
            'title_tr': "Schindler'in Listesi",
            'original_title': "Schindler's List",
            'year': 1993,
            'summary': 'In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.',
            'summary_tr': 'İkinci Dünya Savaşı sırasında Alman işgali altındaki Polonya\'da, sanayici Oskar Schindler, Naziler tarafından Yahudi işgücüne yapılan zulme tanık olduktan sonra yavaş yavaş onlar için endişelenmeye başlar.',
            'imdb_score': 8.9, 'metascore': 94,
            'trailer_url': 'https://www.youtube.com/watch?v=gG22XNhtnoY',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BNjM1ZDQxYWUtMzQyZS00MTE1LWJmZGYtNGUyNTdlYjM3ZmVmXkEyXkFqcGc@._V1_.jpg',
            'runtime_min': 195,
            'release_date': date(1993, 12, 15),
            'language': 'English'
        },
        {
            'title': 'Inception',
            'title_tr': 'Başlangıç',
            'original_title': 'Inception',
            'year': 2010,
            'summary': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'summary_tr': 'Rüya paylaşım teknolojisini kullanarak kurumsal sırları çalan bir hırsıza, bir CEO\'nun zihnine bir fikir ekme gibi ters bir görev verilir.',
            'imdb_score': 8.8, 'metascore': 74,
            'trailer_url': 'https://www.youtube.com/watch?v=YoHD9XEInc0',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 148,
            'release_date': date(2010, 7, 16),
            'language': 'English'
        },
        {
            'title': 'Forrest Gump',
            'title_tr': 'Forrest Gump',
            'original_title': 'Forrest Gump',
            'year': 1994,
            'summary': 'The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold from the perspective of an Alabama man with an IQ of 75.',
            'summary_tr': 'Kennedy ve Johnson başkanlıkları, Vietnam olayları, Watergate ve diğer tarihi olaylar, 75 IQ\'su olan bir Alabama\'lı adamın bakış açısından ortaya çıkıyor.',
            'imdb_score': 8.8, 'metascore': 82,
            'trailer_url': 'https://www.youtube.com/watch?v=bLvqoHBptjg',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BNDYwNzVjMTItZmU5YS00YjQ5LTljYjgtMjY2NDVmYWMyNWFmXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 142,
            'release_date': date(1994, 7, 6),
            'language': 'English'
        },
        {
            'title': 'The Matrix',
            'title_tr': 'Matrix',
            'original_title': 'The Matrix',
            'year': 1999,
            'summary': 'A computer programmer is led to fight an underground war against powerful computers who have constructed his entire reality with a system called the Matrix.',
            'summary_tr': 'Bir bilgisayar programcısı, tüm gerçekliğini Matrix adlı bir sistemle inşa eden güçlü bilgisayarlara karşı bir yeraltı savaşına girmeye yönlendirilir.',
            'imdb_score': 8.7, 'metascore': 73,
            'trailer_url': 'https://www.youtube.com/watch?v=vKQi3bBA1y8',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_.jpg',
            'runtime_min': 136,
            'release_date': date(1999, 3, 31),
            'language': 'English'
        },
        {
            'title': 'Goodfellas',
            'title_tr': 'Sıkı Dostlar',
            'original_title': 'Goodfellas',
            'year': 1990,
            'summary': 'The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.',
            'summary_tr': 'Henry Hill\'in ve mafyadaki hayatının hikayesi, karısı Karen Hill ve mafya ortaklarıyla olan ilişkisini kapsıyor.',
            'imdb_score': 8.7, 'metascore': 90,
            'trailer_url': 'https://www.youtube.com/watch?v=qo5jJpHtI1Y',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BN2E5NzI2ZGMtY2VjNi00YTRjLWI1MDUtZGY5OWU1MWJjZjRjXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 146,
            'release_date': date(1990, 9, 21),
            'language': 'English'
        },
        {
            'title': 'Interstellar',
            'title_tr': 'Yıldızlararası',
            'original_title': 'Interstellar',
            'year': 2014,
            'summary': "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            'summary_tr': "Bir grup kaşif, insanlığın hayatta kalmasını sağlamak amacıyla uzayda bir solucan deliğinden geçer.",
            'imdb_score': 8.6, 'metascore': 74,
            'trailer_url': 'https://www.youtube.com/watch?v=zSWdZVtXT7E',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BYzdjMDAxZGItMjI2My00ODA1LTlkNzItOWFjMDU5ZDJlYWY3XkEyXkFqcGc@._V1_.jpg',
            'runtime_min': 169,
            'release_date': date(2014, 11, 7),
            'language': 'English'
        },
        {
            'title': 'Fight Club',
            'title_tr': 'Dövüş Kulübü',
            'original_title': 'Fight Club',
            'year': 1999,
            'summary': 'An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into something much more.',
            'summary_tr': 'Uykusuz bir ofis çalışanı ve umursamaz bir sabun üreticisi, çok daha fazlasına dönüşen bir yeraltı dövüş kulübü kurar.',
            'imdb_score': 8.8, 'metascore': 66,
            'trailer_url': 'https://www.youtube.com/watch?v=SUXWAEX2jlg',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BOTgyOGQ1NDItNGU3Ny00MjU3LTg2YWEtNmEyYjBiMjI1Y2M5XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 139,
            'release_date': date(1999, 10, 15),
            'language': 'English'
        },
        {
            'title': 'The Lord of the Rings: The Fellowship of the Ring',
            'title_tr': 'Yüzüklerin Efendisi: Yüzük Kardeşliği',
            'original_title': 'The Lord of the Rings: The Fellowship of the Ring',
            'year': 2001,
            'summary': 'A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth.',
            'summary_tr': 'Shire\'dan uysal bir Hobbit ve sekiz yoldaşı, güçlü Tek Yüzük\'ü yok etmek ve Orta Dünya\'yı kurtarmak için bir yolculuğa çıkar.',
            'imdb_score': 8.8, 'metascore': 92,
            'trailer_url': 'https://www.youtube.com/watch?v=V75dMMIW2B4',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BNzIxMDQ2YTctNDY4MC00ZTRhLTk4ODQtMTVlOWY4NTdiYmMwXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 178,
            'release_date': date(2001, 12, 19),
            'language': 'English'
        },
        {
            'title': 'The Social Network',
            'title_tr': 'Sosyal Ağ',
            'original_title': 'The Social Network',
            'year': 2010,
            'summary': 'The story of the founding of Facebook and the lawsuits that followed.',
            'summary_tr': 'Facebook\'un kuruluşunun ve ardından gelen davaların hikayesi.',
            'imdb_score': 7.7, 'metascore': 95,
            'trailer_url': 'https://www.youtube.com/watch?v=lB95KLmpLR4',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BMjlkNTE5ZTUtNGEwNy00MGVhLThmZjMtZjU1NDE5Zjk1NDZkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 120,
            'release_date': date(2010, 10, 1),
            'language': 'English'
        },
        {
            'title': 'The Silence of the Lambs',
            'title_tr': 'Kuzuların Sessizliği',
            'original_title': 'The Silence of the Lambs',
            'year': 1991,
            'summary': 'A young FBI cadet must confide in an incarcerated and manipulative killer to receive his help on catching another serial killer.',
            'summary_tr': 'Genç bir FBI stajyeri, başka bir seri katili yakalamak için yardımını almak üzere hapsedilmiş ve manipülatif bir katile güvenmek zorundadır.',
            'imdb_score': 8.6, 'metascore': 85,
            'trailer_url': 'https://www.youtube.com/watch?v=W6Mm8Sbe__o',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BNDdhOGJhYzctYzYwZC00YmI2LWI0MjctYjg4ODdlMDExYjBlXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 118,
            'release_date': date(1991, 2, 14),
            'language': 'English'
        },
        {
            'title': 'The Empire Strikes Back',
            'title_tr': 'İmparatorun Dönüşü',
            'original_title': 'The Empire Strikes Back',
            'year': 1980,
            'summary': 'After the Rebels are brutally overpowered by the Empire on the ice planet Hoth, Luke Skywalker begins Jedi training with Yoda.',
            'summary_tr': 'Asiler, buz gezegeni Hoth\'ta İmparatorluk tarafından acımasızca alt edildikten sonra, Luke Skywalker Yoda ile Jedi eğitimine başlar.',
            'imdb_score': 8.7, 'metascore': 82,
            'trailer_url': 'https://www.youtube.com/watch?v=JNwNXF9Y6kY',
            'image_url': 'https://m.media-amazon.com/images/M/MV5BMTkxNGFlNDktZmJkNC00MDdhLTg0MTEtZjZiYWI3MGE5NWIwXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
            'runtime_min': 124,
            'release_date': date(1980, 5, 21),
            'language': 'English'
        }
    ]

    movies = []
    for movie_data in movies_data:
        movie = Movie(**movie_data)
        movies.append(movie)
        db.session.add(movie)

    db.session.commit()
    print(f"Created {len(movies)} movies")
    return movies

def create_sample_categories():
    """Create sample categories"""
    category_names = [
        'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
        'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History',
        'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
        'Short', 'Sport', 'Superhero', 'Thriller', 'War', 'Western'
    ]
    categories = []
    for name in category_names:
        category = Category.query.filter_by(name=name).first()
        if not category:
            category = Category(name=name)
            db.session.add(category)
            categories.append(category)
    
    db.session.commit()
    print(f"Created {len(categories)} categories")
    return Category.query.all()

def create_movie_category_relationships(movies, categories):
    """Create relationships between movies and categories using actual genres."""
    
    category_dict = {category.name: category for category in categories}
    
    movie_to_categories_map = {
        'The Shawshank Redemption': ['Drama', 'Crime'],
        'The Godfather': ['Crime', 'Drama'],
        'The Dark Knight': ['Action', 'Superhero', 'Thriller'],
        'Pulp Fiction': ['Crime', 'Drama'],
        "Schindler's List": ['Biography', 'Drama', 'History'],
        'Inception': ['Action', 'Sci-Fi', 'Thriller'],
        'Forrest Gump': ['Drama', 'Romance'],
        'The Matrix': ['Action', 'Sci-Fi'],
        'Goodfellas': ['Biography', 'Crime', 'Drama'],
        'Interstellar': ['Adventure', 'Drama', 'Sci-Fi'],
        'Fight Club': ['Drama', 'Thriller'],
        'The Lord of the Rings: The Fellowship of the Ring': ['Action', 'Adventure', 'Fantasy'],
        'The Social Network': ['Biography', 'Drama'],
        'The Silence of the Lambs': ['Crime', 'Thriller', 'Horror'],
        'The Empire Strikes Back': ['Action', 'Adventure', 'Sci-Fi']
    }

    movie_categories = []
    for movie in movies:
        category_names = movie_to_categories_map.get(movie.title, [])
        for cat_name in category_names:
            category = category_dict.get(cat_name)
            if category:
                # Check if relationship already exists
                existing_rel = MovieCategory.query.filter_by(movie_id=movie.id, category_id=category.id).first()
                if not existing_rel:
                    movie_category = MovieCategory(movie_id=movie.id, category_id=category.id)
                    movie_categories.append(movie_category)
                    db.session.add(movie_category)
            
    db.session.commit()
    print(f"Created {len(movie_categories)} movie-category relationships")

def create_sample_actors():
    """Create sample actors"""
    actors_data = [
        {'full_name': 'Morgan Freeman',       'bio': 'Morgan Freeman is an American actor, director, and narrator.',              'birth_date': date(1937, 6, 1),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Morgan_Freeman_at_The_Pentagon_on_2_August_2023_-_230802-D-PM193-3363_%28cropped%29.jpg'},
        {'full_name': 'Tim Robbins',          'bio': 'Tim Robbins is an American actor, screenwriter, director, producer, and musician.', 'birth_date': date(1958, 10, 16), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/6/61/Tim_Robbins_%28Berlin_Film_Festival_2013%29.jpg'},
        {'full_name': 'Marlon Brando',        'bio': 'Marlon Brando Jr. was an American actor and film director.',               'birth_date': date(1924, 4, 3),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/53/Marlon_Brando_publicity_for_One-Eyed_Jacks.png'},
        {'full_name': 'Al Pacino',            'bio': 'Al Pacino is an American actor and filmmaker.',                           'birth_date': date(1940, 4, 25),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Al_Pacino_2016_%2830401544240%29.jpg'},
        {'full_name': 'Christian Bale',       'bio': 'Christian Charles Philip Bale is an English actor.',                          'birth_date': date(1974, 1, 30),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0a/Christian_Bale-7837.jpg'},
        {'full_name': 'Heath Ledger',         'bio': 'Heath Andrew Ledger was an Australian actor and director.',                  'birth_date': date(1979, 4, 4),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Heath_Ledger%2C_2006.jpg'},
        {'full_name': 'John Travolta',        'bio': 'John Travolta is an American actor, producer, dancer, and singer.',         'birth_date': date(1954, 2, 18),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/f/f1/John_Travolta_2018.jpg'},
        {'full_name': 'Samuel L. Jackson',    'bio': 'Samuel L. Jackson is an American actor and producer.',                     'birth_date': date(1948, 12, 21), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Samuel_L._Jackson_2019_by_Glenn_Francis.jpg'},
        {'full_name': 'Leonardo DiCaprio',    'bio': 'Leonardo DiCaprio is an American actor, producer, and environmentalist.',   'birth_date': date(1974, 11, 11),'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/8/8c/Leonardo_Dicaprio_C%C3%A9sar_2017.jpg'},
        {'full_name': 'Tom Hanks',            'bio': 'Tom Hanks is an American actor and filmmaker.',                             'birth_date': date(1956, 7, 9),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/e/e1/Tom_Hanks_TIFF_2019.jpg'},
        {'full_name': 'Liam Neeson',          'bio': 'Liam Neeson is an Irish actor known for both blockbuster and art house films.', 'birth_date': date(1952, 6, 7),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Liam_Neeson_in_2008.jpg'},
        {'full_name': 'Ben Kingsley',         'bio': 'Sir Ben Kingsley is an English actor known for his versatile roles.',       'birth_date': date(1943, 12, 31), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Ben_Kingsley_Berlinale_2014_%28crop2%29.jpg'},
        {'full_name': 'Joseph Gordon-Levitt', 'bio': 'Joseph Gordon-Levitt is an American actor and filmmaker.',                   'birth_date': date(1981, 2, 17),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Joseph_Gordon-Levitt_2016.jpg'},
        {'full_name': 'Robin Wright',         'bio': 'Robin Wright is an American actress and director.',                         'birth_date': date(1966, 4, 8),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Robin_Wright_TIFF_2017.jpg'},
        {'full_name': 'Keanu Reeves',         'bio': 'Keanu Reeves is a Canadian actor known for action and dramatic roles.',     'birth_date': date(1964, 9, 2),   'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/Keanu_Reeves_2014.jpg'},
        {'full_name': 'Laurence Fishburne',   'bio': 'Laurence Fishburne is an American actor, playwright, and producer.',       'birth_date': date(1961, 7, 30),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Laurence_Fishburne_2013.jpg'},
        {'full_name': 'Robert De Niro',       'bio': 'Robert De Niro is an American actor and producer, co-founder of TriBeCa Productions.', 'birth_date': date(1943, 8, 17),'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/5e/Robert_De_Niro_2012.jpg'},
        {'full_name': 'Ray Liotta',           'bio': 'Ray Liotta was an American actor and film producer.',                      'birth_date': date(1954, 12, 18), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Ray_Liotta_by_Gage_Skidmore.jpg'},
        {'full_name': 'Matthew McConaughey',  'bio': 'Matthew McConaughey is an American actor and producer.',                   'birth_date': date(1969, 11, 4),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Matthew_McConaughey_2020.jpg'},
        {'full_name': 'Anne Hathaway',        'bio': 'Anne Hathaway is an American actress and singer.',                        'birth_date': date(1982, 11, 12), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Anne_Hathaway_Deauville_2016.jpg'},
        {'full_name': 'Brad Pitt',            'bio': 'Brad Pitt is an American actor and film producer.',                       'birth_date': date(1963, 12, 18), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/7/7c/Brad_Pitt_2019_by_Glenn_Francis.jpg'},
        {'full_name': 'Edward Norton',        'bio': 'Edward Norton is an American actor and filmmaker.',                        'birth_date': date(1969, 8, 18),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/d/d8/Edward_Norton_2015.jpg'},
        {'full_name': 'Elijah Wood',          'bio': 'Elijah Wood is an American actor and producer.',                           'birth_date': date(1981, 1, 28),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/d/d7/Elijah_Wood_2014.jpg'},
        {'full_name': 'Ian McKellen',         'bio': 'Sir Ian McKellen is an English actor known for fantasy and Shakespearean roles.', 'birth_date': date(1939, 5, 25), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/6/62/Ian_McKellen_by_Gage_Skidmore.jpg'},
        {'full_name': 'Jesse Eisenberg',      'bio': 'Jesse Eisenberg is an American actor and playwright.',                     'birth_date': date(1983, 10, 5),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/1/13/Jesse_Eisenberg_2012.jpg'},
        {'full_name': 'Andrew Garfield',      'bio': 'Andrew Garfield is an English-American actor.',                            'birth_date': date(1983, 8, 20),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/5a/Andrew_Garfield_at_2011_Le_C%C3%A9sar_Awards.jpg'},
        {'full_name': 'Jodie Foster',         'bio': 'Jodie Foster is an American actress, director, and producer.',             'birth_date': date(1962, 11, 19), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/5/5b/Jodie_Foster_2011.jpg'},
        {'full_name': 'Anthony Hopkins',      'bio': 'Sir Anthony Hopkins is a Welsh actor, director, and composer.',            'birth_date': date(1937, 12, 31), 'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/8/82/Anthony_Hopkins_2010.jpg'},
        {'full_name': 'Mark Hamill',          'bio': 'Mark Hamill is an American actor and voice artist.',                      'birth_date': date(1951, 9, 25),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/4/4c/Mark_Hamill_%282014%29.jpg'},
        {'full_name': 'Harrison Ford',        'bio': 'Harrison Ford is an American actor and film producer.',                   'birth_date': date(1942, 7, 13),  'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/9/97/Harrison_Ford_2018.jpg'},
    ]

    actors = []
    for actor_data in actors_data:
        actor = Actor(**actor_data)
        actors.append(actor)
        db.session.add(actor)

    db.session.commit()
    print(f"Created {len(actors)} actors")
    return actors

def create_movie_actor_relationships(movies, actors):
    """Create correct relationships between movies and actors"""
    movie_actor_mapping = [
        ( 0, [ 0,  1]),  # Shawshank: Morgan Freeman, Tim Robbins
        ( 1, [ 2,  3]),  # Godfather: Marlon Brando, Al Pacino
        ( 2, [ 4,  5]),  # Dark Knight: Christian Bale, Heath Ledger
        ( 3, [ 6,  7]),  # Pulp Fiction: John Travolta, Samuel L. Jackson
        ( 4, [10, 11]),  # Schindler's List: Liam Neeson, Ben Kingsley
        ( 5, [ 8, 12]),  # Inception: Leonardo DiCaprio, Joseph Gordon-Levitt
        ( 6, [ 9, 13]),  # Forrest Gump: Tom Hanks, Robin Wright
        ( 7, [14, 15]),  # The Matrix: Keanu Reeves, Laurence Fishburne
        ( 8, [16, 17]),  # Goodfellas: Robert De Niro, Ray Liotta
        ( 9, [18, 19]),  # Interstellar: Matthew McConaughey, Anne Hathaway
        (10, [20, 21]),  # Fight Club: Brad Pitt, Edward Norton
        (11, [22, 23]),  # LOTR: Fellowship: Elijah Wood, Ian McKellen
        (12, [24, 25]),  # The Social Network: Jesse Eisenberg, Andrew Garfield
        (13, [26, 27]),  # Silence of the Lambs: Jodie Foster, Anthony Hopkins
        (14, [28, 29]),  # Empire Strikes Back: Mark Hamill, Harrison Ford
    ]

    relationships = []
    for movie_idx, actor_indices in movie_actor_mapping:
        for order, actor_idx in enumerate(actor_indices):
            rel = MovieActor(
                movie_id=movies[movie_idx].id,
                actor_id=actors[actor_idx].id,
                order_index=order
            )
            relationships.append(rel)
            db.session.add(rel)

    db.session.commit()
    print(f"Created {len(relationships)} movie-actor relationships")
    return relationships

def create_sample_users():
    """Create sample users for testing"""
    users_data = [
        # US Users (8 users)
        {'email': 'john.doe@example.com',     'full_name': 'John Doe',       'country': 'US', 'city': 'New York',     'auth_provider': 'local'},
        {'email': 'sarah.wilson@example.com', 'full_name': 'Sarah Wilson',   'country': 'US', 'city': 'Los Angeles',  'auth_provider': 'local'},
        {'email': 'mike.johnson@example.com', 'full_name': 'Mike Johnson',   'country': 'US', 'city': 'Chicago',      'auth_provider': 'local'},
        {'email': 'lisa.brown@example.com',   'full_name': 'Lisa Brown',     'country': 'US', 'city': 'Miami',        'auth_provider': 'local'},
        {'email': 'david.miller@example.com', 'full_name': 'David Miller',   'country': 'US', 'city': 'Seattle',      'auth_provider': 'local'},
        {'email': 'emma.davis@example.com',   'full_name': 'Emma Davis',     'country': 'US', 'city': 'Boston',       'auth_provider': 'local'},
        {'email': 'ryan.garcia@example.com',  'full_name': 'Ryan Garcia',    'country': 'US', 'city': 'Phoenix',      'auth_provider': 'local'},
        {'email': 'sophia.martinez@example.com', 'full_name': 'Sophia Martinez', 'country': 'US', 'city': 'Denver',   'auth_provider': 'local'},
        
        # UK Users (6 users)  
        {'email': 'jane.smith@example.com',   'full_name': 'Jane Smith',     'country': 'UK', 'city': 'London',       'auth_provider': 'local'},
        {'email': 'james.thompson@example.com', 'full_name': 'James Thompson', 'country': 'UK', 'city': 'Manchester',   'auth_provider': 'local'},
        {'email': 'olivia.white@example.com', 'full_name': 'Olivia White',   'country': 'UK', 'city': 'Birmingham',   'auth_provider': 'local'},
        {'email': 'william.jones@example.com', 'full_name': 'William Jones',  'country': 'UK', 'city': 'Liverpool',    'auth_provider': 'local'},
        {'email': 'charlotte.evans@example.com', 'full_name': 'Charlotte Evans', 'country': 'UK', 'city': 'Edinburgh',    'auth_provider': 'local'},
        {'email': 'george.taylor@example.com', 'full_name': 'George Taylor',  'country': 'UK', 'city': 'Bristol',      'auth_provider': 'local'},
        
        # Turkey Users (5 users)
        {'email': 'ahmed.hassan@example.com', 'full_name': 'Ahmed Hassan',   'country': 'TR', 'city': 'Istanbul',     'auth_provider': 'local'},
        {'email': 'fatma.yilmaz@example.com', 'full_name': 'Fatma Yılmaz',   'country': 'TR', 'city': 'Ankara',       'auth_provider': 'local'},
        {'email': 'mehmet.demir@example.com', 'full_name': 'Mehmet Demir',   'country': 'TR', 'city': 'İzmir',        'auth_provider': 'local'},
        {'email': 'ayse.kaya@example.com',    'full_name': 'Ayşe Kaya',      'country': 'TR', 'city': 'Bursa',        'auth_provider': 'local'},
        {'email': 'ozan.celik@example.com',   'full_name': 'Ozan Çelik',     'country': 'TR', 'city': 'Antalya',      'auth_provider': 'local'},
        
        # Germany Users (4 users)
        {'email': 'hans.mueller@example.com', 'full_name': 'Hans Müller',    'country': 'DE', 'city': 'Berlin',       'auth_provider': 'local'},
        {'email': 'anna.schmidt@example.com', 'full_name': 'Anna Schmidt',   'country': 'DE', 'city': 'Munich',       'auth_provider': 'local'},
        {'email': 'klaus.weber@example.com',  'full_name': 'Klaus Weber',    'country': 'DE', 'city': 'Hamburg',      'auth_provider': 'local'},
        {'email': 'petra.wagner@example.com', 'full_name': 'Petra Wagner',   'country': 'DE', 'city': 'Frankfurt',    'auth_provider': 'local'},
        
        # France Users (4 users)
        {'email': 'pierre.dubois@example.com', 'full_name': 'Pierre Dubois',  'country': 'FR', 'city': 'Paris',        'auth_provider': 'local'},
        {'email': 'marie.martin@example.com',  'full_name': 'Marie Martin',   'country': 'FR', 'city': 'Lyon',         'auth_provider': 'local'},
        {'email': 'jean.bernard@example.com',  'full_name': 'Jean Bernard',   'country': 'FR', 'city': 'Marseille',    'auth_provider': 'local'},
        {'email': 'claire.rousseau@example.com', 'full_name': 'Claire Rousseau', 'country': 'FR', 'city': 'Toulouse',     'auth_provider': 'local'},
        
        # Canada Users (3 users)
        {'email': 'alex.taylor@example.com',   'full_name': 'Alex Taylor',    'country': 'CA', 'city': 'Toronto',      'auth_provider': 'local'},
        {'email': 'sophie.martin@example.com', 'full_name': 'Sophie Martin',  'country': 'CA', 'city': 'Vancouver',    'auth_provider': 'local'},
        {'email': 'lucas.brown@example.com',   'full_name': 'Lucas Brown',    'country': 'CA', 'city': 'Montreal',     'auth_provider': 'local'},
    ]

    users = []
    for u in users_data:
        user = User(**u)
        user.set_password('TestPass123!')
        users.append(user)
        db.session.add(user)

    db.session.commit()
    print(f"Created {len(users)} users")
    return users

def create_sample_ratings(movies, users):
    """Create sample ratings and comments with realistic distribution"""
    import random
    
    # More realistic rating distribution weights
    # Weights for ratings 1-10 (1=worst, 10=best)
    rating_weights = [1, 2, 3, 8, 12, 15, 20, 18, 12, 9]  # Most ratings are 6-8
    
    # More varied comments
    comments_positive = [
        "Absolutely brilliant! A masterpiece of cinema.",
        "Outstanding performances and direction.",
        "One of the best films I've ever seen.",
        "Incredible storytelling and cinematography.",
        "A must-watch movie for everyone.",
        "Fantastic acting and compelling plot.",
        "Beautifully crafted and emotionally powerful.",
        "Exceeded all my expectations.",
        "Phenomenal movie, highly recommended!",
        "A timeless classic that never gets old."
    ]
    
    comments_neutral = [
        "Good movie, worth watching.",
        "Decent film with some great moments.",
        "Solid entertainment, well made.",
        "Pretty good, though not perfect.",
        "Enjoyable watch overall.",
        "Good acting and production quality.",
        "Well done but didn't blow me away.",
        "Solid movie, met my expectations."
    ]
    
    comments_negative = [
        "Not my cup of tea, didn't enjoy it.",
        "Overhyped, disappointed with the result.",
        "Could have been much better.",
        "Boring and predictable plot.",
        "Not worth the time invested.",
        "Expected more from this film.",
        "Didn't live up to the hype."
    ]
    
    ratings = []
    for user in users:
        # Each user rates 8-12 movies (more data for better distributions)
        num_ratings = random.randint(8, 12)
        for movie in random.sample(movies, min(num_ratings, len(movies))):
            # Use weighted random choice for more realistic rating distribution
            rating_value = random.choices(range(1, 11), weights=rating_weights)[0]
            
            # Choose comment based on rating
            comment = None
            if random.random() < 0.7:  # 70% chance of having a comment
                if rating_value >= 8:
                    comment = random.choice(comments_positive)
                elif rating_value >= 6:
                    comment = random.choice(comments_neutral)
                else:
                    comment = random.choice(comments_negative)
            
            rating = Rating(
                movie_id=movie.id,
                user_id=user.id,
                rating=rating_value,
                comment=comment,
                voter_country=user.country
            )
            ratings.append(rating)
            db.session.add(rating)

    db.session.commit()
    print(f"Created {len(ratings)} ratings")
    return ratings

def update_movie_scores(movies):
    """Update cached movie scores based on ratings"""
    from app.services.movie_service import MovieService
    svc = MovieService()
    for m in movies:
        svc.update_movie_rating(str(m.id))
    print("Updated movie scores")

def create_popularity_snapshots(movies):
    """Create initial popularity snapshots"""
    from app.services.movie_service import MovieService
    svc = MovieService()
    if svc.update_popularity_snapshots():
        print("Created popularity snapshots")
    else:
        print("Failed to create popularity snapshots")

def seed_database():
    """Seeds the database with sample data."""
    print("Starting database seeding...")

    # Clear existing data in the correct order
    print("Clearing existing data...")
    db.session.query(MovieCategory).delete()
    db.session.query(Category).delete()
    db.session.query(PopularitySnapshot).delete()
    db.session.query(Rating).delete()
    db.session.query(Watchlist).delete()
    db.session.query(MovieActor).delete()
    db.session.query(Movie).delete()
    db.session.query(Actor).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    movies = create_sample_movies()
    actors = create_sample_actors()
    categories = create_sample_categories()
    create_movie_category_relationships(movies, categories)
    create_movie_actor_relationships(movies, actors)
    users = create_sample_users()
    create_sample_ratings(movies, users)
    update_movie_scores(movies)
    create_popularity_snapshots(movies)
    print("Database seeding completed successfully!")

def main():
    """Main entry point for script."""
    app = create_app()
    with app.app_context():
        seed_database()

if __name__ == '__main__':
    main()
