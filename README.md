
## Version 2 - REST API

Built a REST API using Python and FastAPI.

### Features
- Retrieve transactions using GET
- Add income and expenses using POST
- Update transactions using PUT
- Delete transactions using DELETE
- Calculate current balance
- Validate transaction amounts
- Handle invalid requests using HTTP errors
- Save transactions using JSON

### Technologies
- Python
- FastAPI
- Pydantic
- JSON

### Run the API

Install dependencies:

    python3 -m pip install "fastapi[standard]"

Start the server:

    fastapi dev api.py

Open http://127.0.0.1:8000/docs to test the API.
