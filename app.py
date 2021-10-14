import os
from models import setup_db, Actor, Movie, create_and_drop_all, setup_migrations
import datetime
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import requires_auth, AuthError


movies_or_actors_Per_Page = 10


def pagination_movie_or_actor(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * movies_or_actors_Per_Page
    end = start + movies_or_actors_Per_Page

    movies_or_actors = [movie_or_actor.format() for movie_or_actor in selection]
    current_movies_or_actors = movies_or_actors[start:end]
    return current_movies_or_actors


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             "Content-Tpe,Authorization,true")
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,PATCH,DELETE,OPTIONS')
        return response

##--------------------------------------------------------------------------------##

                                    # MOVIES #

##--------------------------------------------------------------------------------##

   # get movies from database
    @app.route('/movies')
    @requires_auth('view:movies')
    def view_Movies(payload):

        movies = Movie.query.all()
        if movies is None:
            abort(404)
            
        total_movies = len(movies)
        current_movies = pagination_movie_or_actor(request, movies)

        return jsonify({"success": True,
                        "movies": current_movies,
                        "total_movies": total_movies
                        })



 # create a new movie 
    @app.route('/movies', methods=['POST'])
    @requires_auth('add:movies')
    def create_Movies(payload):

        data = request.get_json()

        # abort if the request body is invalid
        if not ('title' in data and 'release_date' in data and 'genre' in data):
            abort(400)

        try:
            movie = Movie(
                title=data.get('title'),
                release_date=datetime.date.fromisoformat(data.get('release_date')),
                genre=data.get("genre")
                )
            # add the new  to the database
            movie.insert()
            # get the movies ordered by id
            movies = Movie.query.order_by(Movie.id).all()
            # total number of movies in the database after insert the new movie
            total_movies = len(movies)
            # paginate the movies
            current_movies = pagination_movie_or_actor(request, movies)
            return jsonify({
                "success": True,
                "created": movie.title,
                "movies": current_movies,
                "total_movies": total_movies,
            })

        except:
            abort(422)
            
            
            
     #edit the movie by id 
    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('Edit:movies')
    def edit_movies(payload, id):
      
        try:
            data = request.get_json()
            if data is None:
                abort(400)
                
            movie = Movie.query.get(id)
            
            if movie is None:
                abort(404)
                
            if 'title' in data:
                movie.title = data.get('title')
            if 'release_date' in data:
                movie.release_date = data.get('release_date')
            if 'genre' in data:
                movie.genre = data.get('genre')
                
            movie.update()
            
            return jsonify({
                "success": True,
                "movie": movie.format()
            })
        except :
             abort(422)

        
        
        
        
    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, id):
        try:
            movie = Movie.query.get(id)
            
            if movie is None:
                abort(404)
                
            movie.delete()
            
            return jsonify({
                "success": True,
                "deleted": movie.title
            })
        except :
          abort(402)
        
        
        
 ##--------------------------------------------------------------------------------##

                                    # Actors #

##--------------------------------------------------------------------------------##

        
        
    @app.route('/actors')
    @requires_auth('view:actors')
    def view_actors(payload):
        
        
            actors = Actor.query.all()
            
            if actors is None:
                abort(404)
                
            total_actors = len(actors)
            current_actors = pagination_movie_or_actor(request, actors)
                
            return jsonify({
                "success": True,
                "actors": current_actors,
                "total_actors": total_actors,
            })
        
        
    @app.route('/actors', methods=['POST'])
    @requires_auth('add:actors')
    def create_actor(payload):
        try:
            data = request.get_json()
            
            if 'name' not in data or 'age' not in data or 'gender' not in data:
                abort(400)
                
            actor = Actor(name=data.get("name"),
                          age=data.get("age"),
                          gender=data.get("gender")
                          )
            
            actor.insert()
            
            # get the actors ordered by id
            actors = Actor.query.order_by(Actor.id).all()
            # total number of actors in the database after insert the new actor
            total_actors = len(actors)
            # paginate the actors
            current_actors = pagination_movie_or_actor(request,actors)
            return jsonify({
                "success": True,
                "created": actor.name,
                "actors": current_actors,
                "total_actors": total_actors,
            })
        except :
            abort(422)
            
            
    
    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('edit:actors')
    def modify_actor(payload, id):
        
        try:
            
            data = request.get_json()
            
            if data is None:
                abort(400)
                
            actor = Actor.query.get(id)
            
            if actor is None:
                abort(404)
                
            if 'name' in data:
                actor.name = data.get("name")
                
            if 'age' in data:
                actor.age = data.get("age")
                
            if 'gender' in data:
                actor.gender = data.get("gender")
                
            actor.update()
            
            return jsonify({
                "success": True,
                "actor": actor.format()
            })
        except :
            abort(422)     
            
            
            
            
            
            
            
            
    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=8080, debug=True)
