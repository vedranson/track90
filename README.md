# EU Stay Tracking App

The EU Stay Tracking App is a web and mobile application designed to help users keep track of their stays in the European Union and ensure compliance with the 90-day limit within a 180-day period. Users can conveniently select and monitor their stay dates, making it easier to plan future visits to EU countries.

## Features

- **Date Range Selection**: Easily select the start and end dates of your stays within the EU.
- **Stay History**: Maintain a record of past and future stays in the EU for reference.
- **Calendar View**: Visualize your stay dates on an interactive calendar interface.
- **Authentication**: Secure user authentication to protect your data.
- **User-Friendly Interface**: An intuitive and responsive user interface for both web and mobile devices.

## Tech Stack

- **Backend**: Built with Python using the FastAPI framework, ensuring robust API functionality.
- **Frontend**: Developed using React for dynamic and interactive user experiences.
- **Database**: Store user data and stay history using PostgreSQL.
- **Deployment**: Hosted on [to be deterimned].

## Getting Started

1. Clone the repository: `git clone [repository URL]`
2. Install dependencies:
   - Backend: `cd backend && pip install -r requirements.txt`
   - Frontend: `cd frontend && npm install`
3. Configure the database settings in the backend (e.g., PostgreSQL).
4. Start the backend server: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
5. Start the frontend development server: `cd frontend && npm start`
6. Access the app in your web browser at `http://localhost:3000`.

## Contributing

We welcome contributions to improve the EU Stay Tracking App. Please fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss the proposed changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions or feedback, please contact vedranson@gmail.com.
