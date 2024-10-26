Homework for https://education.borshev.com/architecture

cd final_project
kafka, schema-regestry - docker-compose up -d

Cервис аутентификации:

- cd auth 
- база в докере: docker-compose up -d 
- poetry install 
- ENV_FILE=settings/.env poetry run python main.py

Cервис тасков:
- cd ../task_manager 
- база в докере: docker-compose up -d 
- poetry install 
- ENV_FILE=settings/.env poetry run python main.py 
- консьюмер: poetry run python consumer.py