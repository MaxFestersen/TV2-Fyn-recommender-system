# Prerequisites

Tools needed for working environment:

- AWS CLI [install](https://aws.amazon.com/cli/)
- Docker Compose CLI 19.03 or later [install](https://docs.docker.com/cloud/ecs-integration/)


Setup:

- AWS CLI configuration [read more](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- Docker AWS ECS context [read more](https://docs.docker.com/cloud/ecs-integration/)
- Create AWS secret with dockerhub access token

```javascript
{
  "username":"DockerHubUserName",
  "password":"DockerHubAccessToken"
}
```
```$ docker secret create dockerhubAccessToken token.js```

- Setup AWS RDS MySQL database
- Create AWS secret with database info (done in docker-compose.ecs.yml)
  - Create directory with .env containing database info `secrets/.env`

Run:

```$ docker compose -f docker-compose.ecs.yml up```
- Automatically sets up loadbalancer, vpc and security group allowing access on port 80
- Adds secret with database info (remember to create a directory with .env)
- Add A record to point domain to loadbalancer from route53
- Create AWS ACM certificate to enable SSL Termination
- Edit security group to allow access on port 443
- Edit Loadbalancer listeners so http redirects to https and https points to target group

