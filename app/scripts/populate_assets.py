import pandas as pd
from app import create_app, db
from app.models import Asset

app = create_app()

def populate_assets(csv_file):
    data = pd.read_csv(csv_file)
    with app.app_context():
        for index, row in data.iterrows():
            asset = Asset(
                asset_name=row['symbol'],
                asset_symbol=row['name']
            )
            db.session.add(asset)
        db.session.commit()
        print("Assets table repopulated successfully.")

if __name__ == "__main__":
    csv_file = 'app/scripts/seeds/assets.csv'
    populate_assets(csv_file)