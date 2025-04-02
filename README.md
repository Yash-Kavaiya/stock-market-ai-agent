# Deploying to Google Cloud Run

This guide walks you through deploying your Shopping Agent application to Google Cloud Run.

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. Docker installed on your local machine
3. Google Cloud project created
4. Billing enabled on your Google Cloud project
5. Required APIs enabled:
   - Cloud Run API
   - Container Registry API
   - Cloud Build API

## Step 1: Add Gunicorn to requirements.txt

Ensure `gunicorn` is in your requirements.txt file as it's needed for production deployment:

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

## Step 2: Setup Environment Variables

Create a `.env` file with your API keys:

```bash
GOOGLE_API_KEY=your_google_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

## Step 3: Build and Test Locally

```bash
# Build the Docker image
docker build -t shopping-agent .

# Run the container locally
docker run -p 8080:8080 --env-file .env shopping-agent
```

Visit http://localhost:8080 to test your application.

## Step 4: Deploy to Google Cloud Run

### Authenticate with Google Cloud

```bash
gcloud auth login
```

### Configure Docker to use Google Container Registry

```bash
gcloud auth configure-docker
```

### Set your Google Cloud project ID

```bash
gcloud config set project YOUR_PROJECT_ID
```

### Build and push the Docker image to Google Container Registry

```bash
# Build and tag the image
docker build -t gcr.io/YOUR_PROJECT_ID/shopping-agent .

# Push the image to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/shopping-agent
```

### Deploy to Cloud Run

```bash
gcloud run deploy shopping-agent \
  --image gcr.io/YOUR_PROJECT_ID/shopping-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=your_google_api_key,FIRECRAWL_API_KEY=your_firecrawl_api_key,SECRET_KEY=your_secret_key"
```

Replace `YOUR_PROJECT_ID` with your Google Cloud project ID and provide the actual values for your environment variables.

## Step 5: Access Your Deployed Application

After the deployment completes, the command will output a URL for your deployed application, which looks like:

```
https://shopping-agent-xxxx-xx.a.run.app
```

Visit this URL to access your application.

## Continuous Deployment (Optional)

To set up continuous deployment using Cloud Build:

1. Connect your GitHub repository to Cloud Build
2. Create a `cloudbuild.yaml` file in your repository
3. Configure triggers for automatic builds

For more information, see [Cloud Build documentation](https://cloud.google.com/build/docs/deploying-builds/deploy-cloud-run).

## Monitoring and Logging

Access logs and monitoring from the Google Cloud Console:
- Logs: Cloud Run > shopping-agent > Logs
- Metrics: Cloud Run > shopping-agent > Metrics

## Troubleshooting

If you encounter issues:

1. Check container logs in the Cloud Run console
2. Verify environment variables are correctly set
3. Make sure all required APIs are enabled
4. Ensure your service account has proper permissions
