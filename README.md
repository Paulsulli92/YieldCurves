# YieldCurves
A simple app for viewing US Treasury yield data.  It shows the yields for different bond durations for the current day an several other times up to a year ago.

I have this hosted in AWS using a S3 static website.  The website used AJAX to call an API that we host to get the data, then populates a HighCharts object with the data.  To set this up you must:
- Create a Lambda function and upload the Python script to it.  This script pulls the latest data from the Treasury's website and then returns data for the days we want to display
- Create an API Gateway with an endpoint that invokes the lambda
- Replace API_ID in chart.html with the ID of the API Gateway you created
- Create a bucket, upload the two .html files to it and enable it as a static website
