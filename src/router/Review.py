from flask.views import MethodView
from flask import jsonify, request
from src.config.settings import db
from src.models.Review import Review
from flasgger import swag_from
from src.services.AuthService import Authentication
from flask_login import login_required

class ReviewView(MethodView):
    @swag_from({
            'tags':['Reviews'],
            'summary':'Get Review data',
            'parameters':[
                {
                    'name': 'review_id',
                    'in': 'path',
                    'type': 'integer',
                    'required': False,
                    'description': 'ID of the reviews to retrieve'
                }
            ],
            'security': [{'Bearer': []}],  # Include Bearer token authentication
            'responses': {
                200:{
                    'description':'Review(s) retrived successfully',
                    'schema':{
                        'type':'object',
                        'properties':{
                            'Product Review': {
                                'type':'array',
                                'items':{
                                    'type':'object',
                                    'properties':{
                                        'id': {
                                            'type': 'integer',
                                            'example': 1
                                        },
                                        'product': {
                                            'type':'string',
                                            'example': 'laptop'
                                        },
                                        'rating': {
                                            'type': 'integer',
                                            'example': 4.5
                                        },
                                        'description':{
                                            'type':'string',
                                            'example':'Good performance for mobile and code'
                                        }
                                    }
                                    
                                }
                            }
                        }
                    }
                },
                404:{
                    'description': 'Product review not found',
                    'schema':{
                        'type':'object',
                        'properties':{
                            'error':{
                                'type': 'string',
                                'example': 'Review not found'
                            }
                        }
                    }
                }
            }

        })
    @login_required
    @Authentication.token_required
    @Authentication.auth_role('admin')  # Only admin can access this
    def get(self, current_user, review_id=None):
        review_fields = ['id', 'product', 'rating', 'description']

        if review_id is None:
            reviews = Review.query.filter_by(is_deleted = False).all()
            print(f"Review query result: {reviews}")
            if not reviews:
                return jsonify({"error": "Review not found"}), 404
            
            results = [{field: getattr(review, field) for field in review_fields} for review in reviews]
            return jsonify({"Product List": results}), 200
        else: 
            review = Review.query.filter(Review.id == review_id, Review.is_deleted == False).first()
            
            if not review:
                return jsonify({"error": "Product review not Found"}), 404

            results = {field: getattr(review, field) for field in review_fields}
            return jsonify({"Product Detail": results})

    @swag_from({
            'tags':['Reviews'],
            'summary':'Create Review data',
            'parameters':[
                {
                    'name': 'body',
                    'in': 'body',
                    'required': True,
                    'schema':{
                        'type':'object',
                        'properties':{
                            'product':{
                                'type': 'string',
                                'description': 'Name of the product',
                                'example': 'Fan'
                            },
                            'rating':{
                                'type':'integer',
                                'description': 'rating of the product',
                                'example': 4.5
                            },
                            'description':{
                                'type':'string',
                                'description': 'description of the product',
                                'example': 'Good to cooling the environment'
                            },
                        },
                        'required': ['product', 'rating', 'description']  # Required fields
                    }
                }
            ],
            'security': [{'Bearer': []}],  # Include Bearer token authentication
            'responses': {
                201: {
                    'description': 'Product Review created successfully',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {
                                'type': 'string',
                                'example': 'Product Review created successfully'
                            },
                            'Product Review': {
                                'type': 'object',
                                'properties': {
                                    'product': {
                                        'type': 'string',
                                        'example': 'Fan'
                                    },
                                    'rating': {
                                        'type': 'integer',
                                        'example': 4.5
                                    },
                                    'description': {
                                        'type': 'string',
                                        'example': 'Good to cool the environment'
                                    }
                                }
                            }
                        }
                    }   
                },
                400: {
                    'description': 'Invalid data input',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {
                                'type': 'string',
                                'example': 'Invalid data input'
                            }
                        }
                    }
                }
            }
    })
    @login_required
    @Authentication.token_required
    @Authentication.auth_role('admin')  # Only admin can access this
    def post(self, current_user):
        # Get data from request body (assumed to be in JSON format)
        data = request.get_json()
        review_fields = ['id', 'product', 'rating', 'description']
        
        required_fields = ['product', 'rating', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": "Invalid data"}), 400
        
        new_review = Review()
        for field in review_fields:
            setattr(new_review, field, data.get(field, None))
        
        db.session.add(new_review)
        db.session.commit()
        db.session.close_all

        review_data = {field: getattr(new_review, field) for field in review_fields}

        # Respond with the created review and 201 status
        return jsonify({
            "message": "Review created", 
            "review": review_data
            }), 201


    @swag_from({
            'tags':['Reviews'],
            'summary':'Update Review data',
            'parameters':[
                {
                    'name': 'review_id',
                    'in': 'path',
                    'type': 'integer',
                    'required': True,
                    'description': 'ID of the product review to update'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'required': True,
                    'schema':{
                        'type':'object',
                        'properties':{
                            'product':{
                                'type': 'string',
                                'description': 'Name of the product',
                                'example': 'Fan'
                            },
                            'rating':{
                                'type':'integer',
                                'description': 'rating of the product',
                                'example': 4.5
                            },
                            'description':{
                                'type':'string',
                                'description': 'description of the product',
                                'example': 'Good to cooling the environment'
                            },
                        }
                    }
                }
            ],
            'security': [{'Bearer': []}],  # Include Bearer token authentication
            'responses': {
                200: {
                    'description': 'Product Review updated successfully',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {
                                'type': 'string',
                                'example': 'Product Review updated successfully'
                            },
                            'Product Review': {
                                'type': 'object',
                                'properties': {
                                    'product': {
                                        'type': 'string',
                                        'example': 'Fan'
                                    },
                                    'rating': {
                                        'type': 'integer',
                                        'example': 4.5
                                    },
                                    'description': {
                                        'type': 'string',
                                        'example': 'Good to cool the environment'
                                    }
                                }
                            }
                        }
                    }   
                },
                404: {
                    'description': 'Review Not Found',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {
                                'type': 'string',
                                'example': 'Review Not Found'
                            }
                        }
                    }
                }
            }
    })
    @login_required
    @Authentication.token_required
    @Authentication.auth_role('admin')  # Only admin can access this
    def put(self, current_user, review_id):
        review = Review.query.filter(Review.id == review_id, Review.is_deleted == False).first()

        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        review_fields = ['id', 'product', 'rating', 'description']
        
        for field in review_fields:
            value = request.json.get(field)
            if value:
                setattr(review, field, value)
        
        db.session.commit()
        review_data = {field: getattr(review, field) for field in review_fields}

        return jsonify({
            "message": "Product review updated succesfully",
            "review": review_data
        })

    @swag_from({
            'tags':['Reviews'],
            'summary':'Delete Review data',
            'parameters': [
                {
                    'name': 'review_id',
                    'in': 'path',
                    'type': 'integer',
                    'required': True,
                    'description': 'ID of the product review to delete'
                }
            ],
            'security': [{'Bearer': []}],  # Include Bearer token authentication
            'responses':{
                200: {
                    'description': 'Review deleted successfully',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {
                                'type': 'string',
                                'example': 'Review deleted successfully'
                            }
                        }
                    }
                },
                404: {
                    'description': 'Animal not found',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {
                                'type': 'string',
                                'example': 'Animal not found'
                            }
                        }
                    }
                }
            }
    })
    @login_required
    @Authentication.token_required
    @Authentication.auth_role('admin')  # Only admin can access this
    def delete(self, current_user, review_id):
        review = Review.query.filter(Review.id == review_id, Review.is_deleted == False).first()
        # print(f"query result: {review}") # debugging
        if review:
            review.is_deleted = True
            db.session.commit()
            return jsonify({"message": "Review deleted successfully"}), 200
        
        else:
            return jsonify({"message": "Review not Found"}), 404


