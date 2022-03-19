# Cookie & Database Solution

There are two approaches to implementing the cookie and database on a webserver.
One way is to copy the contents of *public* to the webservers public directory i.e. /var/www/html/.
This requires the php-engine i.e., apache2 to have the extension *mysqli*, and the database and tables created in mysql with *db.sql*.
The config file *config/database.php* should be edited with the username and password of a user that has full privileges to the database.
Furthermore, the directory *config* should be copied to the parent directory of the webservers public folder i.e. /var/www/config.

Alternatively, the cookie and database can be implemented as an 'external' solution with Docker.
This requires *Docker Engine* and *Docker Compose*: [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), [Docker compose](https://docs.docker.com/compose/install/).
With Docker a php-server and a mysql-server runs in softwarecontainers, a kind of lightweight modular virtual machine.
Before the containers can be initatiated the directory *secrets* should be created, with a file *db_pass* that contains the wanted password for a mysql user *recommender*.
This password will automatically be added both in the php container and the mysql container.
To initate the containers use the shell command `docker-compose up -d` in the directory containing *docker-compose.yml*.

Default settings is that the php container is exposed through port 80 (standard http) and the mysql container is exposed on port 3306 (standard db port).

# Cookie & Databse løsning

Cookie'en og databasen kan implementeres på en server på to måder. 
Enten kan mappen *public* lægges i webserverens rodmappe f.eks. /var/www/html/ og /js/cookie.js integreres i hver .html fil.
Samtidig kræver det at php-enginen f.eks. apache2 har extensionen *mysqli*, og at databasen sættes op i mysql med *db.sql*.
Config filen database.php i config mappen  skal desuden tilrettes med username og password, til en bruger der har skrive rettigheder til databasen.
Og config mappen skal lægges et niveau oppe fra websereverens rodmappe f.eks. /var/www/config

Alternativt kan cookie'en og databasen implementeres som en "ekstern" løsning vha. docker.
Dette kræver *Docker Engine* og *Docker compose*: [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), [Docker compose](https://docs.docker.com/compose/install/).
Med Docker kan php og mysql databasen køres i softwarecontainere, som bedst kan beskrives som letvægts modulære virtuelle maskiner.
Før containerne sættes op skal der oprettes en mappe /secrets i roden af cookies, hvori filen db_pass oprettes, med passwordet til mysql brugeren recommender.
Dette password bliver så automatisk tilføjet både i php containeren og database containeren.
Dernæst kan containerene startes op vha. kommandoen `docker-compose up -d` i samme mappe som docker-compose.yml filen. 

Standard instillingerne er at php containeren starter på port 80 (standard http) og mysql containeren starter på port 3306 (standard database).
Containerne kan også load-balances videredirigeres til fra subdomæner vha. en reverse proxy f.eks. Nginx.
Hvis der i forvejen kører en reverse proxy i en docker container på serveren, skal det sikres at reverse proxy'en og de nye containere kan "snakke sammen".
Docker compose laver standard et nyt netværk, som reverse proxyen ikke nødvendigvis har adgang til. Dette kan evt. fixes ved at åbne et nyt docker netværk og tilføje reverse proxy'en,
samt tilføje netværket til containerne i docker-compose.yml filen.
