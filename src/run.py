from basic_api import app, db

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(load_dotenv=True, use_evalex=False)
