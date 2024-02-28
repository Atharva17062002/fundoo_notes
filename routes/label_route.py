from app import db, create_app
from app.models import Label
from flask import request
from flask_restx import Api, Resource, fields
from app.utils import api_handler, RedisManager
from schemas.notes_schema import NotesSchema
from app.middleware import auth_user
from sqlalchemy import text

app = create_app()

api = Api(app=app,
          version='1.0',
          title='Labels API',
          description='Notes API',
          security='apikey',
          authorizations={
              'apikey': {
                  'type': 'apiKey',
                  'in': 'header',
                  'name': 'Authorization',
                  'required': True
              }
          },
          doc='/docs',
          prefix='/api/v1')

@api.route('/labels')
class LabelsApi(Resource):
    """Resource for managing labels."""

    method_decorators = [auth_user]

    @api_handler()
    def get(self, *args, **kwargs):
        """Retrieve all labels for the authenticated user.

        Description:
        This endpoint retrieves all labels associated with the authenticated user.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing the retrieved labels with an HTTP status code.
        """

        labels = db.session.execute(
            text(
                f"SELECT * FROM label WHERE user_id = {kwargs['user_id']}"
            )
        )
        labels = list(map(dict, labels.mappings().all()))
        return {"message": "Data retrieved successfully from database", "status": 200, 'data': labels}, 200

    @api.expect(api.model('createLabel', {"name": fields.String()}))
    @api_handler()
    def post(self, *args, **kwargs):
        """Create a new label.

        Description:
        This endpoint creates a new label for the authenticated user.

        Parameter:
        None

        Return:
        dict: A dictionary containing a success message, the created label data, and an HTTP status code.
        """

        data = request.get_json()
        label = Label(**data)
        db.session.execute(
            text(f"INSERT INTO label (name, user_id) VALUES ('{label.name}',{label.user_id})"))
        db.session.commit()
        return {"message": "Label created successfully", "status": 201, "data": label.to_json()}, 201

    @api.doc(params={'label_id': "Label Id"})
    @api_handler()
    def delete(self, *args, **kwargs):
        """Delete a label.

        Description:
        This endpoint deletes a label associated with the authenticated user based on the provided label ID.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing a success message or a label not found message with an HTTP status code.
        """

        label_id = request.args.get('label_id')
        label = db.session.execute(
            text(f"SELECT * FROM label WHERE id = {label_id} and user_id = {kwargs['user_id']}"))
        if label.fetchone():
            db.session.execute(
                text(f"DELETE FROM label WHERE id = {label_id} and user_id = {kwargs['user_id']}"))
            db.session.commit()
            db.session.close()
            return {"message": "Label deleted successfully", "status": 200}, 200
        return {"message": "Label not found", "status": 404}, 404

    @api.expect(api.model('updateLabel', {"id": fields.Integer(), "name": fields.String(), "user_id": fields.Integer()}))
    @api_handler()
    def put(self, *args, **kwargs):
        """Update a label.

        Description:
        This endpoint updates a label associated with the authenticated user based on the provided label ID.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing a success message, updated label data, and an HTTP status code.
        """

        data = request.get_json()
        label = db.session.execute(
            text(f"UPDATE label SET name = '{data['name']}' WHERE id = {data['id']} and user_id = {data['user_id']}"))
        db.session.commit()

        label = db.session.execute(
            text(f"SELECT * FROM label WHERE id = {data['id']} and user_id = {data['user_id']}"))
        label = dict(label.mappings().fetchone())

        return {"message": "Label updated successfully", "status": 201, "data": label}, 201
