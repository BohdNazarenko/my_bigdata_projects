# Object storage
В папку object_storage[]() каждый ***локально*** самостоятельно кладёт:
- `.env` — реальные ключи S3 (никогда не коммитим!).


- папку `new_csv_files` в object_storage/s3_files_handler чтобы туда попадали новые файлы

## Пример .env

AWS_ACCESS_KEY_ID=<ваш ключ>

AWS_SECRET_ACCESS_KEY=<ваш секрет>

AWS_REGION=eu-central-1     

BUCKET_NAME=de--practice



**Задание №1**

* модуль [aws_controller.py](aws_controller.py)

метод list_files() - возвращает список объектов в бакете!

метод file_exists() - возвращает булевый ответ на запрос о наличии файла с определенным именем!


**Задание №2**

2.1 Доступ на чтение + запрет записи кроме админа(меня).

S3 → Buckets -> name our bucket -> Permissions -> Bucket policy -> Edit -> copy json with user data 
(YOUR-BUCKET-NAME, YOUR-ACCOUNT-ID) -> Save changes.

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadObjects",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    },
    {
      "Sid": "OwnerWriteOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*",
      "Condition": {
        "StringNotLike": {
          "aws:userid": "YOUR-ACCOUNT-ID:*"      
        }
      }
    }
  ]
}

**2.2 Версионирование**

S3 → Buckets -> name our bucket -> Properties -> Bucket versioning → Edit → Enable → Save changes
upload file to bucket by python and download last version on UI


**3.3 lifecycle policy** -> delete in 3 days

S3 → Buckets -> name our bucket -> 	Management → Lifecycle rules → Create lifecycle rule -> 

• Lifecycle rule configuration
-> Rule name: (name what policy do)
->  Limit the scope of this rule using one or more filters 
-> Prefix(where delete) 

• Lifecycle rule actions
-> Expire current versions of objects
-> Permanently delete noncurrent versions of objects) 
• Expire current versions of objects
-> Current versions → Expire current versions … after = 3 days.
-> Previous versions → Permanently delete … after = 3 days.

Next → Save rule.

3. file s3_files_handler

FOLDERS: 

• [new_csv_files](s3_files_handler/new_csv_files) -> для новых csv которые отслеживает watchfiles

• [tmp](s3_files_handler/tmp) -> для хранения файлов csv с фильтрацией

• [archive](s3_files_handler/archive) -> куда перемещаются новые файлы, их архив

MODULES:

[s3_client.log](s3_files_handler/s3_client.log) -> для логирования всех действий

[s3_csv_handler.py](s3_files_handler/s3_csv_handler.py) -> реализация