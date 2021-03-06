# cantonfair-scraper

### Linux distribution
Ubuntu 17/18

### Install basic requirements
```
sudo apt-get install git nano \
  build-essential libssl-dev libffi-dev uuid-dev libcap-dev libpcre3-dev \
  python3-pip python3.6 python3.6-dev -y
```

### Install tesseract
```
sudo add-apt-repository ppa:alex-p/tesseract-ocr
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-rus
```

### Install pipenv
```
sudo pip3 install pipenv
```

### Initialize virtualenv
```
pipenv shell --python 3.6
```

### Install python requirements
```
pipenv install
```

### Install Java
```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install default-jdk -y
java -version
```

### Download Selenium Standalone Server
https://www.seleniumhq.org/download/

### Run Selenium Standalone Server
```
java -jar selenium-server-standalone-*.jar
```

### Selenium Python Docs
https://selenium-python.readthedocs.io


### Install requirements for pyvirtualdisplay
```
sudo apt-get install xvfb -y
```

### Install Chrome Binary
```
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt-get update
sudo apt-get install google-chrome-stable
```

### Install Drivers
PhantomJS (Deprecated)
http://phantomjs.org/download.html

Others
https://selenium-python.readthedocs.io/installation.html#downloading-python-bindings-for-selenium

### Selenium Grid
http://automation-remarks.com/nastraivaiem-selenium-grid-za-5-minut/

### PostgreSQL Installation
```
sudo apt-get install postgresql-9.6
```

### PostgreSQL Database
# https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e
```
sudo su - postgres
createuser cantonfair
createdb cantonfair
psql
alter user cantonfair with encrypted password 'cantonfair';
grant all privileges on database cantonfair to cantonfair ;
\q
```
