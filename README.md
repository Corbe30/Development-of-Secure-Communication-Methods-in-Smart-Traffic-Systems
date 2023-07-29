# Development of Secure Communication Methods in Smart Traffic Systems

This project is developed by Shashank Agarwal, Manu Singh Bist, Utsav Agrawal of Jaypee Institute of Information Technology submitted as our Major Project-2 in partial fulfillment of the Degree of Bachelor of Technology In Information Technology.

## Brief Description
The main objective of the project is to develop an efficient framework for establishment of a secure communication channel among vehicles in a shared network. This can be achieved by verifying a vehicle when, or even before, it tries to connect to another vehicle. After establishment of a secure connection, blockchain technology can be used to provide a secure, transparent, and efficient way to collect and manage critical information that can ultimately lead to improved road safety and traffic flow.<br><br>
The solution approach to the development of secure communication methods in smart traffic systems using blockchain technology involves the integration of various components such as cryptography, distributed ledger technology, and consensus mechanisms. The goal is to ensure secure and transparent communication between the various entities within the smart traffic system, such as vehicles, traffic signals, and other infrastructure.<br><br>
One key aspect of this solution approach is the use of cryptography to secure communication channels and data. This involves the use of encryption and digital signatures to ensure the authenticity and integrity of the data being transmitted. Additionally, the use of smart contracts and distributed ledger technology allows for the automation and transparency of transactions, reducing the risk of fraud and errors.

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
