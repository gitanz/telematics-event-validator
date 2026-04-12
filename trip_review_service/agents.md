- This will be responsible to allow human moderators to review trip and flag fraudulent ones.
    - Implementation
      - This is going to be a FastAPI app
  
    - Moderator Login
      - Moderators are seeded in `moderators` table
      - moderators table has the following fields: moderator_id, location
      - A moderator will be able to login using their moderator_id and location
      - The login endpoint /v1/moderators/login will accept a POST request with the moderator_id and location in the request body
      - The login endpoint will validate the moderator_id and location against the moderators table and return a JWT token if the credentials are valid
      - The JWT token will be used for authentication in the subsequent endpoints for trip review
      
    - View Trips
      - Logged in Moderators will be able to list trips in their location since yesterday
      - The endpoint /v1/trips will accept a GET request and return a list of trips since yesterday.
      
    - View Trip
      - Logged in Moderators will be able to view details of an unexpired trip from their location
      - The endpoint /v1/trips/{trip_id} will accept a GET request with the trip_id as a path parameter and return the details of the trip if it is unexpired and belongs to the moderator's location
    
    - Claim Trip
      - Logged in Moderators will be able to claim a trip for review
      - The endpoint /v1/trips/{trip_id}/claim will accept a POST request