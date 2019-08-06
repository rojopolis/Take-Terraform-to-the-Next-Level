# API Artifacts

There are two artifacts produced by the API Gateway:

1. Javascript SDK.  This exports a .zip file of an SDK for the gateway stage created.  The sdk will be found at the path: https://s3.amazonaws.com/api.my90.com/my90-api-<branch_name>.zip and is publically accessible.
2. Swagger document with Postman extensions.  You can import this directly into postman by gibing it the URL: https://s3.amazonaws.com/api.my90.com/my90-api-<branch_name>.json