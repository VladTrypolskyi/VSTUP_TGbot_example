# Vstup helper bot
**Vstup helper bot it is a simple telegram bot that helps applicants calculate their chances of getting into a speciality or find out where they can get into a certain field of study**

## Setting the bot up
1. Git clone the [bot](https://github.com/DrHohol/Internship-tasks.git)
2. Create file config.json and set your API-key for telegram bot </br>
![Configure apikey](https://i.ibb.co/FgJDjKn/Pasted-image-20220115201933.png)
3. Create Postgres database called vstup_db or change it's name in db_map.py, alembic.ini and dockerfile (If you are using docker) </br>
  3.1 Change start link for university in parser (Default KHPI)
4. Start db_map.py and parser.py
5. Build docker container 
	`docker build -t vstup_bot .`
6. Run docker container
	`docker run vstup_bot`
	
## Usage
- **Add or edit ZNO grades** </br>
![alt text](https://i.ibb.co/Ps2rMw0/Pasted-image-20220115202851.png)
- **Check ability to get into university**
	- **For 1 speciality** </br>
	![Choose only 1 speciality](https://i.ibb.co/ZfQscGS/Pasted-image-20220115203430.png)
	- **For field of knowledge** </br>
	![](https://i.ibb.co/YPcNL6W/Pasted-image-20220115203558.png)
