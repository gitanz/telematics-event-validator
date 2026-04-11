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
2. Trip Consumer
3.
