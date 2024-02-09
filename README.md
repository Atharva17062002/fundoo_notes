# fundoo_notes

1. Environment creation

python3 -m venv <env_name>

2. Activation command 

source env_name/bin/activate

3. Install packages

pip3 install <package_name>

4. Tracking packages in requirement file 

pip3 freeze > requirement.txt

5. Create app directory 

6. Initialise migration directory

flask db init

7. Add initial migration

flask db migrate -m "<Description>"

8. Migrate initial version to db

flask db upgrade

9. In migrations -> env.py 

Mention target metadata 
example -
    from app.models import db
    target_metadata = db.metadata

10. Create models

11. Execute step 7 and 8.

