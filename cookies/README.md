# Cookie & Database løsning

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
