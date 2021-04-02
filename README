# update-route53

## Installation

* Install Python/PiP
```
$ sudo apt install python3-pip
```

* Install boto3
``` 
$ pip3 install boto3
```

## Setup
* Add security credentials to `~/.aws/credentials`
```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

* Configure region file `~/.aws/config`
```
[default]
region=us-east-1
```

## Cron job
Check every 4 hours if the IP address changed.

```
$ crontab -e
```

```
0 */4 * * * /path/to/update-route53.py
```