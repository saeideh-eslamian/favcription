# favcription

**Favcription** is a Django-based application designed to help you focus on specific content from YouTube channels you're interested in. For instance, if you follow several English teachers on YouTube and want to view only their videos about "speaking," Favcription allows you to group these channels and filter their content based on specific keywords. This way, you can save time by only viewing the content that matters to you.

## Features
- **Group Channels:** Create groups of YouTube channels you follow.
- **Keyword Filtering:** Assign up to three keywords to each group to filter content. Only videos that match these keywords will be displayed.
- **Google Account Integration:** Easily connect your YouTube account using your Google account.
- **YouTube API Integration:** Retrieve and manage your YouTube channels directly from your account.


## Installation
**1- Clone the repository:**
```bach
git clone https://github.com/your-username/favcription.git
cd favcription
```
**2- Set up environment variables:**
Create a **.env** file in the project root directory add the following environment-specific settings:
```bach
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=yourdatabase
DB_USER=username
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432

# Database configuration for Docker environment
DATABASE_URL=postgres://username:password@db/yourdatabase
```
## 3. Create a Google Cloud account and download the client_secret.json file:
Follow this guide to create your Google Cloud account and obtain the client_secret.json file: [How to Get Client ID and Client Secret in Google Cloud Platform](https://www.cloudsciencelabs.com/blog/how-to-get-client-id-and-client-secret-in-google-cloud-platform).
Place the downloaded client_secret.json file in the root directory of your project.

**Hint:** add this url in your Authorized redirect URIs at cloud 
```bach
http://localhost:8000/api/oauth2callback/
```
### Installation Steps with virtual environment
**4- Create and activate a virtual environment:**
```bach
python -m venv venv
source venv/bin/activate
```
**5- Install the required dependencies:**
```bach
pip install -r requirements.txt
```

**6- Clone the repository:**
```bach
git clone https://github.com/your-username/favcription.git
cd favcription
```

**7- Apply database migrations and run the server**
```bach
python manage.py migrate
python manage.py runserver
```

### Build and start the Docker containers:
**4- Build and start the Docker containers:**
```bach
docker-compose up --build
```
**5- Run the development server:**
create account in the [ngrock](https://ngrok.com/) and add your url in your Authorized redirect URIs

**Hint:** add this url in your Authorized redirect URIs at cloud 
```bach
http://<your-random-ip>.ngrok-free.app/api/oauth2callback/
```
and than in another terminal run this command
```bach
ngrok http 8000
```

**6- start or Stop the Docker containers:**
```bach
docker-compose up
docker-compose down
```

## Contributing
Contributions are welcome! Please fork this repository and submit a pull request for any enhancements or bug fixes.

## Contact
If you have any questions or feedback, feel free to reach out.