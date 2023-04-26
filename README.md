# lr4
Написать сервис авторизации (auth) для сервиса погоды (weather).

Сервис auth хранит в себе хэштаблицу с известными именами пользователей. В качестве запроса принимается имя пользователя, в ответе содержится булевый результат - true/false.
Перед определением погоды weather проверяет авторизацию пользователя через auth. Если в ответе пришел false, то weather должен вернуть HTTP ошибку с кодом 403.
Имя пользователя передается в weather через HTTP заголовок Own-Auth-UserName. Сервисы auth и weather взаимодействуют по gRPC. Сервис auth написан отличном от weather языке программирования.