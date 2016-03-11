## Prerequisites
+ [Oracle VirtualBox](https://www.virtualbox.org/wiki/Downloads)
+ [Vagrant](https://www.vagrantup.com/downloads.html)
* [(optional) Update VirtualBox Guest Additions](https://github.com/dotless-de/vagrant-vbguest)
  * `vagrant plugin install vagrant-vbguest`


## Installation
*Windows Users should perform the following steps using the Git Shell*

```shell
touch .env
```

Open `.env` in your favorite text editor and create entries for :

+ `POSTGRES_USER` = _someuser_
+ `POSTGRES_PASSWORD` = _somepassword_

## Execution
```shell
vagrant up
start http://localhost:8080/
```

You should be able to modify files in the `./tuesday/www/app` directory and 
see the changes when refreshing the browser
