# Django + Vue 3 Full Stack Workspace

This project contains a complete development workspace with a Django REST Framework backend and a Vue 3 frontend, containerized with Docker.

## Project Structure

- **backend/**: Django project with DRF, PostgreSQL configuration, and custom User model.
- **frontend/**: Vue 3 application initialized with Vite, using Pinia for state management and Axios for API calls.
- **docker-compose.yml**: Orchestration for Backend, Frontend, and PostgreSQL database.

## Prerequisites

- Docker and Docker Compose installed.

## Getting Started

1. **Start the containers**:

    ```bash
    docker-compose up --build
    ```

    This will start:
    - Backend API at <http://localhost:8000/api/>
    - Frontend Application at <http://localhost:5173/>
    - PostgreSQL Database (port 5432)

2. **Initial Setup (First Run Only)**:
    Open a new terminal and run the following commands to set up the database and create a superuser:

    ```bash
    # Run database migrations
    docker-compose exec backend python manage.py migrate

    # Create a superuser for the Admin interface
    docker-compose exec backend python manage.py createsuperuser
    ```

## Development

- **Backend**:
  - The `backend` directory is mounted as a volume, so changes to Python files will auto-reload the server.
  - Access the Django Admin at <http://localhost:8000/admin/>.
  - API endpoints are available at <http://localhost:8000/api/>.

- **Frontend**:
  - The `frontend` directory is mounted, enabling Hot Module Replacement (HMR) via Vite.
  - Edit files in `frontend/src` to see changes immediately.

## Testing

- **Backend Tests**:

    ```bash
    docker-compose exec backend python manage.py test
    ```

## Troubleshooting

- **Node/Rolldown Errors**: If you encounter errors related to `rolldown` or node modules in the frontend, try clearing the container's `node_modules`:

    ```bash
    docker-compose exec frontend sh -c "rm -rf node_modules package-lock.json && npm install"
    docker-compose restart frontend
    ```
