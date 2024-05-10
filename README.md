# WeatherSubscriptionsAPI 🌦️

WeatherSubscriptionsAPI is a web application that provides an API for working with weather information and subscriptions for weather notifications for specific cities. Users can register, authenticate, create, and manage subscriptions for weather notifications.

## Features

🔒 **Registration and Authentication**: Users can register for the system and log into their accounts using email and password authentication.

🌍 **Weather Information Retrieval**: The API provides the ability to retrieve current weather information for various cities.

💌 **Subscription to Weather Notifications**: Users can subscribe to weather notifications for selected cities and customize the frequency of receiving notifications.

🔧 **Subscription Management**: Users can view, create, edit, and delete their weather notification subscriptions.

🛡️ **Data Validation**: The API validates user-provided data and protects against incorrect requests.

🗑️ **Removal of Unused Records**: The application automatically deletes cities for which there are no active subscriptions to maintain the database in an up-to-date state.

## Technologies

🐍 **Django**: Used to create the web application and handle requests.

📡 **Django REST Framework**: Provides the creation of RESTful API for client request processing.

📚 **drf-spectacular**: Used for automatic generation of API documentation based on OpenAPI (Swagger) specifications.

🗃️ **PostgreSQL Database**: Used to store information about users, cities, and subscriptions.

🚀 **Python**: The programming language used to develop the web application.

🧪 **pytest**: Used for testing the functionality of the application.

## Installation

To run the WeatherSubscriptionsAPI locally, follow these steps:

1. Clone the repository: `git clone https://github.com/Radchanka/WeatherSubscriptionsAPI.git`
2. Navigate to the project directory: `cd WeatherSubscriptionsAPI`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up the PostgreSQL database and configure the database settings in `settings.py`.
5. Apply migrations: `python manage.py migrate`
6. Run the development server: `python manage.py runserver`

## Usage

Once the server is running, you can access the API endpoints using tools like `curl` or through API testing tools like Postman.

## Documentation

The API documentation is automatically generated using drf-spectacular and can be accessed at [API Documentation](http://localhost:8000/api/schema/swagger-ui/).

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About

Developed by: Uladzimir Radchanka (URadchanka@gmail.com)
