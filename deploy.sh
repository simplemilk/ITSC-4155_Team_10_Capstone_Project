#!/bin/bash

echo "🚀 Deploying Niner Finance to Heroku..."

git add .
git commit -m "Deploy: $(date)"
git push origin main

git push heroku main

heroku run python niner_repo/init_all_db.py

heroku open

echo "✅ Deployment complete!"