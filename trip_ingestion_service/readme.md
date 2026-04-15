- It will be responsible to receive trip events from the Trip Simulator Service and store them in a database for further processing and review by human moderators.
   - Implementation
     - A Trip event will be structured as follows:
     ```json
       {
          "id": "uuid",
          "location": "EU",
          "country": "Ireland",
          "start": {
            "location": "cashel",
            "timestamp": "2025-03-15 13:00:00"
          },
          "stops": [
              {"location": "cashel", "timestamp": "2025-03-15 13:00:00"},
              {"location": "cahir", "timestamp": "2025-03-15 13:25:00"},
              {"location": "michelstown", "timestamp": "2025-03-15 13:45:00"},
              {"location": "fermoy", "timestamp": "2025-03-15 14:00:00"},
              {"location": "cork", "timestamp": "2025-03-15 14:15:00"}
          ],
          "end": {
            "location": "cork",
            "timestamp": "2025-03-15 14:15:00"
          }
       } 
       ```
     - This is going to be a FastAPI app
     - This exposes a POST /v1/webhook/trips endpoint to receive trip events from the Trip Simulator Service
     - The endpoint will push the trip event into a message queue (e.g. RabbitMQ, AWS SQS) 
     - A background worker will consume the message queue and store the trip event into a database (e.g. PostgreSQL, MongoDB) for further processing and review by human moderators
     - 