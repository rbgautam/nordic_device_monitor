# Firebase-write-python-script-in-heroku
### This is a method to write data to FireStore Db at predtermined intervals after call api method.

### USE Case: The job scheduled in here is to call Nordic Cloud API every 30 seconds for data and save the data into Firestore document.

Steps to push local git repo to heroku remote and start the application:

- Create a local git repo 

- Use the following commands to deploy and start application:
```
1.heroku login

2.heroku create <name_app>  #(create a new empty application on Heroku. If you run this command from your app’s root directory,
the empty Heroku Git repository is automatically set as a remote for your local repository.)

3.git remote -v   #(to view the remote heroku app)

4.git push heroku master  #(deploying the code)


#To start the worker process :
5.heroku ps:scale worker=1 --app firebase-heroku-flutter

#To view the logs
6.heroku logs --tail --app <app_name>

#Later when we need to kill the worker process : 
7.heroku scale worker=0 --app firebase-heroku-flutter



```
