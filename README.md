# With Docker easy setup

## Running

### Backend
Navigate to the `backend` directory and run 
```
docker build -t backend .
docker run -p 8000:8000 backend:latest
```

### Frontend
Navigate to the `frontend` directory and run 
```
docker build -t frontend .
docker run -p 3000:3000 frontend:latest
```

### Docker Compose (both at the same time)
From the root directory, run 
```
docker-compose up --build
```

The app will be accessible at http://localhost:3000.

## Testing

With the docker images build at the section above, we can use docker to run the unit tests.

### Backend
To run the backend tests:
```
docker run backend:latest pytest test.py
```

### Frontend
To run the frontend tests:
```
docker run frontend:latest npm test
```

# Without Docker (requires self setup)

## Running

### Backend
Navigate to the backend directory and run:
```
uvicorn app:app --reload
```

### Frontend
Navigate to the frontend directory and run:
```
npm start
```

## Testing

### Backend
If you don't have pytest installed, run:
```
pip install pytest
pip install httpx
```

To run the backend tests, navigate to the backend directory and run:
```
pytest test.py
```

### Frontend
To run the frontend tests, navigate to the frontend directory and run:
```
npm test
```
