# Create an Observer Service 
Write the service in Python
This service should be able to analyze a REST API service and endpoint. 

@app.route('/analyze', methods=['GET','POST'])
@app.route('/version')


Initial implementation would  grade a REST Service with a score between 1 and 100
The score should be based upon the following : 
  - Golden Signals : Response Time, Throughput, Error Rate and Compute Density
  - High Load vs Low Load.  High Load would be greater than 1000 Requests per Hour
  - Fast vs Slow Response Time.  Avearge Response Time Greater than 2000 milliseconds 

It should compute the score for  every hour, day, week, month year,  Hour of the Day and Day of the Week.


Create a new __version__.py file 

```
__version__ = "1.0.0"

If you want to reference this version in your observer service or update the version number, let me know!
