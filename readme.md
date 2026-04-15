## Context
### Trips validation platform

#### Project Overview
This is a conceptual trip validation platform. 

Our clients are companies with large fleet of vehicles and drivers. Company hierarchy could spread into different geographical region viz. NorthAmerica, South America, Europe, Australia, APAC.
Drivers in the company would be working on shifts in the location they're assigned to. At the end of their shift, their trip would be sent to the server for processing.

When we cross validated trip data, driver's work-hours and incidents, we've found data for some drivers doesn't any sense. 
We are almost certain that drivers have been using emulator to fabricate trips and maintain consistently a low risk score.

This conceptual platform will allow human moderators to review trip and flag fraudulent ones.

Below a high level of how it will be handled.

- Drivers drive in a location they're assigned to.
- Trip data will attach location it belongs to
- Human reviewers are assigned to each location
- Reviewers will claim to review a suspicious trip
- A trip under review will be invisible to other reviewers, to not waste human resource on a same trip
- The reviewer can flag trip fraudulent
- After a timeout of 15 minutes in review, unflagged trip will be visible to all reviewers again
- Any trip will go stale after 48 hours

#### High Level Design

##### Components 

1. Trip Simulator Service
   - Details in trip_simulator/readme.md
2. Trip Ingestion Service 
    - Details in trip_ingestion_service/readme.md
3. Trip Review Service (port 8010)
    - Details in trip_review_service/readme.md
    - Use http://localhost:8010
4. Moderator Interface (port 8080)
   - Use http://localhost:8080 to access the moderator interface
   - Few moderators are seeded in moderators table for testing purpose. 
   - You can use the following credentials to login to the moderator interface.
   - (10001, 'North America'), 
   - (10002, 'North America')
   - (10006, 'Europe'), 
   - (10007, 'Europe')
    
5. Database (port 33066)
    - MySQL database to store trip data and moderator data
    - user/password: root/root

6. Message Queue (port 5672 and 15672)
    - RabbitMQ to decouple the trip ingestion and trip review services
    - user/password: guest/guest

Running it 
-----------
1. clone the project using
2. run `docker compose up` in the root directory of the project
3. This will start up all the above components as separate containers
4. The Trip Review Service might fail on it's connection to the database, for the first time.
    Reason, the database container might take a bit longer to start up and be ready to accept connections.
   
5. You will have to restart container manually.
