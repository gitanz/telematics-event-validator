Trip events simulator

   - This is responsible to send out mock trips every 500ms
   - Implementation
     - A Trip will have following structured information
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
     - This is going to be a basic Python CLI app, scheduled to run every 500ms as a cron job 
     - The app will fabricate a random trip
     - The app will POST the trip onto a webhook exposed (POST /v1/trips) by Trip Event Consumer
     - The response expected will be `201 Created`
      