# Daily update emails for my wife on how the job search is going

2024-09-30 - I check my phone at ~8:26AM while getting my kids ready for school and I see an impromptu meeting from my VP titled 'Important Business Update.' Never a fun thing to see. 

Since then I have been working towards finding a new job in DS, and as the sole income of my household my wife is frequently curious what updates there are to be had. It's hard to recall them all at once at the end of the day. So, the purpose of the scripts here are to execute following steps: 

1. Using the Google API available for sheets and calendar pull 3 things: 
    - Job application updates - this is any application that had an update today or was created today. This way she knows the status of all things in the pipeline and can ask questions about specific jobs if she is curious. 
    - Tomorrow's calendar - sends times and names of all events scheduled for tomorrow 
    - Today's notes - description of what happened today and a summary of the meetings/interviews that I had. 
1. Condense this into an HTML object that is ultimately the email body. 
1. Send the email to my wife and myself. 

I have successfully micromanaged myself at the request of nobody. 