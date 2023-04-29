# Development of Secure Communication Methods in Smart Traffic Systems

This project is developed by Shashank Agarwal, Manu Singh Bist, Utsav Agrawal of Jaypee Institute of Information Technology submitted as our Major Project-2 in partial fulfillment of the Degree of Bachelor of Technology In Information Technology.

## Running the Project
1. Download/git clone the project
2. Install Python and Django, if not already
3. Run ```python manage.py runserver```. If this doesn't work, try using ```python3``` instead of ```python```.

## Useful commands:
1. After making changes in models.py file, migrate the changes to the sqlite DB via:
<br> ```python manage.py makemigrations```
<br> ```python manage.py migrate```

2. To delete all entries in the DB:
<br> ```python manage.py flush```
<br> Or, to manually pick and add/delete entries, visit:
<br> ```127.0.0.1:8000/admin```

3. If there is an existing connection on the port 8000, on Windows use the task manager to kill the process. On mac, use:
<br> ```sudo lsof -i :8000```
<br> ```kill -9 <PROCESS_NUMBER>```
